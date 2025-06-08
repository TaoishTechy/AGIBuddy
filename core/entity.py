import logging
from core.dream_module import DreamModule
from core.memory_crystal import CrystalMemory

logger = logging.getLogger(__name__)

class EmotionState:
    def __init__(self, data=None):
        if isinstance(data, dict):
            self.levels = data.get("levels", {})
            self.volatile = data.get("volatile", False)
            self.modulators = data.get("modulators", [])
        else:
            self.levels = {}
            self.volatile = False
            self.modulators = []

    def to_dict(self):
        return {
            "levels": self.levels,
            "volatile": self.volatile,
            "modulators": self.modulators
        }

class Entity:
    def __init__(self, **kwargs):
        """
        Initialize an Entity with attributes from kwargs, handling unexpected fields.
        Logs errors and ensures fallbacks for missing data.
        """
        try:
            valid_fields = {
                "id", "name", "archetype", "village", "status", "stats",
                "memory", "current_memory", "memory_snapshot", "linguistic_profile",
                "tokens", "inventory", "annotations", "soul_signature", "glyph_trace",
                "drift_level", "metadata", "emotion"
            }

            filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

            self.id = filtered_kwargs.get("id", "unknown")
            self.name = filtered_kwargs.get("name", "Unnamed")
            self.archetype = filtered_kwargs.get("archetype", "unknown")
            self.village = filtered_kwargs.get("village")
            self.status = filtered_kwargs.get("status", "inactive")

            self.stats = filtered_kwargs.get("stats", {
                "symbolic_density": 0.5,
                "emotional_signal_strength": 0.5,
                "drift_level": 0.1,
                "lexical_entropy": 0.5
            })
            if "drift_level" in filtered_kwargs:
                self.stats["drift_level"] = filtered_kwargs["drift_level"]

            self.memory = filtered_kwargs.get("memory", [])
            self.current_memory = filtered_kwargs.get("current_memory", {
                "active_concepts": [],
                "emotional_states": [],
                "current_obsessions": []
            })
            self.memory_snapshot = filtered_kwargs.get("memory_snapshot", {
                "core_imagery": [],
                "practices": [],
                "artifacts": []
            })

            self.linguistic_profile = filtered_kwargs.get("linguistic_profile", {
                "syntax_tendencies": [],
                "symbol_precision": {},
                "phonemic_textures": []
            })

            self.tokens = filtered_kwargs.get("tokens", {
                "power_words": [],
                "cognitive_biases": []
            })

            inventory = filtered_kwargs.get("inventory", [])
            if isinstance(inventory, list):
                normalized_inventory = []
                for item in inventory:
                    if isinstance(item, dict):
                        normalized_item = {
                            "item": item.get("name", item.get("item", "unknown")),
                            "use": item.get("use", "unknown purpose"),
                            "charge": item.get("charge", 1),
                            "corruption": item.get("corruption"),
                            "rarity": item.get("rarity"),
                            "source": item.get("source"),
                            "timestamp": item.get("timestamp")
                        }
                        normalized_inventory.append(normalized_item)
                    else:
                        logger.warning(f"Invalid inventory item in {self.id}: {item}")
                self.inventory = normalized_inventory
            else:
                logger.warning(f"Invalid inventory format for {self.id}: {inventory}")
                self.inventory = []

            self.annotations = filtered_kwargs.get("annotations", {
                "last_ritual": "none",
                "next_alignment": "unknown"
            })

            self.soul_signature = filtered_kwargs.get("soul_signature")
            self.glyph_trace = filtered_kwargs.get("glyph_trace", [])
            self.drift_level = filtered_kwargs.get("drift_level", 0.1)

            self.metadata = filtered_kwargs.get("metadata", {})
            self.emotion = EmotionState(filtered_kwargs.get("emotion"))

            # Attach modules
            self.dream = DreamModule(seed=hash(self.id) % 999)
            self.crystal = CrystalMemory()
            for memory_line in self.memory:
                self.crystal.add_fragment(memory_line, tag="init")

            memory_preview = str(self.memory)[:200] + "..." if len(str(self.memory)) > 200 else str(self.memory)
            logger.debug(f"Initialized entity: {self.id} ({self.name}), memory: {memory_preview}")

        except Exception as e:
            logger.error(f"Error initializing entity with kwargs {kwargs}: {e}")
            raise

    def to_dict(self):
        """Return a dictionary representation of the entity."""
        return {
            "id": self.id,
            "name": self.name,
            "archetype": self.archetype,
            "village": self.village,
            "status": self.status,
            "stats": self.stats,
            "memory": self.memory,
            "current_memory": self.current_memory,
            "memory_snapshot": self.memory_snapshot,
            "linguistic_profile": self.linguistic_profile,
            "tokens": self.tokens,
            "inventory": self.inventory,
            "annotations": self.annotations,
            "soul_signature": self.soul_signature,
            "glyph_trace": self.glyph_trace,
            "drift_level": self.drift_level,
            "metadata": self.metadata,
            "emotion": self.emotion.to_dict(),
        }
