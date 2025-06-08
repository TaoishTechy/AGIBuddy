# glyph_parser.py

import re
from collections import Counter
from config.settings import SRQ_KEYWORDS
import logging

def extract_glyphs(memory, min_len=3):
    """Extract glyphs from memory, handling dict or string input."""
    logger.debug(f"Extracting glyphs from memory: {memory}")
    
    # Convert memory to string
    if isinstance(memory, dict):
        # Join relevant fields into a single string
        text_parts = []
        for key in ["active_concepts", "emotional_states", "current_obsessions"]:
            if key in memory and isinstance(memory[key], list):
                text_parts.extend(str(item) for item in memory[key] if isinstance(item, str))
        text = " ".join(text_parts)
    elif isinstance(memory, str):
        text = memory
    else:
        logger.warning(f"Invalid memory type: {type(memory)}")
        return []

    if not text.strip():
        logger.debug("Empty text after processing memory")
        return []

    # Extract words of minimum length
    try:
        words = re.findall(r'\b[a-zA-Z]{%d,}\b' % min_len, text.lower())
        logger.debug(f"Extracted glyphs: {words}")
        return words
    except Exception as e:
        logger.error(f"Error extracting glyphs: {e}")
        return []

def detect_self_reference(text: str) -> float:
    """
    Approximate SRQ based on presence of recursive pronouns/concepts.
    """
    text = text.lower()
    refs = sum(text.count(k) for k in SRQ_KEYWORDS)
    return min(1.0, refs / max(1, len(text.split()) / 5))

def detect_fracture_signals(text: str):
    """
    Extract motifs suggesting psychological or mythic fragmentation.
    """
    fracture_terms = ["lost", "echo", "ash", "void", "hollow", "fracture", "shattered"]
    return [word for word in fracture_terms if word in text.lower()]
