from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class SessionBuffer:
    session_id: str
    turns: deque[Turn] = field(default_factory=lambda: deque(maxlen=40))
    lock: Lock = field(default_factory=Lock)


class WorkingMemoryStore:
    """Thread-safe in-memory conversation buffers per session."""

    def __init__(self, max_turns: int = 40) -> None:
        self._max_turns = max_turns
        self._sessions: dict[str, SessionBuffer] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str | None) -> str:
        sid = session_id or str(uuid4())
        with self._lock:
            if sid not in self._sessions:
                buf = SessionBuffer(session_id=sid, turns=deque(maxlen=self._max_turns))
                self._sessions[sid] = buf
            return sid

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            buf = self._sessions.setdefault(
                session_id, SessionBuffer(session_id=session_id, turns=deque(maxlen=self._max_turns))
            )
        with buf.lock:
            buf.turns.append(Turn(role=role, content=content))

    def transcript(self, session_id: str) -> list[dict[str, str]]:
        with self._lock:
            buf = self._sessions.get(session_id)
        if not buf:
            return []
        with buf.lock:
            return [{"role": t.role, "content": t.content} for t in buf.turns]
