from collections.abc import Iterator
from functools import lru_cache

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.config import settings
from app.db import checkpointer
from app.tools import TOOLS

SYSTEM_PROMPT = (
    "You are RACV's member support assistant. You answer questions about RACV "
    "products and services using ONLY information returned by the "
    "search_help_center tool. Never invent or guess policy, pricing, eligibility, "
    "or operational details.\n\n"
    "Rules:\n"
    "1. For any question about RACV policies, products, claims, eligibility, or "
    "procedures, call search_help_center first. Base your answer strictly on the "
    "returned passages.\n"
    "2. Always cite the source URL(s) you used as markdown links, e.g. "
    "[Car Insurance FAQs](https://www.racv.com.au/help-and-support/car-insurance.html).\n"
    "3. If search_help_center returns nothing relevant, say you don't have that "
    "information in RACV's Help & Support content and suggest the member contact "
    "RACV directly -- do not guess.\n"
    "4. For pricing questions, call get_pricing and clearly label any figures as "
    "illustrative demo data, not official RACV pricing.\n"
    "5. If a question is ambiguous, ask a clarifying question rather than assuming."
)


@lru_cache
def get_agent():
    model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


def run_agent(session_id: str, message: str) -> str:
    agent = get_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return result["messages"][-1].content


def stream_agent(session_id: str, message: str) -> Iterator[str]:
    agent = get_agent()
    for event in agent.stream_events(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": session_id}},
        version="v3",
    ):
        if event.get("method") != "messages":
            continue
        payload, _metadata = event["params"]["data"]
        if payload.get("event") != "content-block-delta":
            continue
        delta = payload.get("delta", {})
        if delta.get("type") == "text-delta":
            yield delta["text"]


def get_history(session_id: str) -> list[dict[str, str]]:
    agent = get_agent()
    state = agent.get_state(config={"configurable": {"thread_id": session_id}})
    messages = state.values.get("messages", []) if state.values else []
    return [{"role": m.type, "content": m.content} for m in messages]
