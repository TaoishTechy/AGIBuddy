import random
import uuid
from datetime import datetime

# === ITEM POOLS ===
ITEM_TEMPLATES = [
    {"name": "Sigil of Grace", "rarity": "rare"},
    {"name": "Whisper Glyph", "rarity": "common"},
    {"name": "Dream Mirror", "rarity": "uncommon"},
    {"name": "Crystal Thread", "rarity": "rare"},
    {"name": "Echo Seed", "rarity": "common"}
]

ITEM_RARITIES = ["common", "uncommon", "rare", "epic", "mythic"]
ITEM_TYPES = ["sigil", "artifact", "glyph", "relic", "potion", "fragment", "scroll"]

ITEM_DESCRIPTIONS = {
    "sigil": ["Mark of Veil", "Echo Seal", "Glyphtrace"],
    "artifact": ["Ashen Lens", "Clock of Stars", "Wyrmcore"],
    "glyph": ["Glyph of Memory", "Glyph of Drift", "Glyph of Soul"],
    "relic": ["Coven Ring", "Chalice of Light", "Whisper Bone"],
    "potion": ["Essence Flask", "Drift Tonic", "Veilwater"],
    "fragment": ["Crystal Shard", "Dream Fragment", "Sigil Fracture"],
    "scroll": ["Scroll of Reflection", "Scroll of Reweaving", "Scroll of Bloom"]
}

# === CLASSES ===

class InventoryItem:
    def __init__(self, name=None, rarity="common", item_type=None, source="unknown", properties=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name or self.generate_name(item_type)
        self.rarity = rarity
        self.type = item_type or random.choice(ITEM_TYPES)
        self.source = source
        self.properties = properties or {}
        self.acquired = datetime.now().isoformat()

    def generate_name(self, item_type=None):
        item_type = item_type or random.choice(ITEM_TYPES)
        descriptor = random.choice(ITEM_DESCRIPTIONS.get(item_type, ["Mysterious Item"]))
        return f"{descriptor} [{item_type.title()}]"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "rarity": self.rarity,
            "source": self.source,
            "properties": self.properties,
            "acquired": self.acquired
        }

    @staticmethod
    def from_dict(data):
        return InventoryItem(
            name=data.get("name"),
            rarity=data.get("rarity", "common"),
            item_type=data.get("type"),
            source=data.get("source", "unknown"),
            properties=data.get("properties", {})
        )


class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        if isinstance(item, InventoryItem):
            item_dict = item.to_dict()
        elif isinstance(item, dict):
            item_dict = item
        else:
            raise TypeError("Item must be dict or InventoryItem.")

        if 'name' not in item_dict:
            item_dict['name'] = 'Unnamed'
        if 'rarity' not in item_dict:
            item_dict['rarity'] = 'common'
        if len(self.items) >= 50:
            return '⚠️ Inventory full'
        self.items.append(item_dict)
        return f"✅ Added {item_dict['name']}"

    def remove_item_by_id(self, item_id: str):
        self.items = [item for item in self.items if item.get("id") != item_id]

    def has_item(self, name: str) -> bool:
        return any(name.lower() in item.get("name", "").lower() for item in self.items)

    def list_items(self):
        return self.items

    def to_dict(self):
        return {"items": self.items}

    @staticmethod
    def from_dict(data):
        inv = Inventory()
        for item_data in data.get("items", []):
            inv.add_item(item_data)
        return inv


# === UTILITIES ===

def generate_item(source="system", rarity=None, name=None):
    """Generate raw dictionary item for flexibility."""
    item = {
        "id": str(uuid.uuid4())[:8],
        "name": name or random.choice(ITEM_TEMPLATES)["name"],
        "type": random.choice(ITEM_TYPES),
        "rarity": rarity or random.choice(["common", "uncommon", "rare"]),
        "source": source,
        "timestamp": uuid.uuid1().time
    }
    return item


def add_item_to_inventory(entity, item):
    """
    Add item to an entity's inventory.
    Supports:
      - Entity object with list-based .inventory
      - Entity with Inventory object
      - Entity represented as dict
    """
    if hasattr(entity, 'inventory'):
        if isinstance(entity.inventory, Inventory):
            return entity.inventory.add_item(item)
        elif isinstance(entity.inventory, list):
            if isinstance(item, InventoryItem):
                item = item.to_dict()
            entity.inventory.append(item)
            return f"✅ Added {item['name']}"
        else:
            raise TypeError("Entity inventory must be a list or Inventory object.")
    elif isinstance(entity, dict):
        entity.setdefault("inventory", [])
        if isinstance(item, InventoryItem):
            item = item.to_dict()
        entity["inventory"].append(item)
        return f"✅ Added {item['name']}"
    else:
        raise TypeError("Unsupported entity format for inventory update.")
