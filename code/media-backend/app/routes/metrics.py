from fastapi import APIRouter
from app.models.schemas import CompareResp
from app.services.storage import get_story_turns

router = APIRouter()

@router.get("/compare", response_model=CompareResp)
def api_compare(story_id: str):
    """
    简化版 compare：直接返回这个 story 的所有 turns。
    前端会用 turns 里的 flow/entropy/author 画散点图。
    后续你们可以扩展：返回 human 组 vs ai 组两套数据。
    """
    turns = get_story_turns(story_id)
    return {"story_id": story_id, "points": turns}
