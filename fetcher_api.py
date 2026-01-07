"""
Standalone API Server for MFAPI Fetcher

A REST API server that provides endpoints for fetching mutual fund data
from MFAPI.in with caching capabilities.

Run: python fetcher_api.py
API will be available at: http://localhost:8000

Endpoints:
- GET /schemes - Get all schemes
- GET /schemes/search?q=query - Search schemes
- GET /schemes/{code} - Get scheme details
- GET /schemes/{code}/nav - Get latest NAV
- GET /cache/info - Get cache information
- POST /cache/clear - Clear cache
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mfapi_fetcher import MFAPIFetcher
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(
    title="MFAPI Fetcher API",
    description="REST API for Indian Mutual Fund data from MFAPI.in",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize fetcher
try:
    fetcher = MFAPIFetcher()
except Exception as e:
    print(f"Error initializing fetcher: {e}")
    raise

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "MFAPI Fetcher API",
        "version": "1.0.0",
        "docs": "/docs",
        "cache_info": fetcher.get_cache_info()
    }

@app.get("/schemes")
async def get_all_schemes(use_cache: bool = True) -> List[Dict[str, Any]]:
    """Get list of all mutual fund schemes"""
    try:
        schemes = fetcher.get_all_schemes(use_cache=use_cache)
        return schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemes/search")
async def search_schemes(
    q: str = Query(..., description="Search query"),
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """Search for schemes by name"""
    try:
        schemes = fetcher.search_schemes(q, use_cache=use_cache)
        return schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemes/{scheme_code}")
async def get_scheme(
    scheme_code: str,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get detailed information about a specific scheme"""
    try:
        scheme = fetcher.get_scheme(scheme_code, use_cache=use_cache)
        return scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemes/{scheme_code}/nav")
async def get_latest_nav(
    scheme_code: str,
    use_cache: bool = True
) -> Dict[str, str]:
    """Get the latest NAV for a scheme"""
    try:
        nav = fetcher.get_latest_nav(scheme_code, use_cache=use_cache)
        if nav is None:
            raise HTTPException(status_code=404, detail="NAV not found")
        return nav
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/info")
async def get_cache_info() -> Dict[str, Any]:
    """Get cache information"""
    return fetcher.get_cache_info()

@app.post("/cache/clear")
async def clear_cache(scheme_code: Optional[str] = None):
    """Clear cache files"""
    try:
        fetcher.clear_cache(scheme_code)
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)