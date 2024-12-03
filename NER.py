import json
from gliner import GLiNER
from nltk.tokenize import word_tokenize
from tqdm import tqdm
import torch

def create_new_dict(data):
    new_dict = {}
    for key in data:
        if data[key] is not None:
            new_dict[key] = data[key]
    return new_dict

def extract_named_entities(input_file, output_file):
    """
    Extracts named entities from the text of each ID in a dictionary.

    Args:
        input_file (str): Path to the JSON file containing the dictionary with IDs and their text.
        output_file (str): Path to save the output JSON file with IDs and their named entities.
    """
    # Load the input data
    with open(input_file, 'r') as infile:
        data = json.load(infile)

    # Remove None values from the dictionary
    data = create_new_dict(data)

    # Initialize GLiNER with the base model
    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

   
    model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
     # Move the model to GPU if available
    model.to(device)

    
    # Labels for entity prediction
    # Most GLiNER models should work best when entity types are in lower case or title case
    labels = ["Person", "Location", "Organization"]

    # Perform entity prediction
    named_entities_by_id = {}
    for id, text in tqdm(data.items(), desc="Extracting named entities"):
        # split the text into sentences of 384 tokens
        # this is to avoid the "input too long" error
        tokens = word_tokenize(text)
        #split the tokens list into pieces of 384 tokens
        tokens = [tokens[i:i + 300] for i in range(0, len(tokens), 300)]
        #predict the entities for each piece of tokens
        entities = []
        for piece in tokens:
            entities += model.predict_entities(" ".join(piece), labels, threshold=0.5)

        named_entities_by_id[id] = entities
    
    # Save the results to the output file
    with open(output_file, 'w') as outfile:
        json.dump(named_entities_by_id, outfile)

    print(f"Named entities have been saved to: {output_file}")

# Example usage
input_file = "dictionary.json"  # Replace with your actual input file path
output_file = "named_entities_by_id.json"
extract_named_entities(input_file, output_file)
