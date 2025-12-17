import os
import re
import asyncio
from typing import AsyncGenerator, Dict, List, Tuple

import httpx

# 读取历史故事
from app.services.storage import get_story_turns


# ====== Config ======
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-51a5d4b499924058a41423e7634468ec")  # ✅ 不要写死在代码里
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # 或 deepseek-reasoner


# ====== Mock ======
def _mock_turns(user_text: str, rounds: int) -> List[Dict]:
    return [
        {"author": "ai", "text": f"（mock AI）基于：{user_text} 的续写（第{i+1}句）"}
        for i in range(rounds)
    ]


# ====== Sentence extraction (robust) ======
_END_PUNCT = r"[。！？.!?]"
_SENT_PATTERN = re.compile(
    rf"""
    (                           # capture 1 complete sentence
      [^\S\r\n]*                # optional leading spaces
      (?:                       # content:
        (?!{_END_PUNCT}+$)      # not only end punct
        [^\r\n]                 # any char except newline
      )+?
      {_END_PUNCT}+             # end punct (one or more)
    )
    """,
    re.VERBOSE,
)

_BAD_ONLY_PUNCT = re.compile(
    r'^[\s"“”‘’\'，,。.！？.!?、:：;；…\-—（）()\[\]【】]+$'
)


def _clean_sentence(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _is_valid_sentence(s: str) -> bool:
    s = _clean_sentence(s)
    if not s:
        return False
    if _BAD_ONLY_PUNCT.match(s):
        return False
    # 至少包含一个“非标点/非空白”的字符
    if not re.search(
        r"[^\s，,。.！？.!?、:：;；…\-—（）()\[\]【】\"“”‘’\']+",
        s,
    ):
        return False
    return True


def extract_complete_sentences(buffer: str) -> Tuple[List[str], str]:
    """
    从 buffer 中抽取所有“已完成句子”（以句末符号结尾），返回 (sentences, remainder)
    remainder 是最后一个未完成的残句
    """
    buffer = buffer or ""
    sentences: List[str] = []
    last_end = 0

    for m in _SENT_PATTERN.finditer(buffer):
        seg = _clean_sentence(m.group(1))
        if _is_valid_sentence(seg):
            sentences.append(seg)
        last_end = m.end()

    remainder = buffer[last_end:] if last_end > 0 else buffer
    remainder = _clean_sentence(remainder)

    return sentences, remainder


# ====== Messages with real context ======
def _build_messages_from_story(story_id: str, user_text: str, continue_hint: str = "") -> List[Dict]:
    """
    ✅ 关键：从 storage 里读取该 story 的历史 turns，按时间顺序拼 messages，
    让模型真正“记得之前写到哪”。
    """
    history = get_story_turns(story_id) or []

    messages: List[Dict] = [
        {
            "role": "system",
            "content": (
                "你是一个擅长互动叙事续写的助手。"
                "请严格延续当前故事的设定、人物与场景继续写，不要新开故事，不要换主角，不要跳出叙事。"
                "输出应是自然的句子，不要只输出标点符号。"
            ),
        }
    ]

    # 控制上下文长度：只取最近 N 条 turns（避免 prompt 太长）
    max_turns = 24
    for t in history[-max_turns:]:
        role = "assistant" if t.get("author") == "ai" else "user"
        text = (t.get("text") or "").strip()
        if text:
            messages.append({"role": role, "content": text})

    # 当前输入放最后
    final_user = (user_text or "").strip() + (continue_hint or "")
    messages.append({"role": "user", "content": final_user})

    return messages


def _auth_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }


# ====== Non-stream call ======
def _call_deepseek(messages: List[Dict], stream: bool = False) -> str:
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "stream": stream,
        "temperature": 0.9,
        "top_p": 0.9,
        "max_tokens": 512,
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, headers=_auth_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()

    return (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    ).strip()


def generate_ai_turns(story_id: str, user_text: str, rounds: int, mode: str) -> List[Dict]:
    """
    非流式：自动补齐 rounds。
    ✅ 使用真实上下文（story_id 对应历史 turns），不会开新故事。
    """
    if mode == "human_only":
        return []

    if not DEEPSEEK_API_KEY:
        return _mock_turns(user_text, rounds)

    MAX_CONTINUE_CALLS = 6  # 防止无限继续
    all_sentences: List[str] = []

    try:
        for _ in range(MAX_CONTINUE_CALLS):
            need = rounds - len(all_sentences)
            if need <= 0:
                break

            continue_hint = (
                f"\n\n请在延续上文的前提下继续故事，严格再输出{need}句完整自然的句子，"
                f"每句必须包含内容，不要只输出标点。"
            )

            messages = _build_messages_from_story(story_id, user_text, continue_hint)

            content = _call_deepseek(messages, stream=False)
            if not content:
                break

            sents, remainder = extract_complete_sentences(content)

            # 一句都切不出来：若整体像句子，则当作一句
            if not sents and _is_valid_sentence(content):
                sents = [_clean_sentence(content)]

            for s in sents:
                if len(all_sentences) >= rounds:
                    break
                all_sentences.append(s)

            # 输出质量太差就停止，避免空转
            if not sents and not remainder:
                break

        if not all_sentences:
            return _mock_turns(user_text, rounds)

        return [{"author": "ai", "text": s} for s in all_sentences[:rounds]]

    except Exception:
        return _mock_turns(user_text, rounds)


# ====== Stream call helpers ======
async def _call_deepseek_stream(payload: Dict) -> AsyncGenerator[str, None]:
    """
    读取 SSE，yield 增量 delta.content
    """
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, headers=_auth_headers(), json=payload) as resp:
            resp.raise_for_status()

            async for line in resp.aiter_lines():
                if not line:
                    continue

                if line.startswith("data:"):
                    chunk = line[len("data:"):].strip()
                else:
                    chunk = line.strip()

                if chunk == "[DONE]":
                    break

                try:
                    j = httpx.Response(200, content=chunk).json()
                except Exception:
                    continue

                delta = (
                    j.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )
                if delta:
                    yield delta


async def stream_ai_turns(
    story_id: str, user_text: str, rounds: int, mode: str
) -> AsyncGenerator[Dict, None]:
    """
    流式：边到边切句 yield；如果结束后不够 rounds，会自动继续请求补齐。
    ✅ 使用真实上下文（story_id 对应历史 turns），不会开新故事。
    """
    if mode == "human_only":
        return

    if not DEEPSEEK_API_KEY:
        for i in range(rounds):
            await asyncio.sleep(0.35)
            yield {"author": "ai", "text": f"（mock stream）{user_text} -> AI 续写第{i+1}句"}
        return

    MAX_CONTINUE_CALLS = 6
    yielded = 0
    buffer = ""

    try:
        for attempt in range(MAX_CONTINUE_CALLS):
            need = rounds - yielded
            if need <= 0:
                return

            continue_hint = (
                f"\n\n请在延续上文的前提下继续故事，严格再输出{need}句完整自然的句子，"
                f"每句必须包含内容，不要只输出标点。"
            )

            messages = _build_messages_from_story(story_id, user_text, continue_hint)

            payload = {
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "stream": True,
                "temperature": 0.9,
                "top_p": 0.9,
                "max_tokens": 512,
            }

            produced_this_attempt = 0

            async for delta in _call_deepseek_stream(payload):
                buffer += delta

                sents, remainder = extract_complete_sentences(buffer)
                buffer = remainder

                for s in sents:
                    if yielded >= rounds:
                        return
                    yielded += 1
                    produced_this_attempt += 1
                    yield {"author": "ai", "text": s}

            # 一次流结束：残句如果像句子，也可以当一句输出
            if yielded < rounds and buffer and _is_valid_sentence(buffer):
                s = _clean_sentence(buffer)
                buffer = ""
                yielded += 1
                produced_this_attempt += 1
                yield {"author": "ai", "text": s}

            # 如果本轮完全没产出，避免死循环
            if attempt > 0 and produced_this_attempt == 0:
                break

    except Exception:
        for i in range(rounds - yielded):
            await asyncio.sleep(0.35)
            yield {
                "author": "ai",
                "text": f"（mock stream fallback）{user_text} -> AI 续写第{yielded + i + 1}句",
            }
