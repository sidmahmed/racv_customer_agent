from app.routes import chat


def test_stream_message(client, monkeypatch):
    monkeypatch.setattr(
        chat, "stream_agent", lambda session_id, message: iter(["echo", ": ", message])
    )

    res = client.post("/chat/stream", json={"session_id": "abc", "message": "hi"})

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/event-stream")
    assert res.text == (
        'data: {"content": "echo"}\n\n'
        'data: {"content": ": "}\n\n'
        'data: {"content": "hi"}\n\n'
        "event: done\ndata: {}\n\n"
    )


def test_send_message(client, monkeypatch):
    monkeypatch.setattr(chat, "run_agent", lambda session_id, message: f"echo: {message}")

    res = client.post("/chat", json={"session_id": "abc", "message": "hi"})

    assert res.status_code == 200
    assert res.json() == {"session_id": "abc", "response": "echo: hi"}


def test_get_history(client, monkeypatch):
    monkeypatch.setattr(
        chat,
        "get_history",
        lambda session_id: [{"role": "human", "content": "hi"}],
    )

    res = client.get("/chat/abc/history")

    assert res.status_code == 200
    assert res.json() == {
        "session_id": "abc",
        "messages": [{"role": "human", "content": "hi"}],
    }
