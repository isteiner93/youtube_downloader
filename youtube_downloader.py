import os
import yt_dlp
import json
import boto3
import re
import requests
from botocore.exceptions import NoCredentialsError, ClientError
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables for sensitive data
API_KEY = os.getenv("YOUTUBE_API_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")
AWS_S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

def upload_to_s3(file_path, bucket, s3_key):
    """Uploads a file to an AWS S3 bucket."""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_S3_ACCESS_KEY,
        aws_secret_access_key=AWS_S3_SECRET,
        region_name=AWS_S3_REGION
    )
    try:
        print(f"Uploading {file_path} to s3://{bucket}/{s3_key}")
        s3_client.upload_file(file_path, bucket, s3_key)
        print(f"Upload successful: s3://{bucket}/{s3_key}")
    except NoCredentialsError:
        print("AWS credentials not available.")
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")

def fetch_video_metadata(video_url):
    """Fetches metadata for a YouTube video."""
    video_id = video_url.split("v=")[-1]
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()

    if not response["items"]:
        raise ValueError("No video found for the provided URL.")

    video_data = response["items"][0]
    metadata = {
        "title": video_data["snippet"]["title"],
        "description": video_data["snippet"]["description"],
        "channel": video_data["snippet"]["channelTitle"],
        "published_at": video_data["snippet"]["publishedAt"],
        "tags": video_data["snippet"].get("tags", []),
        "view_count": video_data["statistics"].get("viewCount", 0),
        "like_count": video_data["statistics"].get("likeCount", 0),
        "comment_count": video_data["statistics"].get("commentCount", 0),
        "thumbnail_url": video_data["snippet"]["thumbnails"]["high"]["url"]  # High-quality thumbnail
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

if __name__ == "__main__":
    video_url = input("Enter the URL of the YouTube video: ")

    try:
        # Fetch metadata
        metadata = fetch_video_metadata(video_url)
        print(f"Fetched Metadata: {metadata}")

        # Sanitize the title for S3 folder name
        sanitized_title = sanitize_title(metadata['title'])
        print(f"Sanitized folder name: {sanitized_title}")

        # Ensure downloads folder exists
        download_path = "downloads"
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Save metadata to a JSON file
        metadata_filename = os.path.join(download_path, f"{sanitized_title}_metadata.json")
        with open(metadata_filename, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4, ensure_ascii=False)
        print(f"Metadata saved to: {metadata_filename}")

        # Download the video thumbnail
        thumbnail_filename = os.path.join(download_path, f"{sanitized_title}_thumbnail.jpg")
        download_thumbnail(metadata["thumbnail_url"], thumbnail_filename)

        # Download the video
        video_file_path = download_youtube_video(video_url)
        print(f"Video downloaded to: {video_file_path}")

        # Upload metadata, video, and thumbnail to S3 under the sanitized folder
        metadata_s3_key = f"{sanitized_title}/{os.path.basename(metadata_filename)}"
        thumbnail_s3_key = f"{sanitized_title}/{os.path.basename(thumbnail_filename)}"
        video_s3_key = f"{sanitized_title}/{os.path.basename(video_file_path)}"

        upload_to_s3(metadata_filename, AWS_S3_BUCKET, metadata_s3_key)
        upload_to_s3(thumbnail_filename, AWS_S3_BUCKET, thumbnail_s3_key)
        upload_to_s3(video_file_path, AWS_S3_BUCKET, video_s3_key)

    except Exception as e:
        print(f"An error occurred: {e}")
