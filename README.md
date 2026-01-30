# Piewallah Video API

A comprehensive FastAPI-based service for video content management, DRM key handling, and HLS streaming with robust fallback mechanisms.

## Features

- 🔐 Secure video URL fetching with authentication
- 🔑 DRM key extraction and management
- 🎬 HLS URL generation for adaptive streaming
- 🔄 Automatic fallback to external API when primary fails
- 📱 Combined response with stream URL, DRM keys, and HLS URLs
- 🚀 Ready for Vercel deployment
- 🌐 CORS enabled for web applications
- 🛡️ Enhanced error handling and reliability

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

Fetch video content with DRM keys and HLS URL (with automatic fallback)

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
    "urlType": "penpencilvdo",
    "scheduleInfo": {...},
    "videoContainer": "DASH",
    "isCmaf": false,
    "serverTime": 1234567890,
    "cdnType": "Gcp"
  },
  "stream_url": "https://example-cdn.com/...?URLPrefix=...",
  "url_type": "penpencilvdo",
  "drm": {
    "kid": "key-id",
    "key": "decryption-key"
  },
  "hls_url": "https://spider.bhanuyadav.workers.dev/play/[encoded-url]/main.m3u8"
}
```

### GET /api/video-url-details

Fetch video URL details from external API (fallback source)

**Parameters:**
- `parentid` (required): Parent ID (batch ID)
- `childid` (required): Child ID

**Example:**
```
GET /api/video-url-details?parentid=BATCH_ID&childid=CHILD_ID
```

### GET /api/hls

Generate HLS streaming URL with encryption key support

**Parameters:**
- `parentid` (required): Parent ID (batch ID)
- `childid` (required): Child ID
- `authorization` (optional): Authorization token for key fetching

**Example:**
```
GET /api/hls?parentid=BATCH_ID&childid=CHILD_ID&authorization=TOKEN
```

### GET /api/batches

Get list of all batches with pagination

**Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Example:**
```
GET /api/batches?page=1&limit=50
```

### GET /api/batch/{batchId}/details

Get detailed information for a specific batch

**Parameters:**
- `batchId` (required): Batch ID

**Example:**
```
GET /api/batch/BATCH_ID/details
```

### GET /api/jwt/{token} or GET /api/jwt?token=TOKEN

Decode JWT tokens and provide detailed information

**Parameters:**
- `token` (required): JWT token to decode

**Example:**
```
GET /api/jwt/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### GET /health

Health check endpoint

## Fallback Mechanism

The API includes a robust fallback system:

1. **Primary Source**: Attempts to fetch data from `studyweb.live` API
2. **Automatic Fallback**: If primary fails (403, 404, etc.), switches to external API
3. **HLS Generation**: Works with both primary and fallback data sources
4. **Graceful Degradation**: Always provides the best possible response

## Error Handling

- HTTP status errors are caught and handled gracefully
- Automatic fallback ensures service continuity
- Detailed logging for debugging
- Compatible error responses

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

## Usage Examples

### Complete Workflow

```bash
# 1. Get all batches
curl "http://localhost:8000/api/batches"

# 2. Get batch details
curl "http://localhost:8000/api/batch/BATCH_ID/details"

# 3. Get video with HLS URL (includes fallback)
curl "http://localhost:8000/api/video?batchId=BATCH_ID&subjectId=SUBJECT_ID&childId=CHILD_ID"

# 4. Get HLS streaming URL directly
curl "http://localhost:8000/api/hls?parentid=BATCH_ID&childid=CHILD_ID"

# 5. Decode JWT token if needed
curl "http://localhost:8000/api/jwt/YOUR_JWT_TOKEN"
```

## Response Format

All endpoints return consistent JSON responses with:
- `success`: Boolean indicating operation success
- `data`: Main response data (varies by endpoint)
- `errors`: Error information (if any)

## Powered By

Satyam RojhaX

## Version

2.0.0 - HLS Streaming & Fallback Support
