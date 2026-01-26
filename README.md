# Piewallah Video API

A FastAPI-based service to fetch video content and DRM keys from studyweb.live for the Piewallah video application.

## Features

- Fetch video URLs with authentication
- Extract DRM keys from video manifests
- Combined response with stream URL and DRM information
- Ready for Vercel deployment
- CORS enabled for web applications

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your actual authentication tokens from studyweb.live

## Local Development

Run the API locally:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /api/video

Fetch video content with DRM keys

**Parameters:**
- `batchId` (required): Batch ID
- `subjectId` (required): Subject ID  
- `childId` (required): Child ID

**Example:**
```
GET /api/video?batchId=67be1ea9e92878bc16923fe8&subjectId=5f709c351b999704b83cca8a&childId=695fcb95dff25a9c77c7dc15
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://sec-prod-mediacdn.pw.live/...",
    "signedUrl": "?URLPrefix=...",
    "urlType": "penpencilvdo",
    "scheduleInfo": {...},
    "videoContainer": "DASH",
    "isCmaf": false,
    "serverTime": 1234567890,
    "cdnType": "Gcp"
  },
  "stream_url": "https://sec-prod-mediacdn.pw.live/...?URLPrefix=...",
  "url_type": "penpencilvdo",
  "drm": {
    "kid": "",
    "key": ""
  }
}
```

### GET /health

Health check endpoint

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

Make sure to set your environment variables in the Vercel dashboard.

## Environment Variables

- `ACCESS_TOKEN`: JWT access token from studyweb.live
- `REFRESH_TOKEN`: Refresh token from studyweb.live  
- `ANON_ID`: Anonymous ID from studyweb.live
- `API_BASE_URL`: Base URL (default: https://studyweb.live)

## Powered By

Satyam RojhaX
