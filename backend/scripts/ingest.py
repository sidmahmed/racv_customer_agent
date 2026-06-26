"""One-time/developer-run ingestion: fetch RACV help-center pages, chunk by
heading, embed, and upsert into Supabase.

Run manually via (from backend/):
    uv sync --group ingest
    uv run python -m scripts.ingest

Not part of the deployed runtime -- requires backend/supabase/schema.sql to
have already been run against the target Supabase project.
"""

import re

import httpx
from bs4 import BeautifulSoup
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import HTMLHeaderTextSplitter

from app.config import settings
from app.supabase_client import get_supabase

URLS = [
    "https://www.racv.com.au/help-and-support.html",
    "https://www.racv.com.au/help-and-support/account-membership.html",
    "https://www.racv.com.au/help-and-support/billing-payments.html",
    "https://www.racv.com.au/help-and-support/emergency-roadside-assistance.html",
    "https://www.racv.com.au/help-and-support/car-insurance.html",
    "https://www.racv.com.au/help-and-support/home-insurance.html",
    "https://www.racv.com.au/help-and-support/financial-hardship.html",
    "https://www.racv.com.au/help-and-support/home-security.html",
    "https://www.racv.com.au/help-and-support/home-electrification.html",
    "https://www.racv.com.au/help-and-support/trades.html",
    "https://www.racv.com.au/help-and-support/holidays.html",
]

HEADERS_TO_SPLIT_ON = [("h1", "h1"), ("h2", "h2"), ("h3", "h3")]

# Recurring "was this helpful" accordion widget chrome on every FAQ answer --
# pure UI noise, not content, repeated dozens of times per page.
FEEDBACK_WIDGET_RE = re.compile(
    r"Did this answer your question\?\s*Yes\s*No\s*(?:Thank you for your feedback\s*)+"
)


def category_from_url(url: str) -> str:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return slug.removesuffix(".html")


def fetch_main_html(url: str) -> str:
    resp = httpx.get(
        url, timeout=30, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    main = soup.select_one("#main")
    if main is None:
        raise RuntimeError(f"No #main element found at {url}")
    return str(main)


def chunk(html: str) -> list[dict]:
    """Split HTML by heading, then merge consecutive pieces that share the
    same heading path (HTMLHeaderTextSplitter emits a heading's own text and
    its following body text as separate documents -- e.g. an FAQ question and
    its answer come out as two disconnected chunks otherwise) and drop
    "bare" chunks that are nothing but a heading label with no body text
    merged in (e.g. an H1/H2 with no leading prose before the next header).
    """
    splitter = HTMLHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
    docs = splitter.split_text(html)

    merged: list[dict] = []
    for d in docs:
        text = FEEDBACK_WIDGET_RE.sub(" ", d.page_content)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        heading_path = " > ".join(v for k, v in d.metadata.items() if k in ("h1", "h2", "h3"))
        if merged and merged[-1]["heading_path"] == heading_path:
            merged[-1]["content"] += " " + text
        else:
            merged.append({"content": text, "heading_path": heading_path})

    return [m for m in merged if m["content"] != m["heading_path"].rsplit(" > ", 1)[-1]]


def run() -> None:
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model, api_key=settings.openai_api_key
    )
    supabase = get_supabase()
    supabase.table("documents").delete().neq("id", 0).execute()  # full re-ingest

    rows = []
    for url in URLS:
        category = category_from_url(url)
        for c in chunk(fetch_main_html(url)):
            rows.append({**c, "source_url": url, "category": category})

    vectors = embeddings.embed_documents([r["content"] for r in rows])
    for row, vec in zip(rows, vectors, strict=True):
        row["embedding"] = vec

    batch_size = 50
    for i in range(0, len(rows), batch_size):
        supabase.table("documents").insert(rows[i : i + batch_size]).execute()

    print(f"Ingested {len(rows)} chunks from {len(URLS)} pages.")


if __name__ == "__main__":
    run()
