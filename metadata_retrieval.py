import re
import json
import time
from googleapiclient.discovery import build
import requests

def get_dislike_count(video_id):
    """Fetch dislike count from the Return YouTube Dislike API."""
    url = f"https://returnyoutubedislikeapi.com/v1/videos/{video_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("dislikes", 0)  # Return 0 if dislikes not found
    else:
        print(f"Failed to fetch dislikes for {video_id}")
        return None

# YouTube Data API setup
API_KEY = "AIzaSyAUW5nTFXGT6r4iMql_aXgojbNITD3ciBE"  # Replace with your API key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Initialize YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def extract_video_ids(file_path):
    """Extracts YouTube video IDs from a text file."""
    with open(file_path, "r") as file:
        links = file.readlines()
    video_ids = [
        re.search(r"v=([\w-]{11})", link).group(1) if "v=" in link else link.strip()[-11:]
        for link in links if link.strip()
    ]
    return video_ids

def fetch_video_metadata(video_ids):
    """Fetch metadata for a list of video IDs using YouTube Data API."""
    metadata = {}
    requests_made = 0  # To track the number of requests made in a session

    for i in range(0, len(video_ids), 50):  # YouTube API supports up to 50 IDs per request
        batch_ids = video_ids[i:i+50]
        request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch_ids)
        )
        response = request.execute()
        requests_made += 1  # Increment the request count

        for item in response.get("items", []):
            video_id = item["id"]
            snippet = item["snippet"]
            stats = item["statistics"]
            dislikes = get_dislike_count(video_id)
            metadata[video_id] = {
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "publishedAt": snippet.get("publishedAt"),
                "likes": int(stats.get("likeCount", 0)),
                "dislikes": dislikes if dislikes is not None else 0,  # Deprecated by YouTube
                "views": int(stats.get("viewCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
            }
        
        # Check if we are nearing the rate limit
        if requests_made % 90 == 0:
            print("Rate limit reached. Pausing for a minute...")
            time.sleep(60)  # Pause for 1 minute

    return metadata

# Main execution
if __name__ == "__main__":
    # Path to the text file containing YouTube links
    file_path = "links.txt"
    
    # Extract video IDs
    video_ids = extract_video_ids(file_path)
    
    # Fetch metadata
    video_metadata = fetch_video_metadata(video_ids)
    
    # Save to a JSON file
    with open("video_metadata_dislikes.json", "w") as json_file:
        json.dump(video_metadata, json_file, indent=4)
    
    print("Video metadata saved to video_metadata_dislikes.json.")
