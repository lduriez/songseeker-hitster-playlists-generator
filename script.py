import pandas as pd
import requests
import time
import hashlib
import os

csv_file_path = '/tmp/file.csv'
cache_file_path = '/tmp/youtube_cache.csv'

api_key = os.getenv('YOUTUBE_API_KEY')

if not api_key:
    raise ValueError("The YouTube API key is not set. Please set the YOUTUBE_API_KEY environment variable.")

# Load the CSV file
data = pd.read_csv(csv_file_path)

# Load or create the cache
if os.path.exists(cache_file_path):
    cache = pd.read_csv(cache_file_path)
else:
    cache = pd.DataFrame(columns=['Artist', 'Title', 'URL', 'Youtube-Title', 'Hashed Info'])

def get_youtube_url(artist, title):
    # Check the cache first
    cached_result = cache[(cache['Artist'] == artist) & (cache['Title'] == title)]
    if not cached_result.empty:
        return cached_result.iloc[0]['URL'], cached_result.iloc[0]['Youtube-Title']

    search_url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': f'{artist} {title} official music video',  # Add filters for more precise results
        'key': api_key,
        'type': 'video',
        'maxResults': 1
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        results = response.json().get('items', [])

        if results:
            video_id = results[0]['id']['videoId']
            video_title = results[0]['snippet']['title']
            url = f'https://www.youtube.com/watch?v={video_id}'
            # Update the cache
            cache.loc[len(cache)] = [artist, title, url, video_title]
            return url, video_title
    except requests.exceptions.RequestException as e:
        print(f"Error requesting {artist} - {title}: {e}")
    return None, None

def get_youtube_info(video_url):
    oembed_url = f"https://www.youtube.com/oembed?url={video_url}"
    try:
        response = requests.get(oembed_url)
        response.raise_for_status()
        data = response.json()
        title = data['title']
        author_name = data['author_name']
        important_info = title + author_name
        hashed_info = hashlib.sha256(important_info.encode()).hexdigest()
        return title, hashed_info
    except requests.exceptions.RequestException as e:
        print(f"Error requesting {video_url}: {e}")
        return None, None

# Add URL, Youtube-Title, and Hashed Info columns if they do not exist
if 'URL' not in data.columns:
    data['URL'] = ''
if 'Youtube-Title' not in data.columns:
    data['Youtube-Title'] = ''
if 'Hashed Info' not in data.columns:
    data['Hashed Info'] = ''

# Ensure columns are of the correct type
data['URL'] = data['URL'].astype(str)
data['Youtube-Title'] = data['Youtube-Title'].astype(str)
data['Hashed Info'] = data['Hashed Info'].astype(str)

for index, row in data.iterrows():
    if pd.notnull(row['URL']) and row['URL'] != '':
        # If the URL is already present, use the URL to get the information
        youtube_title, hashed_info = get_youtube_info(row['URL'])
        if youtube_title:
            data.at[index, 'Youtube-Title'] = youtube_title
        if hashed_info:
            data.at[index, 'Hashed Info'] = hashed_info
    else:
        # If the URL is not present, use the YouTube API to get the URL and information
        url, youtube_title, hashed_info = get_youtube_url(row['Artist'], row['Title'])
        if url:
            data.at[index, 'URL'] = url
        if youtube_title:
            data.at[index, 'Youtube-Title'] = youtube_title
        if hashed_info:
            data.at[index, 'Hashed Info'] = hashed_info

        # Add a delay to avoid exceeding the per-minute request limits
        time.sleep(1)

# Save the updated CSV file
data.to_csv('/tmp/file-Updated.csv', index=False)

# Save the cache
cache.to_csv(cache_file_path, index=False)

print("CSV file successfully updated!")
