import os
import yt_dlp
import json
import boto3
import re
import requests
from botocore.exceptions import NoCredentialsError, ClientError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import isodate  # For parsing ISO 8601 duration

# Load environment variables from .env file
load_dotenv()

# Environment variables for sensitive data
API_KEY = os.getenv("YOUTUBE_API_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")
AWS_S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
API_BASE_URL = "https://videa-backend.uscentral1-0.vint.vidcast.io"


def upload_to_s3(file_path, bucket, s3_key):
    """Uploads a file to an AWS S3 bucket and returns the S3 URI."""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_S3_ACCESS_KEY,
        aws_secret_access_key=AWS_S3_SECRET,
        region_name=AWS_S3_REGION
    )
    try:
        print(f"Uploading {file_path} to s3://{bucket}/{s3_key}")
        s3_client.upload_file(file_path, bucket, s3_key)

        # Return the S3 URI for API use
        s3_uri = f"s3://{bucket}/{s3_key}"
        print(f"Upload successful: {s3_uri}")
        return s3_uri  # Changed to return the s3:// format
    except NoCredentialsError:
        print("AWS credentials not available.")
        raise
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")
        raise

def parse_iso8601_duration(iso_duration):
    """Parses an ISO 8601 duration string to total seconds."""
    duration = isodate.parse_duration(iso_duration)
    return int(duration.total_seconds())

def fetch_video_metadata(video_url):
    """Fetches metadata for a YouTube video."""
    video_id = video_url.split("v=")[-1]
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id)
    response = request.execute()

    if not response["items"]:
        raise ValueError("No video found for the provided URL.")

    video_data = response["items"][0]
    duration = video_data["contentDetails"]["duration"]
    duration_seconds = parse_iso8601_duration(duration)

    metadata = {
        "title": video_data["snippet"]["title"],
        "description": video_data["snippet"]["description"],
        "channel": video_data["snippet"]["channelTitle"],
        "published_at": video_data["snippet"]["publishedAt"],
        "tags": video_data["snippet"].get("tags", []),
        "thumbnail_url": video_data["snippet"]["thumbnails"]["high"]["url"],
        "duration_seconds": duration_seconds  # Add parsed duration in seconds
    }
    return metadata

def download_thumbnail(thumbnail_url, save_path):
    """Downloads the video thumbnail and saves it locally."""
    response = requests.get(thumbnail_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Thumbnail downloaded to: {save_path}")
    else:
        raise Exception(f"Failed to download thumbnail: {response.status_code}")

def sanitize_title(title):
    """Sanitizes a video title to create an S3-safe folder name."""
    sanitized_title = re.sub(r'[^a-zA-Z0-9_\-]', '', title.replace(" ", "_"))
    return sanitized_title

def download_youtube_video(video_url, download_path="downloads"):
    """Downloads a YouTube video using yt-dlp."""
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'best',
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading video: {video_url}")
        info_dict = ydl.extract_info(video_url, download=True)
        video_filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp4')  # Convert filename
        return video_filename  # Return the video file path

def get_or_create_user(email):
    """Calls the getOrCreateUser API."""
    url = f"{API_BASE_URL}/v1/users/user"
    payload = {"email": email}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        user_data = response.json()
        return user_data["id"]
    elif response.status_code == 403:
        raise Exception("User not found and could not be created.")
    else:
        response.raise_for_status()

def create_video(name, description, camera_asset_uri, camera_thumbnail_asset_uri, duration, tags, user_id):
    """Calls the importVideo API."""
    url = f"{API_BASE_URL}/v1/videos/import"
    payload = {
        "name": name,
        "description": description,
        "camera_asset_uri": camera_asset_uri,  # Ensure this is in "s3://" format
        "camera_thumbnail_asset_uri": camera_thumbnail_asset_uri,  # Ensure this is in "s3://" format
        "duration": duration * 1000,  # Convert duration to milliseconds
        "tags": tags,
        "user_id": user_id  # Use 'user_id' instead of 'userID'
    }

    response = requests.post(url, json=payload)

    # Print the payload for debugging
    print("Payload being sent to the API:")
    print(json.dumps(payload, indent=4))

    if response.status_code == 200:
        video_data = response.json()
        return video_data
    else:
        response.raise_for_status()

if __name__ == "__main__":
    video_url = input("Enter the URL of the YouTube video: ")
    user_email = input("Enter the user's email address: ")

    try:
        # Fetch metadata
        metadata = fetch_video_metadata(video_url)
        print(f"Fetched Metadata: {metadata}")

        # Sanitize the title for S3 folder name
        sanitized_title = sanitize_title(metadata['title'])

        # Save metadata to a JSON file
        metadata_filename = os.path.join("downloads", f"{sanitized_title}_metadata.json")
        with open(metadata_filename, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4, ensure_ascii=False)

        # Download the video and thumbnail
        video_file_path = download_youtube_video(video_url)
        thumbnail_filename = os.path.join("downloads", f"{sanitized_title}_thumbnail.jpg")
        download_thumbnail(metadata["thumbnail_url"], thumbnail_filename)

        # Upload files to S3 (using s3:// URIs)
        metadata_s3_uri = upload_to_s3(metadata_filename, AWS_S3_BUCKET, f"{sanitized_title}/metadata.json")
        thumbnail_s3_uri = upload_to_s3(thumbnail_filename, AWS_S3_BUCKET, f"{sanitized_title}/thumbnail.jpg")
        video_s3_uri = upload_to_s3(video_file_path, AWS_S3_BUCKET, f"{sanitized_title}/video.mp4")

        # Get or create user
        user_id = get_or_create_user(user_email)

        # Create video in the API
        video_data = create_video(
            name=metadata["title"],
            description=metadata["description"],
            camera_asset_uri=video_s3_uri,  # Correct format
            camera_thumbnail_asset_uri=thumbnail_s3_uri,  # Correct format
            duration=metadata["duration_seconds"],  # Use actual duration
            tags=metadata["tags"],
            user_id=user_id
        )
        print(f"Video created successfully: {video_data}")

    except Exception as e:
        print(f"An error occurred: {e}")
