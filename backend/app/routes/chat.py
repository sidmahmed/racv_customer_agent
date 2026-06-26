import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent import get_history, run_agent, stream_agent
from app.models import ChatHistoryResponse, ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def send_message(payload: ChatRequest) -> ChatResponse:
    response = run_agent(payload.session_id, payload.message)
    return ChatResponse(session_id=payload.session_id, response=response)


@router.post("/stream")
def stream_message(payload: ChatRequest) -> StreamingResponse:
    def event_stream():
        for token in stream_agent(payload.session_id, payload.message):
            yield f"data: {json.dumps({'content': token})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str) -> ChatHistoryResponse:
    return ChatHistoryResponse(session_id=session_id, messages=get_history(session_id))
