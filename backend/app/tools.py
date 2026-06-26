from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.supabase_client import get_supabase

CATEGORIES = [
    "help-and-support",
    "account-membership",
    "billing-payments",
    "emergency-roadside-assistance",
    "car-insurance",
    "home-insurance",
    "financial-hardship",
    "home-security",
    "home-electrification",
    "trades",
    "holidays",
]


def _embed(text: str) -> list[float]:
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model, api_key=settings.openai_api_key
    )
    return embeddings.embed_query(text)


@tool
def search_help_center(query: str, category: str | None = None) -> str:
    """Search RACV's official Help & Support content for information to answer
    a member's question. ALWAYS call this before answering any question about
    RACV policies, pricing, eligibility, claims, or operational procedures --
    never answer from general knowledge.

    Args:
        query: The member's question or topic, in natural language.
        category: Optional filter to narrow the search to one help-center
            section. One of: help-and-support, account-membership,
            billing-payments, emergency-roadside-assistance, car-insurance,
            home-insurance, financial-hardship, home-security,
            home-electrification, trades, holidays. Leave unset to search
            across all sections.

    Returns:
        Matching passages, each with its source URL and heading, to ground
        your answer and cite as a markdown link.
    """
    embedding = _embed(query)
    supabase = get_supabase()
    result = supabase.rpc(
        "hybrid_search",
        {
            "query_text": query,
            "query_embedding": embedding,
            "match_count": settings.rrf_match_count,
            "rrf_k": settings.rrf_k,
            "filter_category": category,
        },
    ).execute()
    # A result's RRF score only exceeds the max single-source contribution
    # (1/(rrf_k+1), i.e. ranking #1 in just one of full-text/semantic search)
    # when both search methods corroborate it. Below that ceiling, a result
    # is just "most similar of a bad lot" -- not a genuine match -- so drop
    # it rather than feed the agent a plausible-looking but irrelevant chunk.
    min_score = 1.0 / (settings.rrf_k + 1)
    rows = [r for r in (result.data or []) if r["rrf_score"] > min_score]
    if not rows:
        return "No matching content found in the RACV Help & Support pages."
    return "\n\n---\n\n".join(
        f"Source: {r['source_url']}\nSection: {r['heading_path']}\n\n{r['content']}" for r in rows
    )


@tool
def get_pricing(product_query: str, category: str | None = None) -> str:
    """Look up illustrative/demo pricing for an RACV product or service.
    Returns MOCK data for this proof-of-concept -- always tell the user the
    figures are illustrative demo data, not live RACV pricing (RACV's real
    pricing is quote-based and not published).

    Args:
        product_query: Product/plan name or keyword, e.g. "roadside basic"
            or "car insurance excess".
        category: Optional category filter, e.g. "car-insurance",
            "home-insurance", "emergency-roadside-assistance".
    """
    supabase = get_supabase()
    query = supabase.table("pricing").select("*").ilike("product_name", f"%{product_query}%")
    if category:
        query = query.eq("category", category)
    rows = query.execute().data
    if not rows:
        return "No demo pricing data found for that product."
    return "\n".join(
        f"{r['product_name']} ({r['category']}): {r['price_description']} "
        f"[illustrative demo data, not official RACV pricing]"
        for r in rows
    )


TOOLS = [search_help_center, get_pricing]
