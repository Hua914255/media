from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.scoring import score_turns
from app.services.storage import append_turns
from app.services.llm_proxy import stream_ai_turns

router = APIRouter()

@router.websocket("/ws/story/{story_id}")
async def ws_story(websocket: WebSocket, story_id: str):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            user_text = (payload.get("user_text") or "").strip()
            rounds = int(payload.get("rounds") or 1)
            mode = payload.get("mode") or "human_ai"

            # 1) 先把 human turn 推给前端（也存库）
            human_turn = {"author": "human", "text": user_text}
            scored_human = score_turns(story_id, [human_turn])
            saved_human = append_turns(story_id, scored_human)
            # append_turns 返回 list
            await websocket.send_json(saved_human[0])

            # 2) 再流式推 AI turns（每条：打分->存库->推给前端）
            async for ai_turn in stream_ai_turns(story_id, user_text, rounds, mode):
                scored_ai = score_turns(story_id, [ai_turn])
                saved_ai = append_turns(story_id, scored_ai)
                await websocket.send_json(saved_ai[0])

    except WebSocketDisconnect:
        return
    except Exception:
        # 防止前端连接断了导致后端爆炸
        try:
            await websocket.close()
        except Exception:
            pass
