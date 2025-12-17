from pydantic import BaseModel, Field
from typing import List, Literal, Optional

Author = Literal["human", "ai"]

class Turn(BaseModel):
    story_id: str
    turn: int
    author: Author
    text: str
    flow_score: float = 0.0
    entropy_score: float = 0.0

class CreateStoryResp(BaseModel):
    story_id: str

class ContinueReq(BaseModel):
    story_id: str
    user_text: str = Field(min_length=1)
    rounds: int = Field(default=1, ge=1, le=10)
    mode: str = "human_ai"  # human_ai / ai_only / human_only

class ContinueResp(BaseModel):
    story_id: str
    new_turns: List[Turn]

class StoryResp(BaseModel):
    story_id: str
    turns: List[Turn]

class CompareResp(BaseModel):
    story_id: str
    points: List[Turn]  # 这里直接复用 Turn，前端散点图能用
