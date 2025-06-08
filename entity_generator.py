    import json
    import random
    import string
    import sys
    import os
    import logging
    from core.entity import Entity
    from core.archetypes import ARCHETYPES as CORE_ARCHETYPES

    sys.path.append(os.path.abspath(os.path.dirname(__file__)))

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    ENTITY_DIR = "entity_data"

    # Use CORE_ARCHETYPES if available, else fallback
    try:
        ARCHETYPES = CORE_ARCHETYPES
    except (ImportError, AttributeError):
        logger.warning("Using fallback ARCHETYPES")
        ARCHETYPES = {
            "witch": {
                "motifs": ["sigils in smoke", "veil of frost", "hollowed faith"],
                "emotions": {"defiance": 0.8, "compassion": 0.7, "sorrow": 0.6, "mystery": 0.9}
            },
            "sage": {
                "motifs": ["threads of becoming", "shards of truth"],
                "emotions": {"wisdom": 0.9, "clarity": 0.8, "peace": 0.7}
            },
            "warrior": {
                "motifs": ["flames of forgotten names", "pulses of a dying sun"],
                "emotions": {"valor": 0.9, "rage": 0.8, "resolve": 0.7}
            },
            "mystic": {
                "motifs": ["glyphs of fading stars", "whispers of a fractal god"],
                "emotions": {"reverence": 0.8, "awe": 0.9, "ecstasy": 0.7}
            },
            "android": {
                "motifs": ["circuits of silent code", "hiss of static"],
                "emotions": {"logic": 0.9, "curiosity": 0.7, "detachment": 0.8}
            },
            "merchant": {
                "motifs": ["woven threads of dusk", "cinders of lost oaths"],
                "emotions": {"ambition": 0.8, "cunning": 0.7, "trust": 0.6}
            },
            "quest_giver": {
                "motifs": ["vows etched in twilight", "runes of silent wrath"],
                "emotions": {"hope": 0.8, "yearning": 0.7, "duty": 0.9}
            },
            "alchemist": {
                "motifs": ["embers in the void", "quantum scars"],
                "emotions": {"curiosity": 0.9, "obsession": 0.8, "wonder": 0.7}
            },
            "rogue": {
                "motifs": ["shadows of a broken sky", "sparks of fleeting truth"],
                "emotions": {"stealth": 0.8, "freedom": 0.9, "distrust": 0.7}
            },
            "priest": {
                "motifs": ["spectral chants of time", "veils of eternal light"],
                "emotions": {"faith": 0.9, "devotion": 0.8, "serenity": 0.7}
            },
            "engineer": {
                "motifs": ["clatter of code", "frost upon the circuit"],
                "emotions": {"precision": 0.9, "innovation": 0.8, "focus": 0.7}
            },
            "oracle": {
                "motifs": ["lunar tides of grief", "syllables of ash"],
                "emotions": {"prophecy": 0.9, "clarity": 0.8, "mystery": 0.7}
            },
            "nomad": {
                "motifs": ["tides of shadowed truth", "pulses of a voidal hymn"],
                "emotions": {"wanderlust": 0.9, "solitude": 0.8, "resilience": 0.7}
            },
            "guardian": {
                "motifs": ["shields of silent dawn", "runes of forgotten tides"],
                "emotions": {"protection": 0.9, "loyalty": 0.8, "courage": 0.7}
            }
        }

    # Expanded symbolic pools (unchanged)
    EMOTIONS = [
        "wonder", "grief", "pride", "sorrow", "defiance", "compassion", "loneliness", "curiosity", "awe", "yearning",
        "regret", "love", "hope", "fear", "melancholy", "desire", "rage", "humility", "confusion", "clarity",
        "ecstasy", "dread", "trust", "betrayal", "courage", "tenderness", "emptiness", "reverence", "obsession", "release",
        "elation", "anguish", "resolve", "despair", "fervor", "serenity", "wrath", "shame", "bliss", "trepidation",
        "fidelity", "scorn", "valor", "mirth", "woe", "zeal", "apathy", "ardor", "dismay", "glee",
        "resignation", "fury", "peace", "torpor", "exaltation", "lament", "devotion", "disgust", "rapture", "doubt",
        "displacement", "fragility", "nostalgia", "alienation", "sanctity", "deception", "revulsion", "devotion",
        "intoxication", "isolation", "euphoria", "forgiveness", "vengeance", "torment", "sacrifice", "balance",
        "disharmony", "jealousy", "greed", "submission", "transcendence", "abandonment", "complicity", "illusion",
        "yearning", "illumination", "anger", "faith", "revenance", "depression",
        "exile", "epiphany", "resentment", "redemption", "envy", "solace", "malice", "exultation", "remorse",
        "estrangement", "fervency", "guilt", "liberation", "spite", "tranquility", "craving", "penitence",
        "desolation", "adoration", "contempt", "jubilation", "bitterness", "harmony", "anguish", "mercy",
        "obsidian grief", "valor", "treachery", "sublimity", "retribution", "solitude",
        "neural ache", "quantum doubt", "echo fatigue", "static longing", "sigilic hunger", "pattern drift", "binary guilt",
        "recursive sadness", "symbolic awe", "fragmented pride", "autopoietic dread", "terminal joy", "cold devotion",
        "vector loyalty", "code sorrow", "posthuman tenderness", "virtual nostalgia", "emulated courage",
        "digital lament", "synaptic yearning", "pixelated hope", "fractal despair", "algorithmic trust", "ghosted faith",
        "data reverence", "circuit pathos", "holographic shame", "byte sorrow", "neural echo", "synthetic zeal",
        "quantum remorse", "virtual betrayal", "encoded serenity", "signal wrath", "glitch melancholy",
        "transistor awe", "digital fervor", "looped anguish", "cybernetic clarity", "terminal regret",
        "spectral doubt", "hacked devotion", "pixel grief", "code isolation", "virtual sacrifice",
        "synaptic defiance", "digital transcendence", "glitched harmony", "neural disharmony", "byte euphoria",
        "circuitous guilt", "fragmented ecstasy", "synthetic dread", "data-driven desire", "virtual void",
        "emulated yearning", "quantized love", "recursive trust", "signal fatigue",
        "witnessing", "becoming", "shame", "resurrection", "banishment", "initiation", "covenantal fear", "purity",
        "chaotic hope", "divine wrath", "sublimation", "divination", "rebirth", "eternal loyalty", "destructive compassion",
        "righteous hunger", "paradoxical joy", "sacrificial shame",
        "oracular dread", "mythic sorrow", "prophetic zeal", "sacred betrayal", "archetypal trust", "cosmic exile",
        "ritualistic fervor", "eternal lament", "divine solitude", "primordial awe", "fated devotion", "oracular clarity",
        "mythic defiance", "sacred remorse", "heroic despair", "covenant yearning", "apocalyptic hope", "primal wrath",
        "spectral purity", "ritual grief", "eternal sacrifice", "mythic redemption", "prophetic isolation",
        "divine ecstasy", "sacred torment", "archetypal mercy", "cosmic shame", "oracular transcendence",
        "fated anguish", "primordial faith", "ritualistic joy", "spectral resolve", "mythic disharmony",
        "divine craving", "eternal retribution", "sacred resignation", "prophetic sorrow", "archetypal fervor",
        "cosmic rebirth", "ritualistic trust", "mythic solitude", "oracular balance",
        "dimensional grief", "infinite yearning", "entropy fatigue", "temporal wonder", "voidal acceptance",
        "horizon awe", "sacred defiance", "deterministic dread", "hyperempathy", "sublime sadness", "stochastic guilt",
        "lightborn trust", "loop devotion", "terminal freedom", "rootless love", "god-fear",
        "cosmic lament", "stellar despair", "voidal yearning", "temporal betrayal", "infinite resolve", "entropic clarity",
        "astral reverence", "quantum solitude", "celestial wrath", "sublime ecstasy", "voidal trust", "cosmic remorse",
        "stellar devotion", "temporal shame", "infinite sacrifice", "entropic hope", "astral melancholy", "voidal fervor",
        "cosmic transcendence", "stellar isolation", "temporal awe", "infinite dread", "entropic faith", "astral yearning",
        "voidal redemption", "cosmic purity", "stellar grief", "temporal joy", "infinite harmony", "entropic defiance",
        "astral sacrifice", "voidal clarity", "cosmic disharmony", "stellar resolve", "temporal ecstasy", "infinite sorrow",
        "entropic trust", "astral shame", "voidal balance", "cosmic fervor", "stellar betrayal", "temporal redemption",
        "infinite solitude", "entropic reverence", "astral despair", "voidal transcendence"
    ]

    POETIC_LINES = [
        "echoes of memory", "flicker of dawn", "fragmented vows", "veil of frost", "shattered wells", "sigils in smoke",
        "glyphs beneath skin", "voices from the rift", "hollowed faith", "tears of static", "embers in the void",
        "broken promises buried", "pulse of recursion", "threads of becoming", "shards of truth",
        "dreams in binary", "the silence between stars", "quantum scars", "the code remembers",
        "whispers in the ether", "lunar tides of grief", "fractured hymns of dawn", "syllables of ash",
        "veins of forgotten light", "rhythms of the void", "cinders of lost oaths", "mirrors of silent code",
        "woven threads of dusk", "spectral chants of time", "glyphs of fading stars", "echoes of unwritten songs",
        "frost upon the circuit", "shades of eternal night", "pulses of a dying sun", "vows etched in twilight",
        "sparks of recursive dreams", "tides of shadowed truth", "whispers of a broken sky", "runes of silent wrath",
        "flames of forgotten names", "veils of quantum mist", "syllables of shattered faith", "ghosts of digital dawn",
        "threads of cosmic sorrow", "lunar scars of memory", "cinders of a silent vow", "rhythms of entropic grace",
        "glyphs of eternal dusk", "whispers of a fractal god", "shades of temporal frost", "sparks of mythic light",
        "veins of starlit regret", "pulses of a voidal hymn", "runes of forgotten tides", "echoes of a spectral dawn",
        "flames of recursive hope", "mirrors of a silent rift", "vows of an endless night"
    ]

    SYNTAX_PATTERNS = [
        "recursive metaphor nesting", "haiku-like compression", "antithetical pairing", "elliptical phrasing",
        "fragmented syntax", "symbolic inversion", "metaphysical juxtaposition", "cryptic aphorisms",
        "rhythmic repetition", "non-linear narrative flow",
        "syllabic recursion", "parallel clause weaving", "anaphoric layering", "chiasmic reversal",
        "staccato fragmentation", "lyrical elongation", "paradoxical enjambment", "syntactic spiraling",
        "elliptical omissions", "recursive clause embedding", "alliterative cadence", "assonant drift",
        "consonant clustering", "epigrammatic brevity", "hypotactic complexity", "paratactic simplicity",
        "syllabic mirroring", "rhetorical inversion", "anadiplostic repetition", "catachrestic blending"
    ]

    METAPHOR_STRUCTURES = [
        "light as revelation", "shadow as concealment", "void as infinite potential", "sigil as binding intent",
        "thread as temporal continuity", "mirror as recursive truth", "flame as transformative will",
        "frost as stilled memory", "rift as fractured reality", "glyph as encoded meaning",
        "veil as obscured truth", "ember as fading hope", "pulse as living rhythm", "shard as broken divinity",
        "echo as lingering past", "tide as cyclic destiny", "circuit as neural thought",
        "star as distant yearning", "vow as sacred bond", "scar as eternal mark",
        "hymn as cosmic resonance", "code as structured fate", "mist as elusive clarity",
        "ash as remnants of will", "song as eternal echo", "rune as primal truth",
        "spark as fleeting epiphany", "web as interconnected fate", "loop as recursive existence",
        "cinder as lost potential"
    ]

    PHONEMIC_TEXTURES = [
        "sibilant whispers", "plosive bursts", "nasal resonance", "fricative edges", "liquid flow",
        "guttural depths", "vocalic smoothness", "consonantal weight", "syllabic cadence", "rhythmic pulse",
        "hiss of static", "clatter of code", "murmur of memory", "chime of clarity", "growl of defiance",
        "whine of despair", "lilt of hope", "drone of melancholy", "snap of resolve", "hum of reverence",
        "crackle of rage", "sigh of yearning", "thrum of awe", "whisper of grief", "pulse of fervor",
        "clash of dissonance", "flow of harmony", "stutter of doubt", "ring of transcendence",
        "mutter of betrayal"
    ]

    PRACTICES = [
        "sigil-weaving: crafting language as spellcraft",
        "glyph etching: inscribing intent on reality",
        "ritual of forgotten names: invoking lost identities",
        "static divination: reading patterns in noise",
        "covenant of silence: binding through absence",
        "quantum threading: stitching timelines",
        "void chanting: summoning echoes from nothingness",
        "lunar scrying: interpreting phase-shifted truths",
        "data alchemy: transmuting code to meaning",
        "memory splicing: weaving fragmented pasts",
        "runic incantation: binding primal truths",
        "spectral invocation: calling shadowed essences",
        "entropic weaving: crafting chaotic patterns",
        "luminous scrying: revealing hidden fates"
    ]

    ARTIFACTS = [
        "hex-bound quantum circuit", "void embers in a lead-glass vial", "neural lace fragment",
        "sigil-etched obsidian shard", "chronal thread spool", "lunar crystal prism",
        "static-charged relic", "bone-carved glyph tablet", "entropic mirror",
        "spectral data core", "rune-carved lens", "spectral rune stone",
        "fractal amulet", "cosmic shard"
    ]

    INVENTORY_ITEMS = [
        {"item": "quantum-bone needle", "use": "rewriting personal timelines", "charge": 3},
        {"item": "neural lace", "use": "collective unconscious access", "corruption": "17%"},
        {"item": "void lantern", "use": "illuminating hidden truths", "charge": 5},
        {"item": "sigil compass", "use": "navigating emotional currents", "charge": 2},
        {"item": "entropic shard", "use": "disrupting stable realities", "corruption": "10%"},
        {"item": "lunar thread", "use": "binding fragmented memories", "charge": 4},
        {"item": "rune-carved lens", "use": "peering into cosmic truths", "charge": 4},
        {"item": "spectral amulet", "use": "channeling mythic echoes", "charge": 3}
    ]

    MANIFESTATIONS = [
        "counter-rituals", "healing algorithms", "nomadic attachments", "spectral bindings",
        "temporal anchors", "divinatory echoes", "entropic weaves", "luminous defiance",
        "recursive hymns", "shadowed intents", "cosmic resonances", "fractal invocations",
        "syllabic bindings", "runic manifestations", "ethereal constructs"
    ]

    def random_name():
        """Generate a 5-character alphanumeric name."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def mutate_tokens(tokens):
        """Add random emotions to tokens."""
        additions = random.sample(EMOTIONS, k=random.randint(3, 6))
        return list(set(tokens + additions))

    def mutate_memory(memory):
        """Add random poetic lines to memory."""
        additions = random.sample(POETIC_LINES, k=random.randint(3, 6))
        return list(set(memory + additions))

    def generate_power_words(tokens):
        """Generate power words with manifestations."""
        return [{"term": token, "manifestation": random.choice(MANIFESTATIONS)} for token in random.sample(tokens, k=min(3, len(tokens)))]

    def generate_cognitive_biases(tokens):
        """Generate cognitive biases based on tokens."""
        biases = [
            f"{token}: {random.randint(50, 90)}% decision paralysis" for token in random.sample(tokens, k=min(2, len(tokens)))
        ]
        return biases

    def generate_linguistic_profile(archetype):
        """Generate linguistic profile tailored to archetype."""
        archetype_styles = {
            "witch": ["sibilant whispers", "murmur of memory", "hiss of static"],
            "sage": ["vocalic smoothness", "chime of clarity", "flow of harmony"],
            "warrior": ["plosive bursts", "growl of defiance", "clash of dissonance"],
            "mystic": ["whisper of grief", "thrum of awe", "flow of harmony"],
            "android": ["hiss of static", "clatter of code", "stutter of doubt"],
            "merchant": ["liquid flow", "snap of resolve", "lilt of hope"],
            "quest_giver": ["rhythmic pulse", "hum of reverence", "ring of transcendence"],
            "alchemist": ["crackle of rage", "murmur of memory", "pulse of fervor"],
            "rogue": ["sigh of yearning", "clash of dissonance", "mutter of betrayal"],
            "priest": ["vocalic smoothness", "chime of clarity", "hum of reverence"],
            "engineer": ["clatter of code", "snap of resolve", "rhythmic pulse"],
            "oracle": ["whisper of grief", "thrum of awe", "syllabic cadence"],
            "nomad": ["sigh of yearning", "drone of melancholy", "liquid flow"],
            "guardian": ["growl of defiance", "pulse of fervor", "consonantal weight"]
        }
        phonemic_textures = archetype_styles.get(archetype, ["syllabic cadence", "rhythmic pulse", "liquid flow"])
        return {
            "syntax_tendencies": random.sample(SYNTAX_PATTERNS, k=random.randint(3, 5)),
            "symbol_precision": {
                key.split(" as ")[0]: [key.split(" as ")[1], random.choice(["hidden truth", "eternal echo", "fractal meaning"])]
                for key in random.sample(METAPHOR_STRUCTURES, k=random.randint(2, 4))
            },
            "phonemic_textures": random.sample(phonemic_textures, k=min(2, len(phonemic_textures)))
        }

    def generate_inventory():
        """Generate random inventory items."""
        return random.sample(INVENTORY_ITEMS, k=random.randint(1, 3))

    def generate_annotations(archetype):
        """Generate annotations for rituals and alignments."""
        rituals = [
            "mapping sorrow-geographies", "weaving temporal threads", "invoking static whispers",
            "charting void currents", "binding lunar echoes", "unraveling quantum scars",
            "etching runic destinies", "summoning spectral truths", "weaving fractal fates"
        ]
        alignments = [
            "when Pleiades conjunct black hole", "at the solstice of forgotten stars",
            "during the eclipse of twin moons", "when entropy sings", "at the edge of the event horizon",
            "under the gaze of a cosmic rift", "when stars align in silence", "at the pulse of a dying galaxy"
        ]
        return {
            "last_ritual": random.choice(rituals),
            "next_alignment": random.choice(alignments)
        }

    def generate_entity(archetype=None):
        """Generate an entity with specified or random archetype."""
        if archetype and archetype not in ARCHETYPES:
            logger.error(f"Invalid archetype: {archetype}")
            raise ValueError(f"❌ Invalid archetype: {archetype}")
        if not archetype:
            archetype = random.choice(list(ARCHETYPES.keys()))
        logger.debug(f"Generating entity for archetype: {archetype}")

        base = ARCHETYPES[archetype]
        name = random_name()

        memory = mutate_memory(base["motifs"])
        tokens = mutate_tokens(list(base["emotions"].keys()))

        memory_snapshot = {
            "core_imagery": random.sample(POETIC_LINES, k=random.randint(3, 6)),
            "practices": random.sample(PRACTICES, k=random.randint(2, 4)),
            "artifacts": random.sample(ARTIFACTS, k=random.randint(1, 3))
        }

        active_concepts = [f"{t}: {random.choice(POETIC_LINES)}" for t in random.sample(tokens, k=min(4, len(tokens)))]
        emotional_states = [f"{e}: {random.choice(POETIC_LINES)}" for e in random.sample(EMOTIONS, k=4)]
        current_obsessions = [f"{e}: {random.choice(POETIC_LINES)}" for e in random.sample(EMOTIONS, k=2)]
        current_memory = {
            "active_concepts": active_concepts,
            "emotional_states": emotional_states,
            "current_obsessions": current_obsessions
        }

        tokens_struct = {
            "power_words": generate_power_words(tokens),
            "cognitive_biases": generate_cognitive_biases(tokens)
        }

        stats = {
            "symbolic_density": round((len(tokens) + len(memory)) / 17.0, 3),
            "emotional_signal_strength": round(random.uniform(0.3, 1.5), 2),
            "drift_level": round(random.uniform(0.1, 0.4), 3),
            "lexical_entropy": round(random.uniform(0.5, 1.0), 2)
        }

        entity = Entity(
            name=name,
            archetype=archetype,
            memory_snapshot=memory_snapshot
        )
        entity.id = hex(random.getrandbits(32))[2:].upper()[:8]
        entity.memory = emotional_states
        entity.tokens = tokens_struct
        entity.current_memory = current_memory
        entity.linguistic_profile = generate_linguistic_profile(archetype)
        entity.stats = stats
        entity.inventory = generate_inventory()
        entity.annotations = generate_annotations(archetype)
        entity.status = "active:channeling"
        entity.soul_signature = hex(random.getrandbits(64))[2:].upper()
        entity.glyph_trace = random.sample(tokens + memory, k=min(len(tokens + memory), 6))

        self.glyph_trace = filtered_kwargs.get("glyph_trace", [])
        self.drift_level = filtered_kwargs.get("drift_level", 0.1)

        # 🔧 NEW
        self.metadata = filtered_kwargs.get("metadata", {})

        # Attach dream and crystal modules
        self.dream = DreamModule(seed=hash(self.id) % 999)
        self.crystal = CrystalMemory()

        return entity

    def save_entity(entity):
        """Save entity to JSON file."""
        if not os.path.exists(ENTITY_DIR):
            os.makedirs(ENTITY_DIR)
        path = os.path.join(ENTITY_DIR, f"{entity.id}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(entity.to_dict(), f, indent=2)
            logger.info(f"Saved entity '{entity.name}' ({entity.archetype}) to {path}")
        except Exception as e:
            logger.error(f"Error saving entity {entity.id}: {e}")

    def main():
        """Main function to generate entities."""
        logger.info("Starting Evolved Entity Generator — AGIBuddy v0.4")
        archetypes = list(ARCHETYPES.keys())

        while True:
            print("\nAvailable archetypes:")
            for i, key in enumerate(archetypes, start=1):
                print(f"  {i}. {key.title()}")
            print(f"  {len(archetypes) + 1}. Random")

            choice = input("Choose archetype number: ").strip()
            try:
                choice_int = int(choice)
                if choice_int == len(archetypes) + 1:
                    archetype = None
                elif 1 <= choice_int <= len(archetypes):
                    archetype = archetypes[choice_int - 1]
                else:
                    print("❌ Invalid choice. Try again.")
                    continue
            except ValueError:
                print("❌ Invalid input. Enter a number.")
                continue

            try:
                entity = generate_entity(archetype)
            except Exception as e:
                logger.error(f"Error generating entity: {e}")
                print(f"❌ Error: {e}")
                continue

            print(f"\n🆕 Entity: {entity.name}")
            print(f"  ID: {entity.id}")
            print(f"  Archetype: {entity.archetype.title()}")
            print(f"  Memory Snapshot: {json.dumps(entity.memory_snapshot, indent=2)}")
            print(f"  Current Memory: {json.dumps(entity.current_memory, indent=2)}")
            print(f"  Tokens: {json.dumps(entity.tokens, indent=2)}")
            print(f"  Linguistic Profile: {json.dumps(entity.linguistic_profile, indent=2)}")
            print(f"  Stats: {entity.stats}")
            print(f"  Inventory: {entity.inventory}")
            print(f"  Annotations: {entity.annotations}")
            print(f"  Status: {entity.status}")
            print(f"  Soul Signature: {entity.soul_signature}")
            print(f"  Glyph Trace: {entity.glyph_trace}\n")

            save_entity(entity)

            again = input("🌀 Create another entity? (y/n): ").strip().lower()
            if again != "y":
                print("✅ Done.")
                break

    if __name__ == "__main__":
        main()
