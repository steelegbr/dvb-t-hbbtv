from datetime import datetime
from fastapi import APIRouter, Header, Request, status
from fastapi.encoders import jsonable_encoder
from models import LogEntry, LogEntryPost, Session
from pymongo import ASCENDING, DESCENDING
from typing import List, Union
from uuid import UUID

LOG_COLLECTION = "logs"

log_router = APIRouter()


@log_router.post(
    "/{session}",
    response_description="Creates a new log entry",
    response_model=LogEntry,
)
async def create_log_entry(
    entry: LogEntryPost,
    request: Request,
    session: UUID,
    user_agent: Union[str, None] = Header(default=None),
):
    now = datetime.utcnow()
    log_entry = jsonable_encoder(
        {
            **entry.dict(),
            "user_agent": user_agent,
            "timestamp": now.isoformat(),
            "session": session,
        }
    )
    new_log_entry = request.app.database[LOG_COLLECTION].insert_one(log_entry)

    return request.app.database[LOG_COLLECTION].find_one(
        {"_id": new_log_entry.inserted_id}
    )


@log_router.get(
    "/", response_description="Lists all the log sessions", response_model=List[Session]
)
async def get_sessions(request: Request):
    session_ids = list(request.app.database[LOG_COLLECTION].distinct("session"))
    return [
        Session(
            id=session_id,
            start=request.app.database[LOG_COLLECTION].find_one(
                {"session": session_id}, sort=[("timestamp", ASCENDING)]
            )["timestamp"],
            end=request.app.database[LOG_COLLECTION].find_one(
                {"session": session_id}, sort=[("timestamp", DESCENDING)]
            )["timestamp"],
            user_agent=request.app.database[LOG_COLLECTION].find_one(
                {"session": session_id}, sort=[("timestamp", ASCENDING)]
            )["user_agent"],
        )
        for session_id in session_ids
    ]


@log_router.get(
    "/{session}",
    response_description="Lists all the log entries for a session",
    response_model=List[LogEntry],
)
async def get_log_entries(session: UUID, request: Request):
    return [
        LogEntry.parse_obj(entry)
        for entry in request.app.database[LOG_COLLECTION].find(
            {"session": str(session)}, sort=[("timestamp", ASCENDING)]
        )
    ]
