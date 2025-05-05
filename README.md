# YouTube Video Downloader & S3 Uploader

This project provides scripts for downloading YouTube videos and their metadata, storing them locally, and uploading the assets (video, thumbnail, and metadata) to an AWS S3 bucket. It also integrates with a remote video API to register imported videos for a user.

## Features

- Download YouTube videos using `yt-dlp`
- Fetch video metadata via the YouTube Data API
- Parse ISO 8601 duration to seconds
- Download video thumbnails
- Upload files to AWS S3
- Register user and imported video via external API

## Prerequisites

- Python 3.7+
- AWS account with an S3 bucket
- YouTube Data API key
- `.env` file with credentials

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
