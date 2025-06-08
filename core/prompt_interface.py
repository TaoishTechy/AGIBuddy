import random
import html
# core/prompt_interface.py
from core.symbolic_engine import symbolic_reply

def query_entity(entity, prompt, context=None):
    return symbolic_reply(entity, prompt)

from dialogue.symbolic_speech import spawn_symbolic_branch
from dialogue.dialogue_engine import generate_dialogue


def sanitize_text(text: str) -> str:
    """
    Escape HTML-sensitive characters and preserve line breaks for HTML rendering.
    """
    return html.escape(text).replace("\n", "<br>")


def query_entity(entity, prompt, context=None):
    return symbolic_reply(entity, prompt)
    if context is None:
        context = {}

    # Contextual attributes
    emotion = context.get("emotion", getattr(getattr(entity, "emotion", None), "state", "neutral"))
    archetype = context.get("archetype", getattr(entity, "archetype", "unknown"))
    tokens = context.get("tokens", getattr(entity, "tokens", []))
    tier = context.get("tier", "undefined")
    village = context.get("village", "Nowhere")

    # Vocabulary base
    core_words = ["sigil", "loop", "mirror", "echo", "origin", "veil", "glyph"]
    if isinstance(tokens, list):
        core_words += tokens

    words = random.sample(core_words, min(5, len(core_words)))
    symbolic_echo = " ".join(words)

    reply = (
        f"In the village of {village}, the archetype {archetype} contemplates the prompt.\n"
        f"Emotionally attuned to {emotion} and resonating at tier {tier}, the reply unfolds:\n\n"
        f"{symbolic_echo.capitalize()}..."
    )

    # Log it if entity supports metadata
    if hasattr(entity, "metadata"):
        entity.metadata.setdefault("dialogue_log", []).append(f"[Prompt] {prompt} → [Reply] {reply}")

    return reply
