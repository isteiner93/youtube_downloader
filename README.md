# YouTube Video Downloader & S3 Uploader

This project provides Python scripts to:

- Download a YouTube video and its thumbnail.
- Fetch and save video metadata.
- Upload video, thumbnail, and metadata to AWS S3.
- (Optional) Register the video and user via an external video API.

## Features

- Download YouTube videos using `yt-dlp`.
- Fetch video metadata using the YouTube Data API.
- Convert ISO 8601 durations to seconds.
- Upload assets to AWS S3.
- Register users and videos using external HTTP API calls.

## Requirements

- Python 3.7+
- AWS account and S3 bucket
- YouTube Data API key
- `.env` file with secrets

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Install dependencies

bash
Copy Code
pip install -r requirements.txt

3. Create a .env file

Add the following to a new .env file:


ini
Copy Code
YOUTUBE_API_KEY=your_youtube_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_S3_BUCKET=your_bucket_name
AWS_S3_REGION=your_bucket_region

Scripts

1. Basic Script

Run:


bash
Copy Code
python script_basic.py

Functionality:


Prompts for YouTube video URL.
Downloads video and highest resolution thumbnail.
Fetches video metadata.
Saves everything locally.
Uploads to AWS S3 in structured folders.

2. Extended Script (with API Integration)

Run:


bash
Copy Code
python script_api_extended.py

Additional functionality:


Prompts for video URL and user email.
Registers the user via /v1/users/user.
Uploads video, metadata, and thumbnail to S3.
Registers video via /v1/videos/import.

S3 Upload Structure

Example:


Copy Code
s3://your-bucket/my-sanitized-video-title/
├── my-sanitized-video-title_metadata.json
├── my-sanitized-video-title_thumbnail.jpg
└── my-original-video.mp4

Environment Variables

Stored in .env:


YOUTUBE_API_KEY – YouTube Data API v3 key
AWS_ACCESS_KEY_ID – AWS IAM access key
AWS_SECRET_ACCESS_KEY – AWS IAM secret
AWS_S3_BUCKET – Target S3 bucket name
AWS_S3_REGION – AWS region for S3

Requirements File

requirements.txt:


Copy Code
yt-dlp
boto3
requests
google-api-python-client
python-dotenv
isodate

Install with:


bash
Copy Code
pip install -r requirements.txt

Notes

Make sure AWS credentials are authorized for s3:PutObject.
The video folder name is a sanitized version of the title (no special characters).
Thumbnail is selected from the highest available resolution.
Video metadata is saved in JSON format.

License

This project is licensed under the MIT License.
```


My answers are currently limited to public internet data. To get Cisco-specific information about this topic, please start a new chat and select Cisco-data as your data source.
