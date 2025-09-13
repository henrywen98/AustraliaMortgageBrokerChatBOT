from typing import List, Dict
from openai import OpenAI
from .config import OPENAI_API_KEY, CHAT_MODEL, MAX_CONTEXT_CHARS
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

client = OpenAI(api_key=OPENAI_API_KEY)


def build_prompt(query: str, chunks: List[Dict]) -> str:
    pieces = []
    total = 0
    for ch in chunks:
        tag = f"【{ch['title']} | p.{ch['page_from']}-{ch['page_to']}】"
        text = (ch['text'] or '').strip().replace("\n", " ")
        seg = f"{tag}\n{text}\n"
        if total + len(seg) > MAX_CONTEXT_CHARS:
            break
        pieces.append(seg)
        total += len(seg)
    context = "\n\n".join(pieces) if pieces else "(无片段)"
    user_prompt = USER_PROMPT_TEMPLATE.format(query=query, context=context)
    return user_prompt


def answer(query: str, chunks: List[Dict]) -> str:
    prompt = build_prompt(query, chunks)
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content.strip()
