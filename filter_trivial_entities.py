from collections import defaultdict
import json
# import data from json file
with open('data.json') as f:
    data = json.load(f)

# Define stopwords and confidence threshold
stopwords = {"you", "I", "i", "he", "she", "they", "we", "it", "guy", "world", "joe", "joe rogan"}  # Add more stopwords as needed
confidence_threshold = 0.8  # Example threshold

# Step 3: Create a dictionary to map episode IDs to lists of entities
episode_entities = defaultdict(list)  # Structure: {id: [entity_list]}

# Iterate over the data to populate episode_entities
for episode_id, entities in data.items():
    filtered_entities = []
    for entity in entities:
        # Filter entities based on stopwords and confidence threshold
        if (
            entity["text"].lower() not in stopwords
            and entity["score"] >= confidence_threshold
        ):
            normalized_text = entity["text"].strip().lower()  # Normalize capitalization
            filtered_entities.append(normalized_text)
            # filtered_entities turned into sets and then back into lists to remove duplicates
            filtered_entities = list(set(filtered_entities))
    episode_entities[episode_id] = filtered_entities

with open('episode_entities.json', 'w') as f:
    json.dump(episode_entities, f)
# Example: Printing the resulting dictionary
# efficiently find the longest list of entities
max_length = max(len(entities) for entities in episode_entities.values())
print(max_length)
#for episode_id, entities in episode_entities.items():
    #print(f"Episode ID: {episode_id}, Entities: {entities}")
    
