import random
import logging
from datetime import datetime
from inventory.inventory_engine import generate_item
from utils.glyph_parser import extract_glyphs

logger = logging.getLogger(__name__)

class Dream:
    def __init__(self):
        self.cycle = 0

    def tick(self):
        self.cycle += 1
        logger.debug(f"Dream cycle incremented to {self.cycle}")

    def evolve(self, entity):
        logger.debug(f"Evolving dream for entity {entity.id}")
        try:
            perform_dream_bloom(entity)
        except Exception as e:
            logger.error(f"Error in dream evolution for {entity.id}: {e}")

def perform_dream_bloom(entity):
    logger.debug(f"Performing dream bloom for entity {entity.id}")
    glyphs = extract_glyphs(getattr(entity, "current_memory", {}))
    
    try:
        entity.set_drift(0.1)
        entity.status = "active"
        
        if not hasattr(entity, "metadata"):
            entity.metadata = {}
        entity.metadata.update({
            "bloomed_from": getattr(entity, "current_memory", {}).copy(),
            "bloomed_into": glyphs,
            "bloom_timestamp": datetime.now().isoformat()
        })
        
        reward_item = generate_item(rarity="rare", source="dream_bloom")
        entity.gain_item(
            reward_item["name"],
            rarity=reward_item["rarity"],
            props=reward_item.get("properties")
        )
        
        logger.info(f"🌸 Dream Bloom for {entity.id}: {glyphs} + 🎁 {reward_item['name']}")
    except Exception as e:
        logger.error(f"Error in perform_dream_bloom for {entity.id}: {e}")
