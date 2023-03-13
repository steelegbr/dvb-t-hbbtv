from enum import Enum
from pydantic import BaseModel
from uuid import UUID


class LogLevelEnum(str, Enum):
    info = "Info"
    error = "Error"
    debug = "Debug"


class LogEntryPost(BaseModel):
    level: LogLevelEnum
    entry: str


class LogEntry(LogEntryPost):
    timestamp: str
    user_agent: str


class Session(BaseModel):
    id: UUID
    start: str
    end: str
    user_agent: str
