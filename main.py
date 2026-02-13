from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import base64
import re
import json
import jwt
import time
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

load_dotenv()

app = FastAPI(title="Piewallah Video API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BatchResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    pagination: Optional[Dict[str, Any]] = None
    errors: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"

class VideoResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    stream_url: Optional[str] = None
    url_type: Optional[str] = None
    drm: Optional[Dict[str, str]] = None
    hls_url: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"
    
    model_config = ConfigDict(exclude_none=True)

class HLSResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    hls_url: Optional[str] = None
    hls_key: Optional[str] = None
    errors: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"

class VideoURLResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    errors: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"

class DeltaStudyVideoResponse(BaseModel):
    video_url: Optional[str] = None
    url_type: Optional[str] = None
    drm: Optional[Dict[str, str]] = None
    proxy_url: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"

class JWTResponse(BaseModel):
    success: bool
    header: Dict[str, Any]
    payload: Dict[str, Any]
    signature: str
    token_info: Dict[str, Any]
    errors: Optional[str] = None
    powered_by: str = "SATYAM ROJHAX"
    only_used_for: str = "PIE WALLAH"

class PiewallahAPI:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "https://studyweb.live")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.anon_id = os.getenv("ANON_ID")
        self.perf_cookie = os.getenv("PERF_COOKIE")
        
        if not all([self.access_token, self.refresh_token, self.anon_id]):
            raise ValueError("Missing required authentication tokens in environment variables")
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "dnt": "1",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "cookie": f"anon_id={self.anon_id}; accessToken={self.access_token}; refreshToken={self.refresh_token}; {self.perf_cookie}" if self.perf_cookie else f"anon_id={self.anon_id}; accessToken={self.access_token}; refreshToken={self.refresh_token}"
        }
    
    async def fetch_batches(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Fetch batches from Heroku API"""
        url = "https://pw-api-0585c7015531.herokuapp.com/api/batches"
        params = {"page": page, "limit": limit}
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception as e:
                print(f"Failed to parse batches JSON response: {e}")
                content = response.content
                if content:
                    try:
                        text_content = content.decode('utf-8')
                        return json.loads(text_content)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        try:
                            text_content = content.decode('latin-1')
                            return json.loads(text_content)
                        except Exception as e2:
                            print(f"All decoding attempts failed for batches: {e2}")
                            raise HTTPException(status_code=500, detail="Failed to decode batches API response")
                else:
                    raise HTTPException(status_code=500, detail="Empty response from batches API")
    
    async def fetch_all_batches(self) -> Dict[str, Any]:
        """Fetch all batches by paginating through all pages"""
        all_batches = []
        current_page = 1
        page_size = 692  # As per your URL
        total_batches = 0
        
        while True:
            try:
                print(f"Fetching page {current_page}...")
                batches_data = await self.fetch_batches(page=current_page, limit=page_size)
                
                if not batches_data.get('success', True):
                    print(f"API returned failure on page {current_page}")
                    break
                
                # Extract batches from response
                if 'data' in batches_data:
                    if isinstance(batches_data['data'], list):
                        page_batches = batches_data['data']
                    elif isinstance(batches_data['data'], dict) and 'batches' in batches_data['data']:
                        page_batches = batches_data['data']['batches']
                    else:
                        page_batches = []
                    
                    if not page_batches:
                        print(f"No more batches found on page {current_page}")
                        break
                    
                    all_batches.extend(page_batches)
                    print(f"Found {len(page_batches)} batches on page {current_page}, total: {len(all_batches)}")
                    
                    # Check if we have all batches
                    if len(page_batches) < page_size:
                        print(f"Reached end of batches (got {len(page_batches)} < {page_size})")
                        break
                    
                    current_page += 1
                else:
                    print(f"No data field in response on page {current_page}")
                    break
                    
            except Exception as e:
                print(f"Error fetching page {current_page}: {e}")
                if current_page == 1:  # If first page fails, raise error
                    raise HTTPException(status_code=500, detail=f"Failed to fetch batches: {str(e)}")
                break  # Otherwise stop pagination
        
        return {
            "success": True,
            "data": {
                "batches": all_batches,
                "total_count": len(all_batches),
                "pages_fetched": current_page - 1
            },
            "pagination": {
                "total_batches": len(all_batches),
                "pages_fetched": current_page - 1,
                "last_page_size": len(all_batches) % page_size if len(all_batches) >= page_size else len(all_batches)
            }
        }
    
    async def fetch_batch_details(self, batch_id: str) -> Dict[str, Any]:
        """Fetch batch details from Heroku API"""
        url = f"https://pw-api-0585c7015531.herokuapp.com/api/batch/{batch_id}"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception as e:
                print(f"Failed to parse batch details JSON response: {e}")
                content = response.content
                if content:
                    try:
                        text_content = content.decode('utf-8')
                        return json.loads(text_content)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        try:
                            text_content = content.decode('latin-1')
                            return json.loads(text_content)
                        except Exception as e2:
                            print(f"All decoding attempts failed for batch details: {e2}")
                            raise HTTPException(status_code=500, detail="Failed to decode batch details API response")
                else:
                    raise HTTPException(status_code=500, detail="Empty response from batch details API")
    
    async def fetch_video_url(self, batch_id: str, subject_id: str, child_id: str) -> Dict[str, Any]:
        """Fetch video URL from studyweb.live API"""
        params = {
            "batchId": batch_id,
            "subjectId": subject_id,
            "childId": child_id
        }
        
        url = f"{self.base_url}/api/get-video-url"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
    
    async def fetch_drm_key(self, kid: str) -> Dict[str, Any]:
        """Fetch DRM key for the given KID"""
        # Remove dashes from KID
        kid = kid.replace("-", "")
        params = {"kid": kid}
        url = f"{self.base_url}/api/get-otp"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
    
    def extract_kid_from_mpd(self, mpd_content: str) -> Optional[str]:
        """Extract KID from MPD content"""
        try:
            # Look for all possible KIDs and return the one that works
            all_kids = []
            
            # Pattern 1: cenc:default_KID
            matches = re.findall(r'<cenc:default_KID>([^<]+)</cenc:default_KID>', mpd_content)
            all_kids.extend(matches)
            
            # Pattern 2: kid="..."
            matches = re.findall(r'kid="([^"]+)"', mpd_content)
            all_kids.extend(matches)
            
            # Pattern 3: schemeIdUri="urn:uuid:..."
            matches = re.findall(r'schemeIdUri="urn:uuid:([^"]+)"', mpd_content)
            all_kids.extend(matches)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_kids = []
            for kid in all_kids:
                if kid not in seen:
                    seen.add(kid)
                    unique_kids.append(kid)
            
            print(f"Found KIDs in MPD: {unique_kids}")
            return unique_kids[0] if unique_kids else None
                
        except Exception as e:
            print(f"Error extracting KID: {e}")
        
        return None
    
    async def fetch_mpd_content(self, mpd_url: str) -> str:
        """Fetch MPD manifest content"""
        async with httpx.AsyncClient() as client:
            response = await client.get(mpd_url, headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "accept-encoding": "gzip, deflate, br, zstd",
                "origin": "https://studyweb.live",
                "referer": "https://studyweb.live/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            })
            response.raise_for_status()
            
            # Handle base64 encoded MPD content
            content = response.text
            if content.startswith("data:application/octet-stream;base64,"):
                # Extract base64 part and decode
                base64_part = content.split(",", 1)[1]
                try:
                    decoded_bytes = base64.b64decode(base64_part)
                    # Try to decode as UTF-8, if it fails, try other encodings or return raw
                    try:
                        decoded_content = decoded_bytes.decode('utf-8')
                        return decoded_content
                    except UnicodeDecodeError:
                        # Try latin-1 as fallback
                        try:
                            decoded_content = decoded_bytes.decode('latin-1')
                            return decoded_content
                        except UnicodeDecodeError:
                            # Return as string representation of bytes if all else fails
                            return decoded_bytes.decode('utf-8', errors='replace')
                except Exception as e:
                    print(f"Failed to decode base64 content: {e}")
                    # Return the original content if decoding fails
                    return content
            
            return content
    
    async def fetch_video_url_details(self, parentid: str, childid: str) -> Dict[str, Any]:
        """Fetch video URL details from external API"""
        url = "https://video-url-details-v0.bhanuyadav.workers.dev/video-url-details"
        params = {
            "parentid": parentid,
            "childid": childid
        }
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def generate_hls_url(self, video_url: str) -> str:
        """Generate HLS URL from video URL"""
        url = "https://spider.bhanuyadav.workers.dev/generate"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        payload = {"url": video_url}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            # The response is the HLS URL directly
            return response.text.strip()
    
    async def fetch_hls_key(self, video_key: str, key: str, url_prefix: str, expires: str, key_name: str, signature: str, authorization: str) -> str:
        """Fetch HLS encryption key"""
        url = "https://api.penpencil.co/v1/videos/get-hls-key"
        params = {
            "videoKey": video_key,
            "key": key,
            "URLPrefix": url_prefix,
            "Expires": expires,
            "KeyName": key_name,
            "Signature": signature,
            "authorization": authorization
        }
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            # Follow redirect to get the actual key
            if response.status_code == 301:
                redirect_url = response.headers.get("location")
                if redirect_url:
                    key_response = await client.get(redirect_url)
                    key_response.raise_for_status()
                    # The key is returned as base64 data
                    return key_response.text
            return response.text
    
    async def fetch_deltastudy_video_url(self, batch_id: str, child_id: str) -> Dict[str, Any]:
        """Fetch video URL from deltastudy.site API"""
        url = "https://deltastudy.site/api/videosuper"
        params = {
            "batchId": batch_id,
            "childId": child_id
        }
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def fetch_deltastudy_kid(self, mpd_url: str) -> Dict[str, Any]:
        """Fetch KID from deltastudy.site API"""
        url = "https://deltastudy.site/api/kid"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        payload = {"mpdUrl": mpd_url}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def fetch_deltastudy_otp(self, kid: str) -> Dict[str, Any]:
        """Fetch DRM key (OTP) from deltastudy.site API"""
        url = f"https://deltastudy.site/api/otp"
        params = {"kid": kid}
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

piewallah_api = PiewallahAPI()

@app.get("/api/batches", response_model=BatchResponse)
async def get_batches(page: int = Query(1, description="Page number"), limit: int = Query(692, description="Number of batches per page")):
    """
    Fetch batches from Heroku API
    
    This endpoint fetches batches from the Heroku API with pagination support.
    Can fetch all batches or specific pages.
    
    Args:
        page: Page number to fetch (default: 1)
        limit: Number of batches per page (default: 692)
        
    Returns:
        Batch data with pagination information
    """
    try:
        if page == 0:  # Special case: fetch all batches
            batches_data = await piewallah_api.fetch_all_batches()
            return BatchResponse(**batches_data)
        else:
            batches_data = await piewallah_api.fetch_batches(page=page, limit=limit)
            
            # Extract pagination info if available
            pagination = None
            if 'pagination' in batches_data:
                pagination = batches_data['pagination']
            elif 'total' in batches_data or 'page' in batches_data:
                pagination = {
                    'page': page,
                    'limit': limit,
                    'total': batches_data.get('total', 0),
                    'pages': batches_data.get('pages', 0)
                }
            
            return BatchResponse(
                success=batches_data.get('success', True),
                data=batches_data.get('data', batches_data),
                pagination=pagination
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Batches API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/batch/{batchId}/details", response_model=BatchResponse)
async def get_batch_details(batchId: str):
    """
    Fetch detailed information for a specific batch
    
    This endpoint fetches detailed information for a specific batch from the Heroku API.
    
    Args:
        batchId: The ID of the batch to fetch details for
        
    Returns:
        Detailed batch information
    """
    try:
        batch_data = await piewallah_api.fetch_batch_details(batchId)
        
        return BatchResponse(
            success=batch_data.get('success', True),
            data=batch_data.get('data', batch_data),
            pagination=None
        )
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Batch with ID '{batchId}' not found")
        raise HTTPException(status_code=e.response.status_code, detail=f"Batch details API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/video", response_model=VideoResponse, response_model_exclude_none=True)
async def get_video(
    batchId: str = Query(..., description="Batch ID"),
    subjectId: str = Query(..., description="Subject ID"), 
    childId: str = Query(..., description="Child ID")
):
    """
    Fetch video content including stream URL and DRM keys
    
    This endpoint combines video URL fetching and DRM key retrieval into a single response.
    
    Args:
        batchId: The batch identifier
        subjectId: The subject identifier  
        childId: The child identifier
        
    Returns:
        Combined video data with stream URL and DRM information
    """
    try:
        # Fetch video URL first
        video_data = await piewallah_api.fetch_video_url(batchId, subjectId, childId)
        
        if not video_data.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch video URL")
        
        data = video_data.get("data", {})
        mpd_url = data.get("url")
        signed_url = data.get("signedUrl", "")
        
        if not mpd_url:
            raise HTTPException(status_code=404, detail="Video URL not found")
        
        # Construct full stream URL
        full_stream_url = f"{mpd_url}{signed_url}"
        
    except httpx.HTTPStatusError as e:
        # If studyweb.live fails with HTTP error, try fallback to external API
        print(f"🔄 studyweb.live failed with {e.response.status_code}, trying external API fallback")
        try:
            external_data = await piewallah_api.fetch_video_url_details(batchId, childId)
            if external_data.get("success"):
                external_video_data = external_data.get("data", {})
                mpd_url = external_video_data.get("url")
                signed_url = external_video_data.get("signedUrl", "")
                
                if mpd_url:
                    full_stream_url = f"{mpd_url}{signed_url}"
                    # Create a compatible data structure
                    data = {
                        "url": mpd_url,
                        "signedUrl": signed_url,
                        "urlType": "penpencilvdo",
                        "scheduleInfo": external_video_data.get("scheduleInfo", {}),
                        "videoContainer": "DASH",
                        "isCmaf": False,
                        "serverTime": int(time.time() * 1000),
                        "cdnType": "Gcp"
                    }
                    print(f"✅ Successfully fetched data from external API")
                else:
                    raise HTTPException(status_code=404, detail="Video URL not found in external API")
            else:
                raise HTTPException(status_code=400, detail="External API also failed")
        except Exception as e:
            print(f"❌ External API fallback also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and external APIs failed")
    except HTTPException:
        # Re-raise HTTP exceptions from our own code
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
    # Fetch MPD content to extract KID
    try:
        mpd_content = await piewallah_api.fetch_mpd_content(full_stream_url)
        
        # Extract all possible KIDs from MPD
        all_kids = []
        
        # Pattern 1: cenc:default_KID
        matches = re.findall(r'<cenc:default_KID>([^<]+)</cenc:default_KID>', mpd_content)
        all_kids.extend(matches)
        
        # Pattern 2: kid="..."
        matches = re.findall(r'kid="([^"]+)"', mpd_content)
        all_kids.extend(matches)
        
        # Pattern 3: schemeIdUri="urn:uuid:..."
        matches = re.findall(r'schemeIdUri="urn:uuid:([^"]+)"', mpd_content)
        all_kids.extend(matches)
        
        # Pattern 4: Any UUID patterns
        matches = re.findall(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', mpd_content.lower())
        all_kids.extend(matches)
        
        # Remove duplicates
        all_kids = list(set(all_kids))
        print(f"Found KIDs in MPD: {all_kids}")
        
        if not all_kids:
            print("No KIDs found in MPD")
            
    except Exception as e:
        print(f"Failed to fetch MPD content: {e}")
        
    # Fetch DRM key if KID is available
    drm_info = None
    if all_kids:
        # Try each KID until we find a working one
        for kid in all_kids:
            print(f"Trying KID: {kid}")
            try:
                drm_data = await piewallah_api.fetch_drm_key(kid)
                clear_keys = drm_data.get("clearKeys", {})
                
                # Check if the exact KID is in the response
                if kid in clear_keys:
                    drm_info = {
                        "kid": kid.replace("-", ""),
                        "key": clear_keys[kid]
                    }
                    print(f"✅ Found working DRM key for {kid}")
                    break
                else:
                    # Try to find a matching key (with/without hyphens)
                    for response_kid, response_key in clear_keys.items():
                        if response_kid.replace("-", "") == kid.replace("-", ""):
                            drm_info = {
                                "kid": kid.replace("-", ""),
                                "key": response_key
                            }
                            print(f"✅ Found working DRM key for {kid} (matched with {response_kid})")
                            break
                    
                    if drm_info:
                        break
                        
            except Exception as e:
                print(f"Failed to fetch DRM key for {kid}: {e}")
                continue
        
        if not drm_info:
            print("❌ No working DRM key found for any KID")
    else:
        print("❌ No KIDs available to try")
        
    # Fetch HLS URL in background using batchId and childId
    hls_url = None
    try:
        # First try to get HLS URL using the external API method
        video_details = await piewallah_api.fetch_video_url_details(batchId, childId)
        if video_details.get("success"):
            video_data = video_details.get("data", {})
            external_url = video_data.get("url")
            external_signed_url = video_data.get("signedUrl", "")
            if external_url:
                external_full_url = f"{external_url}{external_signed_url}"
                hls_url = await piewallah_api.generate_hls_url(external_full_url)
                print(f"✅ HLS URL generated via external API")
    except Exception as e:
        print(f"❌ External API method failed: {e}")
        
    # Check if CloudFront URL is present (indicates live stream)
    # If so, skip DRM lookup and HLS generation
    is_live_stream = "cloudfront.net" in full_stream_url.lower() or (data.get("url", "") and "cloudfront.net" in data.get("url", "").lower())
    
    if is_live_stream:
        print(f"🔴 CloudFront URL detected - this is a live stream, skipping DRM lookup and HLS generation")
        # Don't include drm and hls_url fields in response for live streams
        response_data = {
            "success": True,
            "data": data,
            "stream_url": full_stream_url,
            "url_type": data.get("urlType", "penpencilvdo")
        }
    else:
        # Fallback: Use existing stream_url if external API failed
        if not hls_url:
            try:
                print(f"🔄 Falling back to existing stream_url for HLS generation")
                hls_url = await piewallah_api.generate_hls_url(full_stream_url)
                print(f" HLS URL generated via fallback method")
            except Exception as e:
                print(f"❌ Fallback method also failed: {e}")
                hls_url = None
        
        # Construct response with drm and hls_url for non-live streams
        response_data = {
            "success": True,
            "data": data,
            "stream_url": full_stream_url,
            "url_type": data.get("urlType", "penpencilvdo"),
            "drm": drm_info,
            "hls_url": hls_url
        }
    
    return VideoResponse(**response_data)

@app.get("/api/jwt/{token}", response_model=JWTResponse)
async def decode_jwt_token(token: str):
    """
    Decode JWT token and provide detailed information
    
    This endpoint decodes JWT tokens without requiring a secret key and provides:
    - Header information
    - Payload/claims
    - Signature details
    - Token validation info
    - Expiration and timing details
    
    Args:
        token: The JWT token to decode (can be provided in URL path)
        
    Returns:
        Detailed JWT token information
    """
    try:
        # Remove any URL encoding or whitespace
        token = token.strip().replace("%2E", ".").replace("%2F", "/").replace("%2B", "+")
        
        # Check if token has 3 parts
        parts = token.split('.')
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail="Invalid JWT format. Token must have 3 parts separated by dots")
        
        header_part, payload_part, signature_part = parts
        
        # Decode header
        try:
            # Add padding if needed
            header_part_padded = header_part + '=' * (-len(header_part) % 4)
            header_decoded = base64.urlsafe_b64decode(header_part_padded)
            header_data = json.loads(header_decoded.decode('utf-8'))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode JWT header: {str(e)}")
        
        # Decode payload
        try:
            # Add padding if needed
            payload_part_padded = payload_part + '=' * (-len(payload_part) % 4)
            payload_decoded = base64.urlsafe_b64decode(payload_part_padded)
            payload_data = json.loads(payload_decoded.decode('utf-8'))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to decode JWT payload: {str(e)}")
        
        # Analyze token information
        token_info = {}
        current_time = int(__import__('time').time())
        
        # Check expiration
        if 'exp' in payload_data:
            exp_time = payload_data['exp']
            token_info['expiration'] = {
                'timestamp': exp_time,
                'datetime': __import__('datetime').datetime.fromtimestamp(exp_time).isoformat(),
                'is_expired': current_time > exp_time,
                'time_remaining': exp_time - current_time if current_time <= exp_time else 0
            }
        
        # Check not before
        if 'nbf' in payload_data:
            nbf_time = payload_data['nbf']
            token_info['not_before'] = {
                'timestamp': nbf_time,
                'datetime': __import__('datetime').datetime.fromtimestamp(nbf_time).isoformat(),
                'is_valid_now': current_time >= nbf_time
            }
        
        # Check issued at
        if 'iat' in payload_data:
            iat_time = payload_data['iat']
            token_info['issued_at'] = {
                'timestamp': iat_time,
                'datetime': __import__('datetime').datetime.fromtimestamp(iat_time).isoformat(),
                'time_ago': current_time - iat_time
            }
        
        # Check subject
        if 'sub' in payload_data:
            token_info['subject'] = payload_data['sub']
        
        # Check issuer
        if 'iss' in payload_data:
            token_info['issuer'] = payload_data['iss']
        
        # Check audience
        if 'aud' in payload_data:
            token_info['audience'] = payload_data['aud']
        
        # Check token ID
        if 'jti' in payload_data:
            token_info['jwt_id'] = payload_data['jti']
        
        # Analyze algorithm
        if 'alg' in header_data:
            token_info['algorithm'] = header_data['alg']
        
        # Analyze token type
        if 'typ' in header_data:
            token_info['token_type'] = header_data['typ']
        
        # Token structure info
        token_info['structure'] = {
            'header_length': len(header_part),
            'payload_length': len(payload_part),
            'signature_length': len(signature_part),
            'total_length': len(token)
        }
        
        # Common claims analysis
        common_claims = ['name', 'email', 'role', 'scope', 'permissions', 'userId', 'user_id']
        found_claims = {}
        for claim in common_claims:
            if claim in payload_data:
                found_claims[claim] = payload_data[claim]
        
        if found_claims:
            token_info['common_claims'] = found_claims
        
        # Signature info (without verification)
        token_info['signature'] = {
            'present': len(signature_part) > 0,
            'length': len(signature_part),
            'algorithm': header_data.get('alg', 'unknown'),
            'note': 'Signature is present but not verified (no secret key provided)'
        }
        
        return JWTResponse(
            success=True,
            header=header_data,
            payload=payload_data,
            signature=signature_part,
            token_info=token_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode JWT token: {str(e)}")

@app.get("/api/jwt", response_model=JWTResponse)
async def decode_jwt_query(token: str = Query(..., description="JWT token to decode")):
    """
    Decode JWT token via query parameter (alternative to path parameter)
    
    Args:
        token: JWT token as query parameter
        
    Returns:
        Detailed JWT token information
    """
    return await decode_jwt_token(token)

@app.get("/")
async def root():
    return {
        "status": False,
        "message": "Please update your app. You are using outdated version(1).",
        "data": [],
        "time": 1770989585,
        "interval": 10,
        "limit": 0,
        "cd_time": 17709764491497
    }

@app.get("/api")
async def api_documentation():
    """
    Comprehensive API Documentation
    
    This endpoint provides complete documentation for all available endpoints
    including parameters, examples, and response formats.
    """
    return {
        "title": "Piewallah Video API Documentation",
        "version": "2.0.0",
        "description": "Complete API for video streaming, batch management, JWT decoding, and HLS streaming",
        "base_url": "https://piewallahapi.vercel.app",
        "powered_by": "SATYAM ROJHAX",
        "only_used_for": "PIE WALLAH",
        "endpoints": {
            "video_api": {
                "endpoint": "/api/video",
                "method": "GET",
                "description": "Fetch video content with DRM keys from studyweb.live API",
                "authentication": "Required (tokens from .env)",
                "parameters": {
                    "batchId": {
                        "type": "string",
                        "required": True,
                        "description": "Batch ID from batches list",
                        "example": "67be1ea9e92878bc16923fe8"
                    },
                    "subjectId": {
                        "type": "string", 
                        "required": True,
                        "description": "Subject ID from batch details",
                        "example": "5f709c26796f410011b7b80b"
                    },
                    "childId": {
                        "type": "string",
                        "required": True,
                        "description": "Child ID for specific video",
                        "example": "695757705590a2c154a8ca27"
                    }
                },
                "example_request": "/api/video?batchId=67be1ea9e92878bc16923fe8&subjectId=5f709c26796f410011b7b80b&childId=695757705590a2c154a8ca27",
                "example_response": {
                    "success": True,
                    "data": {
                        "url": "https://sec-prod-mediacdn.pw.live/.../master.mpd",
                        "signedUrl": "?URLPrefix=...&Expires=...&KeyName=pw-prod-key&Signature=...",
                        "urlType": "penpencilvdo",
                        "videoContainer": "DASH",
                        "scheduleInfo": {
                            "startTime": "2026-01-09T11:30:00.000Z",
                            "endTime": "2026-01-09T12:34:18.801Z"
                        }
                    },
                    "stream_url": "https://sec-prod-mediacdn.pw.live/.../master.mpd?URLPrefix=...",
                    "drm": {
                        "kid": "7c4ffcd57072d39995adf6cae1b50359",
                        "key": "676c5f8bf5af7259c0de389a7f133046"
                    }
                },
                "features": [
                    "Multiple base URL fallbacks",
                    "Dynamic DRM key extraction",
                    "MPD manifest parsing",
                    "Error handling"
                ]
            },
            "batches_api": {
                "endpoint": "/api/batches",
                "method": "GET",
                "description": "Fetch list of all available batches",
                "authentication": "Not required",
                "parameters": {
                    "page": {
                        "type": "integer",
                        "required": False,
                        "default": 1,
                        "description": "Page number for pagination",
                        "example": 1
                    },
                    "limit": {
                        "type": "integer",
                        "required": False,
                        "default": 692,
                        "description": "Number of batches per page",
                        "example": 10
                    }
                },
                "special_endpoints": {
                    "all_batches": {
                        "url": "/api/batches?page=0",
                        "description": "Fetch all batches without pagination"
                    }
                },
                "example_request": "/api/batches?page=1&limit=10",
                "example_response": {
                    "success": True,
                    "data": [
                        {
                            "_id": "6789f904f69b15eb632db640",
                            "name": "Lakshya JEE 2.0 2026",
                            "byName": "For JEE Aspirants",
                            "language": "Hinglish",
                            "exam": "IIT-JEE",
                            "class": "12",
                            "start_date": "2025-06-10",
                            "end_date": "2026-06-30"
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "limit": 10,
                        "total": 692
                    }
                }
            },
            "batch_details_api": {
                "endpoint": "/api/batch/{batchId}/details",
                "method": "GET",
                "description": "Fetch detailed information for a specific batch",
                "authentication": "Not required",
                "parameters": {
                    "batchId": {
                        "type": "string",
                        "required": True,
                        "description": "Batch ID from batches list",
                        "example": "67ebbb8fbe321bd5247df0ba"
                    }
                },
                "example_request": "/api/batch/67ebbb8fbe321bd5247df0ba/details",
                "example_response": {
                    "success": True,
                    "data": {
                        "_id": "67ebbb8fbe321bd5247df0ba",
                        "name": "UPSC CSE 2026 Foundation",
                        "description": "Complete foundation course for UPSC CSE 2026",
                        "language": "Hinglish",
                        "exam": "UPSC",
                        "subjects": [
                            {
                                "_id": "67f3be806b0ca88c8b3f2b52",
                                "subject": "Environment",
                                "lectureCount": 3,
                                "displayOrder": 2
                            }
                        ],
                        "fee": {
                            "amount": 0,
                            "currency": "INR"
                        }
                    }
                }
            },
            "video_url_details_api": {
                "endpoint": "/api/video-url-details",
                "method": "GET",
                "description": "Fetch complete video URL details from deltastudy.site APIs (combined 3-in-1 endpoint)",
                "authentication": "Not required",
                "parameters": {
                    "batchId": {
                        "type": "string",
                        "required": True,
                        "description": "Batch ID",
                        "example": "678a0324dab28c8848cc026f"
                    },
                    "childId": {
                        "type": "string",
                        "required": True,
                        "description": "Child ID",
                        "example": "68317eb12da436329a1dc5e6"
                    }
                },
                "example_request": "/api/video-url-details?batchId=678a0324dab28c8848cc026f&childId=68317eb12da436329a1dc5e6",
                "example_response": {
                    "video_url": "https://sec-prod-mediacdn.pw.live/fd4e7eea-8645-486d-b629-c00c21823d2c/master.mpd?URLPrefix=aHR0cHM6Ly9zZWMtcHJvZC1tZWRpYWNkbi5wdy5saXZlL2ZkNGU3ZWVhLTg2NDUtNDg2ZC1iNjI5LWMwMGMyMTgyM2QyYw&Expires=1769794258&KeyName=pw-prod-key&Signature=wHdz5MxgbFjhR3FvxNrUAW9z7D-1Lc1LGM3YEhKHEb9PB64jNAukCeXu_5mQSMeyLWw50V6mWcPlQ56t6jXjAQ",
                    "url_type": "penpencilvdo",
                    "drm": {
                        "kid": "d613fcf7fefefa4878136b236ba1f908",
                        "key": "7489a93072d0b347a92df4c6d8f9fcf0"
                    },
                    "proxy_url": "https://spider.bhanuyadav.workers.dev/play/aHR0cHM6Ly9zZWMtcHJvZC1tZWRpYWNkbi5wdy5saXZlL2YzMjRlNzc2LTlhMmUtNGQ2Yy05N2Q0LTlmNzE5YzRlMDZhZS9tYXN0ZXIubXBkP1VSTFByZWZpeD1hSFIwY0hNNkx5OXpaV010Y0hKdlpDMXRaV1JwWVdOa2JpNXdkeTVzYVhabEwyWXpNalJsTnpjMkxUbGhNbVV0TkdRMll5MDVOMlEwTFRsbU56RTVZelJsTURaaFpRJkV4cGlyZXM9MTc2OTc5NDMwMiZLZXlOYW1lPXB3LXByb2Qta2V5JlNpZ25hdHVyZT1BSnVpUmJrOVpOUzdfV2tBWDR3NXQyQlFDUlFVUGRmdDA1dmJqZVpZX01KajRyVURHTkFpVHNCZENqZVA2djBNY2o4WHRUbzc5N0JCRzBaUXNnbS1DQQ==/main.m3u8",
                    "powered_by": "SATYAM ROJHAX",
                    "only_used_for": "PIE WALLAH"
                },
                "features": [
                    "Combined 3 API calls in 1 request",
                    "Automatic video URL fetching",
                    "DRM KID extraction",
                    "DRM key retrieval",
                    "Complete streaming solution"
                ]
            },
            "video_url_details_external_api": {
                "endpoint": "/api/video-url-details-external",
                "method": "GET",
                "description": "Fetch video URL details from external API",
                "authentication": "Not required",
                "parameters": {
                    "parentid": {
                        "type": "string",
                        "required": True,
                        "description": "Parent ID (batch ID)",
                        "example": "67be1ea9e92878bc16923fe8"
                    },
                    "childid": {
                        "type": "string",
                        "required": True,
                        "description": "Child ID",
                        "example": "69416be84090b507f5ce250a"
                    }
                },
                "example_request": "/api/video-url-details-external?parentid=67be1ea9e92878bc16923fe8&childid=69416be84090b507f5ce250a",
                "example_response": {
                    "success": True,
                    "data": {
                        "url": "https://sec-prod-mediacdn.pw.live/a433e1ca-53d8-4f91-b62d-73adfcdf19f6/master.mpd",
                        "signedUrl": "?URLPrefix=...&Expires=...&KeyName=pw-prod-key&Signature=...",
                        "drmDetails": null,
                        "scheduleInfo": {
                            "startTime": "2025-12-17T09:30:00.000Z",
                            "endTime": "2025-12-17T11:16:28.617Z"
                        },
                        "dataFrom": "StudyMaxer"
                    }
                }
            },
            "hls_api": {
                "endpoint": "/api/hls",
                "method": "GET",
                "description": "Generate HLS URL and fetch encryption key",
                "authentication": "Optional (for HLS key fetching)",
                "parameters": {
                    "parentid": {
                        "type": "string",
                        "required": True,
                        "description": "Parent ID (batch ID)",
                        "example": "67be1ea9e92878bc16923fe8"
                    },
                    "childid": {
                        "type": "string",
                        "required": True,
                        "description": "Child ID",
                        "example": "69416be84090b507f5ce250a"
                    },
                    "authorization": {
                        "type": "string",
                        "required": False,
                        "description": "Authorization token for HLS key fetching",
                        "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                },
                "example_request": "/api/hls?parentid=67be1ea9e92878bc16923fe8&childid=69416be84090b507f5ce250a&authorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "example_response": {
                    "success": True,
                    "data": {
                        "url": "https://sec-prod-mediacdn.pw.live/a433e1ca-53d8-4f91-b62d-73adfcdf19f6/master.mpd",
                        "signedUrl": "?URLPrefix=...&Expires=...&KeyName=pw-prod-key&Signature=...",
                        "drmDetails": null,
                        "scheduleInfo": {
                            "startTime": "2025-12-17T09:30:00.000Z",
                            "endTime": "2025-12-17T11:16:28.617Z"
                        }
                    },
                    "hls_url": "https://spider.bhanuyadav.workers.dev/play/aHR0cHM6Ly9zZWMtcHJvZC1tZWRpYWNkbi5wdy5saXZlL2E0MzNlMWNhLTUzZDgtNGY5MS1iNjJkLTczYWRmY2RmMTlmNi9tYXN0ZXIubXBkP1VSTFByZWZpeD1hSFIwY0hNNkx5OXpaV010Y0hKdlpDMXRaV1JwWVdOa2JpNXdkeTVzYVhabEwyRTBNek5sTVdOaExUVXpaRGd0TkdZNU1TMWlOakprTFRjellXUm1ZMlJtTVRsbU5nJkV4cGlyZXM9MTc2OTc4NzE4NSZLZXlOYW1lPXB3LXByb2Qta2V5JlNpZ25hdHVyZT1MLXU1OS1xeTM1Uk1sVDR6ektReG1TaTVVZHg1RmhuOU54ZThpeXRNNHI5aC1DTmdzZGpzN0VDdy1iOTRRTjFibUgtbkx6eW91N0dCU09uN1BJMTZBZw==/main.m3u8",
                    "hls_key": "data:application/octet-stream;base64,jJVkue+pYHf+PEPhkHYAVA=="
                },
                "features": [
                    "Automatic HLS URL generation",
                    "Encryption key fetching",
                    "Complete streaming solution",
                    "Error handling"
                ]
            },
            "jwt_decoder_api": {
                "path_parameter": {
                    "endpoint": "/api/jwt/{token}",
                    "method": "GET",
                    "description": "Decode JWT token via path parameter",
                    "authentication": "Not required",
                    "parameters": {
                        "token": {
                            "type": "string",
                            "required": True,
                            "description": "JWT token to decode",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                        }
                    },
                    "example_request": "/api/jwt/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2OTYxNDQxYzcwY2U2NzVjNjRiMTA4NWQiLCJuYW1lIjoiVXRrYXJzaCAiLCJpYXQiOjE3Njc5ODIxMDksImV4cCI6MTc2OTI3ODEwOX0.Od-Xsge4x34OWi5CZ3La-SHXfVvYhZXaZ_9YxvkCt10"
                },
                "query_parameter": {
                    "endpoint": "/api/jwt",
                    "method": "GET",
                    "description": "Decode JWT token via query parameter",
                    "authentication": "Not required",
                    "parameters": {
                        "token": {
                            "type": "string",
                            "required": True,
                            "description": "JWT token to decode",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                        }
                    },
                    "example_request": "/api/jwt?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                },
                "example_response": {
                    "success": True,
                    "header": {
                        "alg": "HS256",
                        "typ": "JWT"
                    },
                    "payload": {
                        "userId": "6961441c70ce675c64b1085d",
                        "name": "Utkarsh",
                        "iat": 1767982109,
                        "exp": 1769278109
                    },
                    "token_info": {
                        "expiration": {
                            "timestamp": 1769278109,
                            "datetime": "2026-01-24T23:38:29",
                            "is_expired": False,
                            "time_remaining": 1291349
                        },
                        "algorithm": "HS256",
                        "token_type": "JWT"
                    }
                }
            },
            "health_check": {
                "endpoint": "/health",
                "method": "GET",
                "description": "API health check endpoint",
                "authentication": "Not required",
                "example_request": "/health",
                "example_response": {
                    "status": "healthy",
                    "service": "piewallah-api"
                }
            }
        },
        "error_handling": {
            "description": "All endpoints return appropriate HTTP status codes and error messages",
            "common_errors": {
                "400": "Bad Request - Invalid parameters",
                "404": "Not Found - Resource not found",
                "500": "Internal Server Error - Server error"
            }
        },
        "base_urls_fallback": {
            "description": "Video API uses multiple base URLs with automatic fallback",
            "urls": [
                "https://studyweb.live (primary)",
                "https://studymeta.in (fallback 1)",
                "https://pwthor.site (fallback 2)"
            ]
        },
        "authentication": {
            "video_api": {
                "required": True,
                "method": "Bearer tokens via cookies",
                "env_variables": [
                    "ACCESS_TOKEN",
                    "REFRESH_TOKEN", 
                    "ANON_ID"
                ]
            },
            "other_apis": {
                "required": False,
                "description": "Batches and JWT decoder APIs don't require authentication"
            }
        },
        "usage_examples": {
            "complete_workflow": [
                "1. GET /api/batches - Get list of all batches",
                "2. GET /api/batch/{batchId}/details - Get batch details and subjects",
                "3. GET /api/video?batchId=&subjectId=&childId= - Get video with DRM keys",
                "4. GET /api/video-url-details?batchId=&childId= - Get complete video details (3-in-1 deltastudy.site)",
                "5. GET /api/video-url-details-external?parentid=&childid= - Get video URL details (external API)",
                "6. GET /api/hls?parentid=&childid=&authorization= - Get HLS streaming URL and key",
                "7. GET /api/jwt/{token} - Decode authentication tokens if needed"
            ]
        }
    }

@app.get("/api/video-url-details", response_model=DeltaStudyVideoResponse)
async def get_video_url_details_deltastudy(
    batchId: str = Query(..., description="Batch ID"),
    childId: str = Query(..., description="Child ID")
):
    """
    Fetch complete video URL details from deltastudy.site APIs
    
    This endpoint combines three API calls:
    1. GET /api/videosuper - Get video URL
    2. POST /api/kid - Get DRM KID from MPD URL
    3. GET /api/otp - Get DRM key using KID
    
    Args:
        batchId: The batch ID
        childId: The child ID
        
    Returns:
        Complete video details including URL and DRM information
    """
    try:
        # Step 1: Fetch video URL from deltastudy.site
        print(f"🎥 Fetching video URL for batchId: {batchId}, childId: {childId}")
        video_response = await piewallah_api.fetch_deltastudy_video_url(batchId, childId)
        
        if not video_response.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch video URL from deltastudy.site")
        
        video_data = video_response.get("data", {})
        video_url = video_data.get("video_url")
        message = video_response.get("message")
        timestamp = video_response.get("timestamp")
        
        if not video_url:
            raise HTTPException(status_code=404, detail="Video URL not found in deltastudy.site response")
        
        print(f"✅ Got video URL: {video_url}")
        
        # Step 2: Fetch KID using the MPD URL
        print(f"🔑 Fetching KID for MPD URL")
        kid_response = await piewallah_api.fetch_deltastudy_kid(video_url)
        
        if not kid_response.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch KID from deltastudy.site")
        
        kid = kid_response.get("kid")
        if not kid:
            raise HTTPException(status_code=404, detail="KID not found in deltastudy.site response")
        
        print(f"✅ Got KID: {kid}")
        
        # Step 3: Fetch DRM key using KID
        print(f"🔐 Fetching DRM key for KID: {kid}")
        otp_response = await piewallah_api.fetch_deltastudy_otp(kid)
        
        if not otp_response.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch DRM key from deltastudy.site")
        
        drm_key = otp_response.get("key")
        key_id = otp_response.get("keyid")
        
        if not drm_key:
            raise HTTPException(status_code=404, detail="DRM key not found in deltastudy.site response")
        
        print(f"✅ Got DRM key: {drm_key}")
        
        # Generate HLS URL (proxy_url) using the same logic as /api/video
        proxy_url = None
        try:
            print(f"🔄 Generating HLS URL (proxy_url)...")
            proxy_url = await piewallah_api.generate_hls_url(video_url)
            print(f"✅ HLS URL generated: {proxy_url}")
        except Exception as e:
            print(f"❌ Failed to generate HLS URL: {e}")
            proxy_url = None
        
        # Construct response in the exact format requested
        response_data = {
            "video_url": video_url,
            "url_type": "penpencilvdo",
            "drm": {
                "kid": key_id or kid,
                "key": drm_key
            },
            "proxy_url": proxy_url
        }
        
        print(f"🎉 Successfully fetched complete video details")
        return DeltaStudyVideoResponse(**response_data)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"DeltaStudy API request failed: {e}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in video URL details endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/video-url-details-external", response_model=VideoURLResponse)
async def get_video_url_details(
    parentid: str = Query(..., description="Parent ID (batch ID)"),
    childid: str = Query(..., description="Child ID")
):
    """
    Fetch video URL details from external API
    
    This endpoint fetches video URL details including the signed URL and DRM information
    from the external video-url-details API.
    
    Args:
        parentid: The parent ID (batch ID)
        childid: The child ID
        
    Returns:
        Video URL details with signed URL and DRM information
    """
    try:
        video_data = await piewallah_api.fetch_video_url_details(parentid, childid)
        
        return VideoURLResponse(
            success=video_data.get("success", True),
            data=video_data.get("data", video_data),
            errors=None
        )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Video URL details API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/hls", response_model=HLSResponse)
async def get_hls_url(
    parentid: str = Query(..., description="Parent ID (batch ID)"),
    childid: str = Query(..., description="Child ID"),
    authorization: str = Query(None, description="Authorization token for HLS key")
):
    """
    Generate HLS URL and fetch encryption key
    
    This endpoint combines video URL details fetching, HLS generation, and key retrieval
    to provide a complete HLS streaming solution.
    
    Args:
        parentid: The parent ID (batch ID)
        childid: The child ID
        authorization: Optional authorization token for fetching HLS key
        
    Returns:
        HLS URL and encryption key information
    """
    try:
        # Step 1: Fetch video URL details
        video_data = await piewallah_api.fetch_video_url_details(parentid, childid)
        
        if not video_data.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch video URL details")
        
        data = video_data.get("data", {})
        video_url = data.get("url")
        signed_url = data.get("signedUrl", "")
        
        if not video_url:
            raise HTTPException(status_code=404, detail="Video URL not found")
        
        # Step 2: Construct full video URL
        full_video_url = f"{video_url}{signed_url}"
        
        # Step 3: Generate HLS URL
        hls_url = await piewallah_api.generate_hls_url(full_video_url)
        
        # Step 4: Extract video key from URL for key fetching
        video_key = None
        if "/" in video_url:
            # Extract video key from URL path (last UUID-like segment before master.mpd)
            url_parts = video_url.split("/")
            for part in url_parts:
                if len(part) == 36 and "-" in part:  # UUID format
                    video_key = part
                    break
        
        hls_key = None
        
        # Step 5: Fetch HLS key if authorization is provided and video_key is found
        if authorization and video_key:
            try:
                # Parse the signed URL parameters
                url_params = {}
                if signed_url.startswith("?"):
                    param_string = signed_url[1:]  # Remove the leading '?'
                    for param in param_string.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            url_params[key] = value
                
                hls_key = await piewallah_api.fetch_hls_key(
                    video_key=video_key,
                    key="enc.key",
                    url_prefix=url_params.get("URLPrefix", ""),
                    expires=url_params.get("Expires", ""),
                    key_name=url_params.get("KeyName", ""),
                    signature=url_params.get("Signature", ""),
                    authorization=authorization
                )
            except Exception as e:
                print(f"Failed to fetch HLS key: {e}")
                hls_key = None
        
        # Construct response
        response_data = {
            "success": True,
            "data": data,
            "hls_url": hls_url,
            "hls_key": hls_key
        }
        
        return HLSResponse(**response_data)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HLS API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint with video API status monitoring
    
    This endpoint checks the health of the service and tests all video API base URLs.
    If all video APIs fail, it shows offline status.
    """
    video_api_status = {}
    
    # Test each video API base URL
    test_batch_id = "67be1ea9e92878bc16923fe8"
    test_subject_id = "5f709c26796f410011b7b80b"
    test_child_id = "695757705590a2c154a8ca27"
    
    for base_url in piewallah_api.base_urls:
        try:
            url = f"{base_url}/api/get-video-url"
            params = {
                "batchId": test_batch_id,
                "subjectId": test_subject_id,
                "childId": test_child_id
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=piewallah_api.get_headers())
                if response.status_code == 200:
                    video_api_status[base_url] = "online"
                else:
                    # Handle 307 redirects as working (studymeta.in and pwthor.site redirect to auth)
                    if response.status_code == 307:
                        video_api_status[base_url] = "online_redirect"
                    else:
                        video_api_status[base_url] = f"error_{response.status_code}"
        except Exception as e:
            video_api_status[base_url] = "offline"
    
    # Check if all video APIs failed
    all_failed = all(status in ["offline", "error_404", "error_500", "error_401", "error_403"] for status in video_api_status.values())
    
    if all_failed:
        return {
            "status": "offline",
            "service": "piewallah-api",
            "message": "LIBI LIBI !!!",
            "video_apis": video_api_status,
            "all_apis_failed": True,
            "description": "All video APIs are offline",
            "powered_by": "SATYAM ROJHAX",
            "only_used_for": "PIE WALLAH"
        }
    else:
        return {
            "status": "healthy",
            "service": "piewallah-api",
            "video_apis": video_api_status,
            "all_apis_failed": False,
            "description": "Service is running with at least one video API online",
            "powered_by": "SATYAM ROJHAX",
            "only_used_for": "PIE WALLAH"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
