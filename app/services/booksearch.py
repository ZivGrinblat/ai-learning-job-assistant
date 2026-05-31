"""
Open Library integration — similar book titles for the notes shop zone.

Returns list of dicts matching SimilarBook schema.
Network errors propagate to the route (no retry layer yet).
"""

import httpx


def find_similar_books(book_title: str, limit: int = 5) -> list[dict]:
    response = httpx.get(
        "https://openlibrary.org/search.json",
        params={"q": book_title, "limit": limit},
    )

    response.raise_for_status()
    docs = response.json().get("docs", [])

    results = []
    for doc in docs:
        author = doc.get("author_name") or []
        results.append(
            {
                "title": doc.get("title", "Unknown"),
                "author": author[0] if author else "Unknown",
            }
        )

    return results
