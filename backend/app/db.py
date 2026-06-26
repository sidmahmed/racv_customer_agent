import os
import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

if os.environ.get("VERCEL"):
    # Vercel's deployed filesystem is read-only outside /tmp, and /tmp is
    # ephemeral per cold start -- chat history only persists within a warm
    # instance's lifetime in production. Acceptable for this PoC.
    DB_PATH = Path("/tmp/chat_history.db")
else:
    DB_PATH = Path(__file__).resolve().parent.parent / "chat_history.db"

_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(_connection)
