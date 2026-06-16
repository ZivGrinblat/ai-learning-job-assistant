"""
Open Library integration — similar book titles for the notes shop zone.

Returns list of dicts matching SimilarBook schema.
Network errors propagate to the route (no retry layer yet).
"""

import httpx

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
UNKNOWN_AUTHOR = "Unknown"
UNKNOWN_TITLE = "Unknown"


def _to_similar_book(doc: dict) -> dict[str, str]:
    """Map one Open Library document into SimilarBook-compatible shape."""
    author_names = doc.get("author_name") or []
    return {
        "title": doc.get("title", UNKNOWN_TITLE),
        "author": author_names[0] if author_names else UNKNOWN_AUTHOR,
    }


def find_similar_books(book_title: str, limit: int = 5) -> list[dict]:
    """Fetch similar books from Open Library and return title/author pairs."""
    response = httpx.get(
        OPEN_LIBRARY_SEARCH_URL,
        params={"q": book_title, "limit": limit},
    )

    response.raise_for_status()
    docs = response.json().get("docs", [])

    return [_to_similar_book(doc) for doc in docs]
