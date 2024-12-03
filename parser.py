import ast
import json
import multiprocessing
import os
import sys

def process_chunk(chunk):
    """
    Process a chunk of text and extract concatenated transcripts
    Uses eval for speed, not safety
    """
    result = {}
    current_buffer = chunk
    
    while True:
        try:
            # Attempt to parse the current buffer
            entry, index = ast.literal_eval(current_buffer), len(current_buffer)
            
            # Process the parsed entry
            for key, transcript_list in entry.items():
                if key not in result:
                    result[key] = ""
                result[key] += " ".join(item['text'] for item in transcript_list)
            
            # Clear the processed part of the buffer
            current_buffer = current_buffer[index:].lstrip()
        
        except (SyntaxError, ValueError):
            # Not enough data in buffer; break the processing
            break
    
    return result

def chunk_file(filename, chunk_size=1024*1024):
    """
    Split file into chunks for parallel processing
    """
    file_size = os.path.getsize(filename)
    chunks = []
    
    with open(filename, 'r') as fp:
        while True:
            chunk = fp.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    
    return chunks, file_size

def parse_and_concatenate_parallel(filename, num_processors=8):
    """
    Parallelize text parsing across multiple processors
    """
    # Split file into chunks
    chunks, file_size = chunk_file(filename)
    
    # Use all available processors, but no more than 8
    num_processors = min(num_processors, multiprocessing.cpu_count())
    
    # Create a pool of workers
    with multiprocessing.Pool(processes=num_processors) as pool:
        # Track progress manually
        print(f"Processing file with {num_processors} processors...")
        processed_size = 0
        
        # Process chunks in parallel
        results = []
        for i, chunk_result in enumerate(pool.imap(process_chunk, chunks), 1):
            results.append(chunk_result)
            
            # Manual progress tracking
            processed_size += len(chunks[i-1])
            progress = min(100, int(processed_size / file_size * 100))
            sys.stdout.write(f"\rProgress: [{progress}%] {'#' * (progress // 5)}{' ' * (20 - progress // 5)}")
            sys.stdout.flush()
        
        print("\nProcessing complete!")
    
    # Merge results from all chunks
    final_result = {}
    for chunk_result in results:
        for key, text in chunk_result.items():
            if key in final_result:
                final_result[key] += " " + text
            else:
                final_result[key] = text
    
    return final_result

def main():
    filename = "transcripts.json"  # Replace with your filename
    output_filename = "concatenated_transcripts.json"
    
    # Process the file
    concatenated_data = parse_and_concatenate_parallel(filename)
    
    # Save results
    with open(output_filename, "w") as out_fp:
        json.dump(concatenated_data, out_fp, indent=2)
    
    # Print a sample of results
    print("\nSample Output:")
    for id_, text in list(concatenated_data.items())[:5]:
        print(f"ID: {id_}\nText: {text[:100]}...\n")

if __name__ == "__main__":
    main()