import json
import os
import uuid
from typing import Any, Dict, List

from app.core.config import settings

def _ensure_data_file():
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    if not os.path.exists(settings.STORIES_PATH):
        with open(settings.STORIES_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

def _load_db() -> Dict[str, List[Dict[str, Any]]]:
    _ensure_data_file()
    with open(settings.STORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_db(db: Dict[str, List[Dict[str, Any]]]) -> None:
    _ensure_data_file()
    with open(settings.STORIES_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def create_story() -> str:
    db = _load_db()
    story_id = str(uuid.uuid4())[:8]
    db[story_id] = []
    _save_db(db)
    return story_id

def get_story_turns(story_id: str) -> List[Dict[str, Any]]:
    db = _load_db()
    return db.get(story_id, [])

def append_turns(story_id: str, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    db = _load_db()
    cur = db.get(story_id, [])
    start_turn = len(cur)

    saved = []
    for i, t in enumerate(turns):
        # 统一分配 turn 序号（从 1 开始）
        t2 = dict(t)
        t2["story_id"] = story_id
        t2["turn"] = start_turn + i + 1
        saved.append(t2)
        cur.append(t2)

    db[story_id] = cur
    _save_db(db)
    return saved
