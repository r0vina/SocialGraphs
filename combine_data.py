import json

class DataCombiner:
    def __init__(self, metadata_file, nebi_file, transcripts_file):
        self.metadata_file = metadata_file
        self.nebi_file = nebi_file
        self.transcripts_file = transcripts_file

    def combine_data(self):
        # Load the metadata file
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)

        # Load the nebi file
        with open(self.nebi_file, 'r') as f:
            nebi = json.load(f)

        # Load the transcripts file
        with open(self.transcripts_file, 'r') as f:
            transcripts = json.load(f)

        # Combine the data for each id/key
        combined_data = {}
        for id in metadata:
            if id in transcripts and transcripts[id] is not None:
                combined_data[id] = {
                    'metadata': metadata[id],
                    'nebi': nebi[id] if id in nebi else [],
                    'transcript': transcripts[id]
                }

        return combined_data

# Usage example
combiner = DataCombiner('video_metadata_with_guests.json', 'episode_entities.json', 'dictionary.json')
combined_data = combiner.combine_data()

# Save the combined data to a file
with open('final_data.json', 'w') as f:
    json.dump(combined_data, f)