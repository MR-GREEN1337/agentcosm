"""
Enhanced Pexels API Integration for Images and Videos
Comprehensive media fetching with fallbacks and optimization
"""

import requests
from typing import Dict, List, Any, Optional, Literal
from cosm.settings import settings


def get_pexels_media(
    query: str,
    media_type: Literal["images", "videos", "both"] = "images",
    per_page: int = 5,
    orientation: str = "landscape",
    size: str = "large",
    min_width: Optional[int] = None,
    min_height: Optional[int] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Comprehensive Pexels media fetcher for images and videos

    Args:
        query: Search term for media content
        media_type: Type of media to fetch ("images", "videos", "both")
        per_page: Number of results per media type (1-80)
        orientation: Media orientation ("landscape", "portrait", "square")
        size: Image size preference ("large", "medium", "small")
        min_width: Minimum width for images (pixels)
        min_height: Minimum height for images (pixels)
        min_duration: Minimum duration for videos (seconds)
        max_duration: Maximum duration for videos (seconds)

    Returns:
        Dictionary with 'images' and/or 'videos' keys containing media data
    """
    try:
        # Validate API key
        pexels_api_key = settings.PEXELS_API_KEY
        if not pexels_api_key:
            print("⚠️ Pexels API key not found in settings")
            return get_fallback_media(query, media_type)

        headers = {"Authorization": pexels_api_key}
        results = {"images": [], "videos": []}

        # Fetch images if requested
        if media_type in ["images", "both"]:
            print(f"🖼️ Fetching {per_page} images for '{query}'...")
            images = fetch_pexels_images(
                query, per_page, orientation, size, min_width, min_height, headers
            )
            results["images"] = images

        # Fetch videos if requested
        if media_type in ["videos", "both"]:
            print(f"🎥 Fetching {per_page} videos for '{query}'...")
            videos = fetch_pexels_videos(
                query,
                per_page,
                orientation,
                min_width,
                min_height,
                min_duration,
                max_duration,
                headers,
            )
            results["videos"] = videos

        # Log results summary
        total_images = len(results.get("images", []))
        total_videos = len(results.get("videos", []))
        print(
            f"✅ Successfully fetched {total_images} images and {total_videos} videos"
        )

        return results

    except Exception as e:
        print(f"❌ Error fetching Pexels media: {e}")
        return get_fallback_media(query, media_type)


def fetch_pexels_images(
    query: str,
    per_page: int,
    orientation: str,
    size: str,
    min_width: Optional[int],
    min_height: Optional[int],
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Fetch images from Pexels API"""
    try:
        # Build image search parameters
        params = {
            "query": query,
            "per_page": min(per_page, 80),  # Pexels max limit
            "orientation": orientation,
            "size": size,
        }

        # Add optional dimension filters
        if min_width:
            params["min_width"] = min_width
        if min_height:
            params["min_height"] = min_height

        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            images = []

            for photo in data.get("photos", []):
                # Extract all available image sizes
                src = photo.get("src", {})
                image_data = {
                    "id": photo.get("id"),
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "alt": photo.get("alt", query),
                    "photographer": photo.get("photographer"),
                    "photographer_url": photo.get("photographer_url"),
                    "pexels_url": photo.get("url"),
                    # All available image sizes
                    "urls": {
                        "original": src.get("original"),
                        "large2x": src.get("large2x"),
                        "large": src.get("large"),
                        "medium": src.get("medium"),
                        "small": src.get("small"),
                        "portrait": src.get("portrait"),
                        "landscape": src.get("landscape"),
                        "tiny": src.get("tiny"),
                    },
                    # Quick access URLs (backward compatibility)
                    "url": src.get(size, src.get("large")),
                    "url_large": src.get("large"),
                    "url_medium": src.get("medium"),
                    "url_small": src.get("small"),
                    # Metadata
                    "avg_color": photo.get("avg_color"),
                    "type": "image",
                    "source": "pexels",
                }

                images.append(image_data)

            return images

        else:
            print(f"❌ Pexels Images API error: {response.status_code}")
            return get_fallback_images(query, per_page)

    except Exception as e:
        print(f"❌ Error fetching Pexels images: {e}")
        return get_fallback_images(query, per_page)


def fetch_pexels_videos(
    query: str,
    per_page: int,
    orientation: str,
    min_width: Optional[int],
    min_height: Optional[int],
    min_duration: Optional[int],
    max_duration: Optional[int],
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Fetch videos from Pexels API"""
    try:
        # Build video search parameters
        params = {
            "query": query,
            "per_page": min(per_page, 80),  # Pexels max limit
            "orientation": orientation,
        }

        # Add optional filters
        if min_width:
            params["min_width"] = min_width
        if min_height:
            params["min_height"] = min_height
        if min_duration:
            params["min_duration"] = min_duration
        if max_duration:
            params["max_duration"] = max_duration

        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            videos = []

            for video in data.get("videos", []):
                # Extract video file information
                video_files = video.get("video_files", [])
                video_urls = {}

                # Organize video files by quality
                for file in video_files:
                    quality = file.get("quality", "unknown")
                    file_type = file.get("file_type", "mp4")
                    width = file.get("width")
                    height = file.get("height")

                    video_urls[f"{quality}_{file_type}"] = {
                        "url": file.get("link"),
                        "width": width,
                        "height": height,
                        "file_type": file_type,
                        "quality": quality,
                        "size": file.get("size"),  # File size in bytes
                    }

                # Get video preview image
                video_pictures = video.get("video_pictures", [])
                preview_image = (
                    video_pictures[0].get("picture") if video_pictures else None
                )

                video_data = {
                    "id": video.get("id"),
                    "width": video.get("width"),
                    "height": video.get("height"),
                    "duration": video.get("duration"),  # Duration in seconds
                    "alt": f"{query} video",
                    "tags": video.get("tags", []),
                    "user": {
                        "name": video.get("user", {}).get("name"),
                        "url": video.get("user", {}).get("url"),
                    },
                    "pexels_url": video.get("url"),
                    # Video files organized by quality
                    "video_files": video_urls,
                    # Quick access to common qualities
                    "url_hd": next(
                        (f["url"] for f in video_files if f.get("quality") == "hd"),
                        None,
                    ),
                    "url_sd": next(
                        (f["url"] for f in video_files if f.get("quality") == "sd"),
                        None,
                    ),
                    "url_mobile": next(
                        (f["url"] for f in video_files if f.get("width", 0) <= 640),
                        None,
                    ),
                    # Preview and metadata
                    "preview_image": preview_image,
                    "video_pictures": video_pictures,
                    "type": "video",
                    "source": "pexels",
                }

                videos.append(video_data)

            return videos

        else:
            print(f"❌ Pexels Videos API error: {response.status_code}")
            return get_fallback_videos(query, per_page)

    except Exception as e:
        print(f"❌ Error fetching Pexels videos: {e}")
        return get_fallback_videos(query, per_page)


def get_curated_pexels_media(
    media_type: Literal["images", "videos", "both"] = "images", per_page: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch curated (trending) media from Pexels

    Args:
        media_type: Type of media to fetch
        per_page: Number of results per media type

    Returns:
        Dictionary with curated media data
    """
    try:
        pexels_api_key = settings.PEXELS_API_KEY
        if not pexels_api_key:
            return get_fallback_media("trending", media_type)

        headers = {"Authorization": pexels_api_key}
        results = {"images": [], "videos": []}

        # Fetch curated images
        if media_type in ["images", "both"]:
            try:
                response = requests.get(
                    "https://api.pexels.com/v1/curated",
                    headers=headers,
                    params={"per_page": per_page},
                    timeout=15,
                )

                if response.status_code == 200:
                    data = response.json()
                    for photo in data.get("photos", []):
                        src = photo.get("src", {})
                        results["images"].append(
                            {
                                "id": photo.get("id"),
                                "width": photo.get("width"),
                                "height": photo.get("height"),
                                "alt": photo.get("alt", "Curated image"),
                                "photographer": photo.get("photographer"),
                                "url": src.get("large"),
                                "url_medium": src.get("medium"),
                                "url_small": src.get("small"),
                                "type": "image",
                                "source": "pexels_curated",
                            }
                        )
            except Exception as e:
                print(f"Error fetching curated images: {e}")

        # Fetch popular videos
        if media_type in ["videos", "both"]:
            try:
                response = requests.get(
                    "https://api.pexels.com/videos/popular",
                    headers=headers,
                    params={"per_page": per_page},
                    timeout=15,
                )

                if response.status_code == 200:
                    data = response.json()
                    for video in data.get("videos", []):
                        video_files = video.get("video_files", [])
                        hd_file = next(
                            (f for f in video_files if f.get("quality") == "hd"),
                            video_files[0] if video_files else {},
                        )

                        results["videos"].append(
                            {
                                "id": video.get("id"),
                                "width": video.get("width"),
                                "height": video.get("height"),
                                "duration": video.get("duration"),
                                "alt": "Popular video",
                                "url_hd": hd_file.get("link"),
                                "preview_image": video.get("video_pictures", [{}])[
                                    0
                                ].get("picture"),
                                "user": video.get("user", {}),
                                "type": "video",
                                "source": "pexels_popular",
                            }
                        )
            except Exception as e:
                print(f"Error fetching popular videos: {e}")

        return results

    except Exception as e:
        print(f"Error fetching curated media: {e}")
        return get_fallback_media("curated", media_type)


def get_pexels_collections(
    collection_id: str, media_type: str = "photos"
) -> List[Dict[str, Any]]:
    """
    Fetch media from a specific Pexels collection

    Args:
        collection_id: Pexels collection ID
        media_type: "photos" or "videos"

    Returns:
        List of media items from the collection
    """
    try:
        pexels_api_key = settings.PEXELS_API_KEY
        if not pexels_api_key:
            return []

        headers = {"Authorization": pexels_api_key}
        endpoint = f"https://api.pexels.com/v1/collections/{collection_id}"

        response = requests.get(endpoint, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            media_items = []

            for item in data.get("media", []):
                if item.get("type") == "Photo" and media_type == "photos":
                    src = item.get("src", {})
                    media_items.append(
                        {
                            "id": item.get("id"),
                            "url": src.get("large"),
                            "photographer": item.get("photographer"),
                            "type": "image",
                            "source": "pexels_collection",
                        }
                    )
                elif item.get("type") == "Video" and media_type == "videos":
                    video_files = item.get("video_files", [])
                    hd_file = next(
                        (f for f in video_files if f.get("quality") == "hd"),
                        video_files[0] if video_files else {},
                    )

                    media_items.append(
                        {
                            "id": item.get("id"),
                            "url_hd": hd_file.get("link"),
                            "duration": item.get("duration"),
                            "user": item.get("user", {}),
                            "type": "video",
                            "source": "pexels_collection",
                        }
                    )

            return media_items

    except Exception as e:
        print(f"Error fetching collection {collection_id}: {e}")
        return []


def get_fallback_media(query: str, media_type: str) -> Dict[str, List[Dict[str, Any]]]:
    """Comprehensive fallback media when Pexels API fails"""
    results = {"images": [], "videos": []}

    if media_type in ["images", "both"]:
        results["images"] = get_fallback_images(query, 5)

    if media_type in ["videos", "both"]:
        results["videos"] = get_fallback_videos(query, 5)

    return results


def get_fallback_images(query: str, count: int = 5) -> List[Dict[str, Any]]:
    """Enhanced fallback images with more variety"""
    fallback_collections = {
        "business": [
            {
                "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
                "alt": "Modern business building skyline",
                "photographer": "Unsplash Contributors",
            },
            {
                "url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
                "alt": "Business team collaboration meeting",
                "photographer": "Unsplash Contributors",
            },
            {
                "url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&auto=format&fit=crop&w=2126&q=80",
                "alt": "Professional workspace setup",
                "photographer": "Unsplash Contributors",
            },
        ],
        "technology": [
            {
                "url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=2125&q=80",
                "alt": "Technology and innovation concept",
                "photographer": "Unsplash Contributors",
            },
            {
                "url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
                "alt": "AI and digital transformation",
                "photographer": "Unsplash Contributors",
            },
        ],
        "workflow": [
            {
                "url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
                "alt": "Team workflow and productivity",
                "photographer": "Unsplash Contributors",
            },
        ],
        "success": [
            {
                "url": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80",
                "alt": "Success and achievement concept",
                "photographer": "Unsplash Contributors",
            },
        ],
    }

    # Match query to appropriate category
    query_lower = query.lower()

    if any(
        word in query_lower for word in ["business", "team", "professional", "office"]
    ):
        selected_images = fallback_collections["business"]
    elif any(
        word in query_lower
        for word in ["tech", "software", "ai", "digital", "innovation"]
    ):
        selected_images = fallback_collections["technology"]
    elif any(word in query_lower for word in ["workflow", "productivity", "process"]):
        selected_images = fallback_collections["workflow"]
    elif any(word in query_lower for word in ["success", "growth", "achievement"]):
        selected_images = fallback_collections["success"]
    else:
        # Mix from all categories
        all_images = []
        for images in fallback_collections.values():
            all_images.extend(images)
        selected_images = all_images

    # Add required fields for compatibility
    enhanced_images = []
    for i, img in enumerate(selected_images[:count]):
        enhanced_images.append(
            {
                **img,
                "id": f"fallback_{i}",
                "width": 2070,
                "height": 1380,
                "photographer_url": "https://unsplash.com",
                "type": "image",
                "source": "fallback_unsplash",
            }
        )

    return enhanced_images


def get_fallback_videos(query: str, count: int = 5) -> List[Dict[str, Any]]:
    """Fallback videos from various sources"""
    fallback_videos = [
        {
            "id": "fallback_video_1",
            "alt": f"{query} - business concept video",
            "url_hd": "https://player.vimeo.com/external/392479206.hd.mp4?s=b0a652ae5b88d3c9b5b5e5e5e1e1e1e1&profile_id=175",
            "duration": 30,
            "width": 1920,
            "height": 1080,
            "preview_image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "type": "video",
            "source": "fallback_vimeo",
            "user": {"name": "Stock Video Creator", "url": ""},
        },
        {
            "id": "fallback_video_2",
            "alt": f"{query} - technology animation",
            "url_hd": "https://player.vimeo.com/external/387563832.hd.mp4?s=a0a652ae5b88d3c9b5b5e5e5e1e1e1e1&profile_id=175",
            "duration": 25,
            "width": 1920,
            "height": 1080,
            "preview_image": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
            "type": "video",
            "source": "fallback_vimeo",
            "user": {"name": "Tech Video Creator", "url": ""},
        },
    ]

    return fallback_videos[:count]


# Enhanced legacy function for backward compatibility
def get_pexels_images(query: str, per_page: int = 3) -> List[Dict[str, str]]:
    """
    Legacy function for backward compatibility
    Enhanced to use the new comprehensive fetcher
    """
    result = get_pexels_media(query, "images", per_page)
    images = result.get("images", [])

    # Convert to legacy format
    legacy_format = []
    for img in images:
        legacy_format.append(
            {
                "url": img.get("url", img.get("url_large", "")),
                "url_medium": img.get("url_medium", ""),
                "url_small": img.get("url_small", ""),
                "alt": img.get("alt", query),
                "photographer": img.get("photographer", "Unknown"),
                "photographer_url": img.get("photographer_url", ""),
            }
        )

    return legacy_format


# Usage examples and testing function
def test_pexels_integration():
    """Test the Pexels integration with various queries"""
    print("🧪 Testing Pexels Integration...")

    # Test 1: Images only
    print("\n1. Testing image search...")
    images_result = get_pexels_media("business meeting", "images", 3)
    print(f"Images found: {len(images_result.get('images', []))}")

    # Test 2: Videos only
    print("\n2. Testing video search...")
    videos_result = get_pexels_media("technology", "videos", 2)
    print(f"Videos found: {len(videos_result.get('videos', []))}")

    # Test 3: Both images and videos
    print("\n3. Testing combined media search...")
    both_result = get_pexels_media("startup team", "both", 2)
    print(
        f"Images: {len(both_result.get('images', []))}, Videos: {len(both_result.get('videos', []))}"
    )

    # Test 4: Curated content
    print("\n4. Testing curated content...")
    curated = get_curated_pexels_media("both", 2)
    print(
        f"Curated - Images: {len(curated.get('images', []))}, Videos: {len(curated.get('videos', []))}"
    )

    print("\n✅ Pexels integration testing complete!")


if __name__ == "__main__":
    test_pexels_integration()
