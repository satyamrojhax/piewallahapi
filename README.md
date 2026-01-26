# Piewallah Video API

A FastAPI-based service for video content management and DRM key handling.

## Features

- Secure video URL fetching with authentication
- DRM key extraction and management
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

3. Update `.env` with your authentication tokens

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
GET /api/video?batchId=BATCH_ID&subjectId=SUBJECT_ID&childId=CHILD_ID
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example-cdn.com/...",
    "signedUrl": "?URLPrefix=...",
    "urlType": "video",
    "scheduleInfo": {...},
    "videoContainer": "DASH",
    "isCmaf": false,
    "serverTime": 1234567890,
    "cdnType": "CDN"
  },
  "stream_url": "https://example-cdn.com/...?URLPrefix=...",
  "url_type": "video",
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

- `ACCESS_TOKEN`: JWT access token for authentication
- `REFRESH_TOKEN`: Refresh token for session management  
- `ANON_ID`: Anonymous identifier
- `API_BASE_URL`: Base URL for API endpoints
- `PERF_COOKIE`: Performance cookie (optional)

## Powered By

Satyam RojhaX
