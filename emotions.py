import os, re
from typing import Literal, Tuple

# Plant mapping
PLANT_BY_EMOTION = {
    "happy": "🌻 Sunflower",
    "romantic": "🌹 Rose",
    "sad": "🌿 Willow",
    "calm": "🌲 Pine",
    "angry": "🌵 Cactus",
    "nostalgic": "🌼 Daisy",
    "excited": "🌷 Tulip",
    "proud": "🌺 Hibiscus",
}

DEFAULT_EMOTION = "nostalgic"

def classify_rule_based(text: str) -> str:
    t = text.lower()
    # super simple keyword buckets
    rules = [
        (r"\b(happy|joy|glad|smile|delight|celebrate)\b", "happy"),
        (r"\b(love|romance|date|anniversary|kiss|valentine)\b", "romantic"),
        (r"\b(sad|cry|loss|hurt|miss|lonely)\b", "sad"),
        (r"\b(calm|peace|relax|serene|quiet|beach)\b", "calm"),
        (r"\b(angry|mad|rage|furious|annoyed)\b", "angry"),
        (r"\b(old times|nostalgia|remember|childhood|school)\b", "nostalgic"),
        (r"\b(excited|thrill|hype|can’t wait|win)\b", "excited"),
        (r"\b(proud|achievement|award|rank|milestone)\b", "proud"),
    ]
    for pattern, label in rules:
        if re.search(pattern, t):
            return label
    return DEFAULT_EMOTION

def classify(text: str) -> Tuple[str, str]:
    """
    Returns (emotion_label, plant_label)
    Uses RULE-BASED by default. Switch to HF or OpenAI by setting env flags:
    - EMOTION_BACKEND=hf or openai
    - For HF, model downloads at runtime; for OpenAI, set OPENAI_API_KEY.
    """
    backend = os.getenv("EMOTION_BACKEND", "rule").lower()
    if backend == "rule":
        label = classify_rule_based(text or "")
    elif backend == "hf":
        try:
            from transformers import pipeline
            nlpp = pipeline("sentiment-analysis")
            out = nlpp(text or "")[0]["label"].lower()
            # Map common outputs to our labels
            label = "happy" if "pos" in out else "sad"
        except Exception:
            label = classify_rule_based(text or "")
    elif backend == "openai":
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = ("Classify the dominant emotion of this memory text into exactly one of: " ,"happy, romantic, sad, calm, angry, nostalgic, excited, proud.\nText:\n" + (text or ""))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                temperature=0
            )
            label = (resp.choices[0].message.content or "").strip().lower()
            if label not in PLANT_BY_EMOTION:
                label = DEFAULT_EMOTION
        except Exception:
            label = classify_rule_based(text or "")
    else:
        label = classify_rule_based(text or "")

    return label, PLANT_BY_EMOTION.get(label, "🌼 Daisy")

