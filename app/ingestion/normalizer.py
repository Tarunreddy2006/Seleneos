import re
import hashlib
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from bs4 import BeautifulSoup

# Tracking parameters to strip for canonical URL normalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "fb_action_ids", "fb_action_types",
    "action_object_map", "action_type_map", "action_ref_map",
    "ncid", "cps", "ito", "mkt_tok", "_ga", "_gl"
}


def canonicalize_url(raw_url: str) -> str:
    """
    Normalizes a URL by:
    1. Lowercasing the scheme and host.
    2. Stripping tracking parameters (UTM, Facebook, Google click IDs).
    3. Sorting remaining query parameters deterministically.
    4. Removing fragments and trailing slashes from the path.
    """
    if not raw_url:
        return ""

    parsed = urlparse(raw_url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove standard port if default
    if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
        netloc = netloc.rsplit(":", 1)[0]

    # Clean path (strip redundant trailing slashes, except root '/')
    path = parsed.path
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    # Strip tracking parameters and sort remaining
    clean_params = []
    if parsed.query:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        clean_params = sorted([(k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS])

    new_query = urlencode(clean_params)

    # Omit fragment completely
    return urlunparse((scheme, netloc, path, parsed.params, new_query, ""))


def clean_html_text(raw_html: str) -> str:
    """
    Safely strips HTML tags, script/style content, and normalizes whitespace.
    Uses Python's built-in html.parser (100% binary-free for Termux portability).
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove scripts, styles, iframes
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Normalize multiple whitespace, tabs, and newlines
    clean = re.sub(r"\s+", " ", text).strip()
    return clean


def generate_content_hash(text: str) -> str:
    """Generates a deterministic SHA-256 hash for exact deduplication."""
    if not text:
        return ""
    normalized = re.sub(r"\W+", "", text.lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
