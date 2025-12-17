from typing import Dict, List

def _clamp01(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x

def score_turns(story_id: str, turns: List[Dict]) -> List[Dict]:
    """
    MVP版打分：
    - flow_score：按文本长度归一化（只是占位，后续可替换成 embedding 余弦相似度）
    - entropy_score：按不同字符比例做一个“新颖度”占位
    """
    scored = []
    for t in turns:
        text = (t.get("text") or "").strip()
        if not text:
            flow = 0.0
            entropy = 0.0
        else:
            flow = _clamp01(len(text) / 80.0)
            entropy = _clamp01(len(set(text)) / 50.0)

        t2 = dict(t)
        t2["flow_score"] = float(flow)
        t2["entropy_score"] = float(entropy)
        scored.append(t2)
    return scored
