from pydantic import BaseModel


class EventFeedItem(BaseModel):
    event_id: str
    event_type: str
    message: str
    created_at: str
