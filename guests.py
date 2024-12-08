import re
import json

def extract_guests(title):
    """
    Extract guest names from the video title.
    Guests are listed after '-' or 'with', and names are separated by ',', '&', or 'and'.
    Handles cases like 'Derek, More Plates More Dates' as single entities.
    """
    # Look for "with" or "-" followed by names
    match = re.search(r"(?:with|-\s)(.+)", title, re.IGNORECASE)
    if match:
        guests_raw = match.group(1).strip()
        
        # Check if the entire string seems like a single entity
        if "," in guests_raw and not re.search(r"[, &]|\sand\s", guests_raw):
            return [guests_raw.strip()]  # Treat as a single entity
        
        # Split names using common separators (',', '&', 'and') while preserving single entities
        guests = re.split(r",|&| and ", guests_raw)
        # Trim and filter
        return [guest.strip() for guest in guests if guest.strip()]
    
    return []

# Example metadata dictionary
with open("video_metadata.json", "r") as json_file:
    metadata = json.load(json_file)

# Process each video's metadata and add the "guests" field
for video_id, video_data in metadata.items():
    title = video_data.get("title", "")
    guests = extract_guests(title)
    video_data["guests"] = guests

# Save the updated metadata to a JSON file
with open("video_metadata_with_guests.json", "w") as json_file:
    json.dump(metadata, json_file, indent=4)

# Output the updated metadata for verification
print(json.dumps(metadata, indent=4))
