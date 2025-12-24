from fastapi import APIRouter, HTTPException
from app.models.schemas import CreateStoryResp, ContinueReq, ContinueResp, StoryResp
from app.services.storage import create_story, get_story_turns, append_turns
from app.services.llm_proxy import generate_ai_turns
from app.services.scoring import score_turns

router = APIRouter()

@router.post("/create", response_model=CreateStoryResp)
def api_create_story():
    sid = create_story()
    return {"story_id": sid}

@router.get("/static-data")
def api_get_static_data():
    """
    提供生成的全量可视化数据 (data/story/web_visualization_data.json)
    用于前端展示"语义河流图"历史存档
    """
    import os
    import json
    
    # 路径：根据部署环境可能不同，这里以本地开发相对路径为例
    # 假设后端运行在 media-backend, 数据在 data/story
    # 尝试多个可能的路径
    possible_paths = [
        # 1. 之前生成的路径 (最准)
        r'd:\STUDY\SchoolLearning\level3\Interactive_media_technology\lab\data\story\web_visualization_data.json',
        # 2. 相对路径
        '../../../../data/story/web_visualization_data.json'
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading json: {e}")
                
    return {"error": "Static data not found", "paths_tried": possible_paths}

@router.get("/{story_id}", response_model=StoryResp)
def api_get_story(story_id: str):
    turns = get_story_turns(story_id)
    if turns is None:
        raise HTTPException(status_code=404, detail="story not found")
    return {"story_id": story_id, "turns": turns}

@router.post("/continue", response_model=ContinueResp)
def api_continue(req: ContinueReq):
    # 1) 先把用户输入作为一个 turn（human）
    base_turns = [{
        "author": "human",
        "text": req.user_text
    }]

    # 2) 生成 AI turns（mock/真实LLM都从 llm_proxy 来）
    ai_turns = generate_ai_turns(req.story_id, req.user_text, req.rounds, req.mode)

    # 3) 合并并打分
    all_new = base_turns + ai_turns
    scored = score_turns(req.story_id, all_new)

    # 4) 存储并给 turn 编号
    saved = append_turns(req.story_id, scored)

    return {"story_id": req.story_id, "new_turns": saved}
