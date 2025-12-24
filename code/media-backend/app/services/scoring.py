from typing import Dict, List
from app.utils import algo
from app.services.storage import get_story_turns

def _clamp01(x: float) -> float:
    if x < 0: return 0.0
    if x > 1: return 1.0
    return x

def score_turns(story_id: str, new_turns: List[Dict]) -> List[Dict]:
    """
    使用 algo.py 计算真实的 Flow & Entropy
    """
    # 1. 获取该故事的所有历史 turns (为了拿到上下文向量)
    history_turns = get_story_turns(story_id) or []
    
    # 提取所有历史的 embedding (如果有的话)
    context_vectors = []
    for t in history_turns:
        if t.get("embedding"):
            context_vectors.append(t["embedding"])
    
    scored_result = []
    
    # 2. 逐条计算新生成的 turn
    for t in new_turns:
        text = (t.get("text") or "").strip()
        
        # 调用核心算法
        # 注意：这里我们传入当前的 context_vectors，
        # 算完一条后，要把这一条的 embedding 加进去，作为下一条的 context
        metrics = algo.calculate_metrics(text, context_vectors)
        print(f"🐛 [DEBUG] Text: {text[:10]}... | Metrics: {metrics.keys()} | X: {metrics.get('x')} | Y: {metrics.get('y')}")
        
        # 组装结果
        t2 = dict(t)
        t2["flow_score"] = metrics["flow_score"]
        t2["entropy_score"] = metrics["entropy_score"]
        t2["embedding"] = metrics["embedding"] # 存库
        # 新增可视化坐标
        t2["x"] = metrics.get("x", 0.0)
        t2["y"] = metrics.get("y", 0.0)
        
        # 将当前向量加入上下文，供下一轮循环使用 (如果是批量生成多条的情况)
        if metrics["embedding"]:
            context_vectors.append(metrics["embedding"])
            
        scored_result.append(t2)
        
    return scored_result
