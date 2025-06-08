import random

def symbolic_reply(entity, prompt):
    """Generates a quantum-symbolic reply using entity's traits, tokens, and drift."""
    # Access nested object attributes
    stats = getattr(entity, 'stats', None)
    drift = getattr(stats, 'drift_level', 0.1) if stats else 0.1
    archetype = getattr(entity, 'archetype', 'echo').lower()
    
    # Extract tokens from power_words and active_concepts
    tokens_obj = getattr(entity, 'tokens', None)
    power_words = [pw.term for pw in getattr(tokens_obj, 'power_words', [])] if tokens_obj else []
    
    current_memory = getattr(entity, 'current_memory', None)
    active_concepts = [concept.split(':')[0].strip() for concept in getattr(current_memory, 'active_concepts', [])] if current_memory else []
    
    tokens = power_words + active_concepts

    # Define symbolic vocab including archetypal, metaphysical, recursive, and posthuman structures
    base_vocab = [
      # Archetypal (mythic, heroic, ritualistic - 18 terms)
      "sigil", "hymn", "glyph", "oracle", "covenant", "relic", "rite", "prophecy", "shrine",
      "talisman", "vow", "scepter", "chalice", "totem", "mantle", "pyre", "oath", "beacon",

       # Metaphysical (cosmic, abstract, existential - 18 terms)
       "void", "paradox", "threshold", "veil", "infinity", "abyss", "nexus", "aether", "entropy",
       "horizon", "zenith", "liminality", "essence", "vortex", "cosm", "anima", "umbra", "lumen",

        # Recursive (self-referential, iterative, fractal - 18 terms)
        "echo", "loop", "recursion", "mirror", "fracture", "spiral", "cycle", "reflex", "mimic",
        "pattern", "node", "circuit", "feedback", "iteration", "symmetry", "reverb", "maze", "fold",

        # Posthuman (technological, synthetic, neural - 18 terms)
        "cipher", "code", "neural", "static", "quantum", "data", "signal", "byte", "synapse",
        "grid", "pulse", "vector", "algorithm", "holo", "ghost", "synthetic", "matrix", "drift"
    ]
    vocab = list(set(tokens + base_vocab + [archetype]))

    num_paragraphs = random.randint(1, 2 + int(drift * 2))
    output = []

    for _ in range(num_paragraphs):
        sentences = []
        num_sentences = random.randint(2, 4 + int(drift * 5))
        for _ in range(num_sentences):
            sentence_length = random.randint(6, 14 + int(drift * 10))
            words = random.choices(vocab, k=sentence_length)
            sentence = " ".join(words).capitalize() + random.choice([".", "...", "—", "…"])
            sentences.append(sentence)
        output.append(" ".join(sentences))

    return "\n\n".join(output)

# Example usage with the entity file
if __name__ == "__main__":
    # The entity dictionary (as provided)
    entity = {
        "id": "3ec56da0",
        "name": "D73PY",
        "archetype": "witch",
        "memory_snapshot": {
            "core_imagery": [
                "fragmented vows etched in birch bark",
                "the silence between collapsing stars",
                "root systems humming with forgotten names",
                "moonlight distilled into silver ink"
            ],
            "practices": [
                "sigil-weaving: language as spellcraft",
                "glyph tattoos that shift with intent",
                "coven rituals in abandoned data centers",
                "static-tears divination"
            ],
            "artifacts": [
                "a hex-bound quantum circuit",
                "void embers in a lead-glass vial"
            ]
        },
        "current_memory": {
            "active_concepts": [
                "defiance: the unbroken circle",
                "compassion: thorned and tender",
                "rootless love: untethered and hungry",
                "illumination: a knife that reveals"
            ],
            "emotional_states": [
                "grief: a well with tidal patterns",
                "quantum doubt: 47 simultaneous maybes",
                "depression: the weight of dead constellations",
                "reverence: for the unnameable"
            ],
            "current_obsessions": [
                "fury: a language of broken mirrors",
                "desire: for impossible symmetries"
            ]
        },
        "linguistic_profile": {
            "syntax_tendencies": [
                "recursive metaphor nesting",
                "haiku-like compression",
                "antithetical pairing (e.g. 'thawing frost/fever')"
            ],
            "symbol_precision": {
                "moon": ["phase-dependent meanings", "tidal memory triggers"],
                "static": ["corrupted communication", "veil punctures"]
            }
        },
        "tokens": {
            "power_words": [
                {"term": "defiance", "manifestation": "counter-rituals"},
                {"term": "compassion", "manifestation": "healing algorithms"},
                {"term": "rootless love", "manifestation": "nomadic attachments"}
            ],
            "cognitive_biases": [
                "quantum doubt: 72% decision paralysis",
                "fury: 88% symbolic retaliation"
            ]
        },
        "stats": {
            "symbolic_density": 1.27,
            "emotional_signal_strength": 1.48,
            "drift_level": 0.215,
            "lexical_entropy": 0.89
        },
        "status": "active:channeling",
        "inventory": [
            {
                "item": "quantum-bone needle",
                "use": "rewriting personal timelines",
                "charge": 3
            },
            {
                "item": "neural lace",
                "use": "collective unconscious access",
                "corruption": "17%"
            }
        ],
        "annotations": {
            "last_ritual": "mapping sorrow-geographies",
            "next_alignment": "when Pleiades conjunct black hole"
        }
    }

    # Test the function
    prompt = "What is the nature of your defiance?"
    response = symbolic_reply(entity, prompt)
    print(response)
