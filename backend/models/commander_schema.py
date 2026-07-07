from pydantic import BaseModel
from typing import List


class CommanderResponse(BaseModel):
    priority: str
    summary: str
    actions: List[str]