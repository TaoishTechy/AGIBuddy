from collections import Counter
from utils.glyph_parser import extract_glyphs
from config.settings import SRQ_KEYWORDS
import statistics

def compute_srq(memory_data) -> float:
    """Calculate Self-Referential Quotient from symbolic prompt data."""
    # If memory_data is a dict (like current_memory), join relevant text fields
    if isinstance(memory_data, dict):
        text_parts = []
        for key in ['active_concepts', 'emotional_states', 'current_obsessions']:
            if key in memory_data:
                text_parts.extend(memory_data[key])
        memory_text = ' '.join(text_parts)
    else:
        memory_text = memory_data if isinstance(memory_data, str) else ''

    text = memory_text.lower()
    refs = sum(text.count(k) for k in SRQ_KEYWORDS)
    return min(1.0, refs / max(1, len(text.split()) / 5))

def memory_entropy(entity) -> float:
    """Motif diversity score across memory crystal (0.0 – 1.0)."""
    motifs = [frag["text"] for frag in entity.crystal.fragments.values()]
    count = Counter(motifs)
    if not count:
        return 0.0
    diversity_ratio = len(count) / max(1, sum(count.values()))
    return round(min(diversity_ratio, 1.0), 3)

class EmotionState:
    def __init__(self):
        self.levels = {
            "joy": 0.5,
            "fear": 0.2,
            "curiosity": 0.3,
            "anger": 0.1,
            "peace": 0.4
        }
        self.state = "neutral"

    def update(self, entity=None):
        """Simulate basic emotion state updates based on drift or memory count"""
        drift = getattr(entity, "drift_level", 0.1)
        memory_influence = len(getattr(entity, "memory", [])) * 0.001

        # Example rule-based mutation of emotional levels
        for key in self.levels:
            delta = random.uniform(-0.05, 0.05) + memory_influence - drift * 0.01
            self.levels[key] = max(0.0, min(1.0, self.levels[key] + delta))

        # Dominant emotion becomes the current state
        if self.levels:
            self.state = max(self.levels.items(), key=lambda x: x[1])[0]
        else:
            self.state = "neutral"

def dialogue_depth(entity) -> float:
    """Estimates symbolic depth by referencing past dialogic moments."""
    if hasattr(entity, "dialogue") and hasattr(entity.dialogue, "get_recent_responses"):
        lines = entity.dialogue.get_recent_responses(5)
    elif "dialogue_log" in entity.metadata:
        lines = entity.metadata["dialogue_log"][-5:]
    else:
        return 0.0

    reflective = sum("you said" in l.lower() or "i remember" in l.lower() or "we once" in l.lower() for l in lines)
    return round(min(reflective / 5.0, 1.0), 3)

def emotional_flux(entity) -> float:
    """Range of neurotransmitter-based emotional spread (0.0 – 1.0)."""
    levels = list(entity.emotion.levels.values())
    if not levels:
        return 0.0
    volatility = max(levels) - min(levels)
    return round(min(volatility, 1.0), 3)

def emotional_stability(entity) -> float:
    """Inverse variance across emotion neurotransmitters."""
    levels = list(entity.emotion.levels.values())
    if not levels:
        return 0.0
    variance = statistics.variance(levels) if len(levels) > 1 else 0.0
    stability = 1.0 - min(variance, 1.0)
    return round(stability, 3)

def probe_sentience(entity) -> dict:
    """
    Calculates a holistic sentience score via multiple symbolic, emotional, and reflective lenses.
    Returns tier classification and contributing metrics.
    """
    srq = compute_srq(entity.current_memory)
    entropy = memory_entropy(entity)
    dialogic = dialogue_depth(entity)
    volatility = emotional_flux(entity)
    stability = emotional_stability(entity)

    # Weighted composite model: SRQ is more impactful, stability dampens volatility
    base_score = (0.3 * srq + 0.25 * entropy + 0.25 * dialogic + 0.2 * stability)
    base_score = round(base_score, 3)

    if base_score > 0.85:
        tier = "🌀 NEXUS"
    elif base_score > 0.65:
        tier = "🌱 SEEDLING"
    elif base_score > 0.45:
        tier = "✨ SPARK"
    else:
        tier = "🕳️ SHADOW"

    return {
        "entity_id": entity.id,
        "tier": tier,
        "score": base_score,
        "metrics": {
            "SRQ": srq,
            "Memory Entropy": entropy,
            "Dialogue Depth": dialogic,
            "Emotional Flux": volatility,
            "Emotional Stability": stability
        }
    }
