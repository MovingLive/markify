from urllib.parse import urlparse, urljoin, urldefrag
from typing import Tuple

def normalize_url(url: str) -> str:
    """Normalize URL by removing fragment and trailing slash."""
    url, _ = urldefrag(url)
    if url.endswith("/"):
        url = url[:-1]
    return url

def get_base_info(url: str) -> Tuple[str, str]:
    """Extract base URL and path from URL."""
    parsed = urlparse(url)
    return (
        parsed.netloc,
        parsed.path.split('/')[1] if parsed.path else ''
    )

def is_valid_next_url(next_url: str, base_url: str, base_path: str) -> bool:
    """Check if URL is valid for crawling."""
    try:
        parsed = urlparse(next_url)
        return parsed.netloc == base_url and parsed.path.startswith(f"/{base_path}")
    except:
        return False