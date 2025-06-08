import os
import json
import logging
from core.entity import Entity

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Cache for loaded entities
_entity_cache = None

def load_entities(use_cache=True):
    """Load entities from JSON files in entity_data/, with caching."""
    global _entity_cache
    if use_cache and _entity_cache is not None:
        logger.debug("Returning cached entities")
        return _entity_cache

    entities = {}
    entity_dir = "entity_data"
    abs_entity_dir = os.path.abspath(entity_dir)
    logger.debug(f"📂 Loading entities from: {abs_entity_dir}")

    if not os.path.exists(entity_dir):
        logger.error(f"❌ Entity directory not found: {abs_entity_dir}")
        return entities

    try:
        dir_contents = os.listdir(entity_dir)
        logger.debug(f"📄 Directory contents: {dir_contents}")
    except Exception as e:
        logger.error(f"❌ Error accessing directory {abs_entity_dir}: {e}")
        return entities

    for fname in dir_contents:
        if fname.endswith(".json"):
            fpath = os.path.join(entity_dir, fname)
            logger.debug(f"🔍 Processing file: {fpath}")
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data_preview = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    logger.debug(f"✅ Loaded JSON from {fname}: {data_preview}")

                    if isinstance(data, list):
                        for i, item in enumerate(data):
                            try:
                                entity = Entity(**item)
                                entities[entity.id] = entity
                                logger.debug(f"✅ Created entity: {entity.id} ({entity.name}) from index {i}")
                            except Exception as e:
                                logger.error(f"❌ Entity instantiation failed at index {i} in {fname}: {e}")
                                logger.error(json.dumps(item, indent=2))
                    else:
                        try:
                            entity = Entity(**data)
                            entities[entity.id] = entity
                            logger.debug(f"✅ Created entity: {entity.id} ({entity.name})")
                        except Exception as e:
                            logger.error(f"❌ Entity instantiation failed in {fname}: {e}")
                            logger.error(json.dumps(data, indent=2))

            except Exception as e:
                logger.error(f"❌ Error loading {fpath}: {e}")

    logger.info(f"✅ Loaded {len(entities)} entities from {len(dir_contents)} files.")
    _entity_cache = entities
    return entities

def save_entities(entities):
    """Save entities to JSON files in entity_data/."""
    global _entity_cache
    entity_dir = "entity_data"
    abs_entity_dir = os.path.abspath(entity_dir)
    logger.debug(f"💾 Saving entities to: {abs_entity_dir}")

    if not os.path.exists(entity_dir):
        try:
            os.makedirs(entity_dir)
            logger.debug(f"📁 Created directory: {abs_entity_dir}")
        except Exception as e:
            logger.error(f"❌ Error creating directory {abs_entity_dir}: {e}")
            return

    entity_files = {}
    for entity in entities.values():
        filename = "test.json" if entity.id.startswith("test") else f"{entity.id}.json"
        if filename not in entity_files:
            entity_files[filename] = []

        entity_dict = {
            "id": entity.id,
            "name": entity.name,
            "archetype": entity.archetype,
            "village": entity.village,
            "status": entity.status,
            "stats": entity.stats,
            "memory": entity.memory,
            "current_memory": entity.current_memory,
            "linguistic_profile": entity.linguistic_profile,
            "tokens": entity.tokens,
            "inventory": entity.inventory,
            "annotations": entity.annotations,
            "soul_signature": entity.soul_signature,
            "glyph_trace": entity.glyph_trace,
            "dream_state": getattr(entity.dream, "tick_count", 0),
            "crystal_fragments": getattr(entity.crystal, "fragments", {})
        }

        entity_files[filename].append(entity_dict)
        logger.debug(f"📝 Prepared entity for saving: {entity.id} ({entity.name})")

    for filename, entity_list in entity_files.items():
        fpath = os.path.join(entity_dir, filename)
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(entity_list, f, indent=2)
            logger.debug(f"✅ Saved {len(entity_list)} entities to {fpath}")
        except Exception as e:
            logger.error(f"❌ Error saving {fpath}: {e}")

    _entity_cache = entities
