# YouTube Video Downloader and Metadata Uploader

This project provides a script for downloading a YouTube video, extracting metadata, and uploading the video, thumbnail, and metadata to AWS S3. Additionally, it integrates with a video management API to create a new video entry with the uploaded content.

## Features

- Download YouTube video using [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Extract metadata (title, description, tags, etc.) from YouTube video using the YouTube API
- Download video thumbnail
- Upload video, metadata, and thumbnail to AWS S3
- Create a new video entry via a custom API

## Prerequisites

Before running this script, you need to set up the following:

- **Python 3.6+**
- **AWS Account** with S3 access
- **Google API Key** for YouTube API access
- **.env file** for sensitive configuration values

### Required Libraries

To install the required Python libraries, run:

bash
pip install -r requirements.txt

### Configuration
Create a .env file in the root directory of the project with the following environment variables:

YOUTUBE_API_KEY=your_youtube_api_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_S3_REGION=your_s3_region
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
Functions
upload_to_s3(file_path, bucket, s3_key)
Uploads a file to an AWS S3 bucket and returns the S3 URI.

parse_iso8601_duration(iso_duration)
Parses an ISO 8601 duration string to total seconds.

fetch_video_metadata(video_url)
Fetches metadata for a YouTube video, including title, description, tags, and duration.

download_thumbnail(thumbnail_url, save_path)
Downloads the video thumbnail and saves it locally.

sanitize_title(title)
Sanitizes a video title to create an S3-safe folder name.

download_youtube_video(video_url, download_path="downloads")
Downloads a YouTube video using yt-dlp and returns the local file path.

get_or_create_user(email)
Calls the getOrCreateUser API to fetch or create a user based on their email.

create_video(name, description, camera_asset_uri, camera_thumbnail_asset_uri, duration, tags, user_id)
Calls the importVideo API to create a new video entry in the video management system.

###Usage
Ensure all dependencies are installed and environment variables are set.

Run the script:

python script_name.py
Follow the prompts to enter the YouTube video URL and the user email.

The script will:

Fetch the metadata from the YouTube video.

Download the video and thumbnail.

Upload the video, metadata, and thumbnail to AWS S3.

Create a video entry in the video management API.

#Example

Enter the URL of the YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Enter the user's email address: user@example.com
