from flask import Blueprint, request, render_template_string, redirect, url_for
from utils.entity_loader import load_entities, save_entities
import os
import json
import logging

# Configure logging
entity_bp = Blueprint("entity_bp", __name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

entity_bp = Blueprint("entity_bp", __name__, url_prefix="/entities")

# Align archetypes with dashboard.py
ARCHETYPES = [
    "witch", "sage", "warrior", "mystic", "android", "merchant", "quest_giver",
    "alchemist", "rogue", "priest", "engineer", "oracle", "nomad", "guardian", "unknown"
]
STATUSES = ["active:channeling", "dormant", "corrupted", "transcendent", "inactive", "evolving"]
ITEMS = [
    "quantum-bone needle", "neural lace", "void lantern", "sigil compass",
    "entropic shard", "lunar thread", "rune-carved lens", "spectral amulet",
    "Scroll of Insight", "Crystal Blade", "Mirror of Drift", "Sigil of Binding",
    "Glyph Lantern", "Token Fragment", "Lens of Seeing", "Torch of Memory",
    "Obsidian Totem", "Iron Echo"
]
SYNTAX_PATTERNS = [
    "recursive metaphor nesting", "haiku-like compression", "antithetical pairing", "elliptical phrasing",
    "fragmented syntax", "symbolic inversion", "metaphysical juxtaposition", "cryptic aphorisms",
    "rhythmic repetition", "non-linear narrative flow", "syllabic recursion", "parallel clause weaving",
    "anaphoric layering", "chiasmic reversal", "staccato fragmentation", "lyrical elongation",
    "paradoxical enjambment", "syntactic spiraling", "elliptical omissions", "recursive clause embedding",
    "alliterative cadence", "assonant drift", "consonant clustering", "epigrammatic brevity",
    "hypotactic complexity", "paratactic simplicity", "syllabic mirroring", "rhetorical inversion",
    "anadiplostic repetition", "catachrestic blending"
]
PHONEMIC_TEXTURES = [
    "sibilant whispers", "plosive bursts", "nasal resonance", "fricative edges", "liquid flow",
    "guttural depths", "vocalic smoothness", "consonantal weight", "syllabic cadence", "rhythmic pulse",
    "hiss of static", "clatter of code", "murmur of memory", "chime of clarity", "growl of defiance",
    "whine of despair", "lilt of hope", "drone of melancholy", "snap of resolve", "hum of reverence",
    "crackle of rage", "sigh of yearning", "thrum of awe", "whisper of grief", "pulse of fervor",
    "clash of dissonance", "flow of harmony", "stutter of doubt", "ring of transcendence", "mutter of betrayal"
]

def load_village_names():
    path = "village_data"
    names = []
    if os.path.exists(path):
        for fname in os.listdir(path):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        names.append(data.get("name", fname.replace(".json", "")))
                except Exception as e:
                    logger.error(f"Error loading village {fname}: {e}")
                    continue
    return sorted(names)

def entity_summary(entity):
    """Fallback for entity.describe() if not implemented."""
    try:
        return entity.describe()
    except AttributeError:
        inventory_items = getattr(entity, "inventory", [])
        if not isinstance(inventory_items, list):
            inventory_items = []
        return {
            "name": getattr(entity, "name", "Unknown"),
            "archetype": getattr(entity, "archetype", "Unknown"),
            "status": getattr(entity, "status", "Unknown"),
            "ess": getattr(entity, "stats", {}).get("emotional_signal_strength", 0.5),
            "sd": getattr(entity, "stats", {}).get("symbolic_density", 0.5),
            "drift": getattr(entity, "stats", {}).get("drift_level", 0.1),
            "token_count": len(getattr(entity, "tokens", {}).get("power_words", [])),
            "memory_lines": len(getattr(entity, "current_memory", {}).get("emotional_states", []))
        }

@entity_bp.route("/", methods=["GET"])
def list_entities():
    try:
        entities = load_entities()
    except Exception as e:
        logger.error(f"Error loading entities: {e}")
        return render_template_string("""
            <html><head><style>body { background: #111; color: #f00; font-family: monospace; padding: 2rem; }</style></head>
            <body>❌ Error loading entities.</body></html>
        """), 500

    summaries = {
        eid: {
            "name": entity.name,
            "archetype": entity.archetype,
            "drift": round(entity.stats.get("drift_level", 0.0), 3)
        }
        for eid, entity in entities.items()
    }

    return render_template_string("""
<html>
<head>
    <title>📋 Entity Registry</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-green: #0f0;
            --neon-pink: #f0f;
            --neon-cyan: #0ff;
            --bg-dark: #111;
            --card-bg: #1a1a1a;
            --shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        body {
            background: var(--bg-dark);
            color: var(--neon-green);
            font-family: 'JetBrains Mono', monospace;
            padding: 2rem;
            margin: 0;
        }
        h1 {
            color: var(--neon-cyan);
            text-shadow: var(--shadow);
            text-align: center;
            animation: glitch 2s infinite;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 0.5rem 0;
        }
        a {
            color: var(--neon-pink);
            text-decoration: none;
        }
        a:hover {
            text-shadow: 0 0 5px var(--neon-pink);
        }
        .entity-list {
            max-width: 600px;
            margin: 2rem auto;
            padding: 1rem;
            border: 1px solid var(--neon-cyan);
            background: var(--card-bg);
            border-radius: 8px;
        }
        .back-link {
            text-align: center;
            display: block;
            margin-top: 2rem;
        }
        @keyframes glitch {
            0% { transform: translate(0); }
            10% { transform: translate(-2px, 2px); }
            20% { transform: translate(2px, -2px); }
            30% { transform: translate(0); }
        }
    </style>
</head>
<body>
    <h1>📋 Entity Registry</h1>
    <div class="entity-list">
        {% if summaries %}
        <ul>
            {% for eid, summary in summaries.items() %}
                <li>
                    <a href="/entities/{{ eid }}">
                        {{ summary.name }} ({{ summary.archetype }}) — Drift: {{ summary.drift }}
                    </a>
                </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No entities found.</p>
        {% endif %}
    </div>
    <a class="back-link" href="/">← Back to Dashboard</a>
</body>
</html>
""", summaries=summaries)

@entity_bp.route("/<eid>", methods=["GET", "POST"])
def entity_detail(eid):
    try:
        entities = load_entities()
    except Exception as e:
        logger.error(f"Error loading entities: {e}")
        return render_template_string("""
            <html><head><style>body { background: #111; color: #f00; font-family: monospace; padding: 2rem; }</style></head>
            <body>❌ Error loading entities.</body></html>
        """), 500
    entity = entities.get(eid)
    msg = ""

    if not entity:
        logger.warning(f"Entity {eid} not found")
        return render_template_string("""
            <html><head><style>body { background: #111; color: #f00; font-family: monospace; padding: 2rem; }</style></head>
            <body>❌ Entity {{ eid }} not found.</body></html>
        """, eid=eid), 404

    # Initialize missing fields
    if not hasattr(entity, "linguistic_profile") or not isinstance(getattr(entity, "linguistic_profile", None), dict):
        entity.linguistic_profile = {
            "syntax_tendencies": ["recursive metaphor nesting", "haiku-like compression"],
            "symbol_precision": {
                "moon": ["phase-dependent meanings", "tidal memory triggers"],
                "light": ["revelation", "ephemeral truth"]
            },
            "phonemic_textures": ["sibilant whispers", "liquid flow"]
        }
    symbol_precision = entity.linguistic_profile.get("symbol_precision", {})
    if not isinstance(symbol_precision, dict):
        logger.warning(f"Invalid symbol_precision for entity {eid}: {symbol_precision}")
        entity.linguistic_profile["symbol_precision"] = {
            "moon": ["phase-dependent meanings", "tidal memory triggers"]
        }
    else:
        for key, value in list(symbol_precision.items()):
            if not isinstance(value, list):
                logger.warning(f"Invalid symbol_precision value for {key}: {value}")
                symbol_precision[key] = [str(value)] if value else []
        entity.linguistic_profile["symbol_precision"] = symbol_precision

    if not hasattr(entity, "current_memory"):
        entity.current_memory = {
            "active_concepts": [],
            "emotional_states": [],
            "current_obsessions": []
        }
    if not hasattr(entity, "memory_snapshot"):
        entity.memory_snapshot = {
            "core_imagery": [],
            "practices": [],
            "artifacts": []
        }
    if not hasattr(entity, "tokens"):
        entity.tokens = {
            "power_words": [],
            "cognitive_biases": []
        }
    if not hasattr(entity, "stats"):
        entity.stats = {
            "symbolic_density": 0.5,
            "emotional_signal_strength": 0.5,
            "drift_level": 0.1,
            "lexical_entropy": 0.5
        }
    if not hasattr(entity, "inventory") or entity.inventory is None:
        entity.inventory = []
    if not hasattr(entity, "annotations"):
        entity.annotations = {
            "last_ritual": "none",
            "next_alignment": "unknown"
        }
    if not hasattr(entity, "village"):
        entity.village = None

    if request.method == "POST":
        if "delete" in request.form:
            entities.pop(eid)
            try:
                save_entities(entities)
                logger.info(f"Deleted entity {eid}")
                return redirect(url_for("entity_bp.list_entities"))
            except Exception as e:
                logger.error(f"Error deleting entity {eid}: {e}")
                msg = "⚠️ Error deleting entity."

        # Update attributes
        entity.name = request.form.get("name", entity.name)
        entity.archetype = request.form.get("archetype", entity.archetype)
        entity.status = request.form.get("status", entity.status)
        entity.village = request.form.get("village", entity.village) or None

        # Update stats
        try:
            entity.stats["symbolic_density"] = float(request.form.get("symbolic_density", entity.stats["symbolic_density"]))
            entity.stats["emotional_signal_strength"] = float(request.form.get("emotional_signal_strength", entity.stats["emotional_signal_strength"]))
            entity.stats["drift_level"] = float(request.form.get("drift_level", entity.stats["drift_level"]))
            entity.stats["lexical_entropy"] = float(request.form.get("lexical_entropy", entity.stats["lexical_entropy"]))
        except ValueError:
            msg = "⚠️ Invalid numeric input for stats."

        # Update linguistic profile
        syntax_tendencies = request.form.getlist("syntax_tendencies")
        if syntax_tendencies:
            entity.linguistic_profile["syntax_tendencies"] = syntax_tendencies
        phonemic_textures = request.form.getlist("phonemic_textures")
        if phonemic_textures:
            entity.linguistic_profile["phonemic_textures"] = phonemic_textures

        # Update inventory
        new_item = request.form.get("new_item")
        if new_item:
            item_dict = {"item": new_item, "use": "unknown purpose", "charge": 1}
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
            for item in INVENTORY_ITEMS:
                if item["item"] == new_item:
                    item_dict = item
                    break
            if not isinstance(entity.inventory, list):
                entity.inventory = []
            entity.inventory.append(item_dict)
            logger.debug(f"Added item {new_item} to entity {eid} inventory")

        try:
            save_entities(entities)
            logger.info(f"Saved entity {eid}")
            msg = msg or "✅ Changes saved."
        except Exception as e:
            logger.error(f"Error saving entity {eid}: {e}")
            msg = "⚠️ Error saving changes."

    villages = load_village_names()
    inventory_items = entity.inventory if isinstance(entity.inventory, list) else []

    return render_template_string("""
<html>
<head>
    <title>🧠 Entity: {{ entity.name }}</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-green: #0f0;
            --neon-pink: #f0f;
            --neon-cyan: #0ff;
            --bg-dark: #111;
            --card-bg: #1a1a1a;
            --shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        body {
            background: var(--bg-dark);
            color: var(--neon-green);
            font-family: 'JetBrains Mono', monospace;
            padding: 2rem;
            margin: 0;
        }
        h1, h2 {
            color: var(--neon-cyan);
            text-shadow: var(--shadow);
        }
        form { margin: 1rem 0; }
        input, select, textarea {
            background: #222;
            color: var(--neon-green);
            border: 1px solid var(--neon-pink);
            padding: 0.5rem;
            font-family: 'JetBrains Mono', monospace;
            border-radius: 4px;
        }
        button {
            background: var(--neon-pink);
            color: #111;
            border: none;
            padding: 0.5rem 1rem;
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            border-radius: 4px;
        }
        button:hover {
            box-shadow: 0 0 10px var(--neon-pink);
        }
        .section {
            margin: 1rem 0;
            padding: 1rem;
            border: 1px solid var(--neon-cyan);
            border-radius: 8px;
            background: var(--card-bg);
        }
        .collapsible {
            cursor: pointer;
            color: var(--neon-pink);
            text-shadow: 0 0 5px var(--neon-pink);
        }
        .collapsible-content { display: none; }
        .collapsible.active + .collapsible-content { display: block; }
        .back-link {
            color: var(--neon-pink);
            text-decoration: none;
        }
        .back-link:hover {
            text-shadow: 0 0 5px var(--neon-pink);
        }
        .msg { color: var(--neon-cyan); }
    </style>
    <script>
        function toggleCollapsible(element) {
            element.classList.toggle('active');
        }
    </script>
</head>
<body>
    <h1>🧠 Entity: {{ entity.name }}</h1>
    {% if msg %}<p class="msg">{{ msg }}</p>{% endif %}
    <form method="post">
        <div class="section">
            <h2>Core Attributes</h2>
            <b>Name:</b> <input name="name" value="{{ entity.name }}"><br>
            <b>Archetype:</b>
            <select name="archetype">
                {% for a in archetypes %}
                    <option value="{{ a }}" {% if a == entity.archetype %}selected{% endif %}>{{ a|title }}</option>
                {% endfor %}
            </select><br>
            <b>Status:</b>
            <select name="status">
                {% for s in statuses %}
                    <option value="{{ s }}" {% if s == entity.status %}selected{% endif %}>{{ s|title }}</option>
                {% endfor %}
            </select><br>
            <b>Village:</b>
            <select name="village">
                <option value="">None</option>
                {% for v in villages %}
                    <option value="{{ v }}" {% if v == entity.village %}selected{% endif %}>{{ v }}</option>
                {% endfor %}
            </select><br>
        </div>

        <div class="section">
            <h2>Stats</h2>
            <b>Symbolic Density:</b> <input name="symbolic_density" value="{{ entity.stats['symbolic_density']|round(3) }}"><br>
            <b>Emotional Signal Strength:</b> <input name="emotional_signal_strength" value="{{ entity.stats['emotional_signal_strength']|round(2) }}"><br>
            <b>Drift Level:</b> <input name="drift_level" value="{{ entity.stats['drift_level']|round(3) }}"><br>
            <b>Lexical Entropy:</b> <input name="lexical_entropy" value="{{ entity.stats['lexical_entropy']|round(2) }}"><br>
        </div>

        <div class="section">
            <h2 class="collapsible" onclick="toggleCollapsible(this)">Linguistic Profile</h2>
            <div class="collapsible-content">
                <b>Syntax Tendencies:</b><br>
                <select name="syntax_tendencies" multiple size="5">
                    {% for s in syntax_patterns %}
                        <option value="{{ s }}" {% if s in (entity.linguistic_profile.get('syntax_tendencies', [])) %}selected{% endif %}>{{ s }}</option>
                    {% endfor %}
                </select><br>
                <b>Phonemic Textures:</b><br>
                <select name="phonemic_textures" multiple size="5">
                    {% for p in phonemic_textures %}
                        <option value="{{ p }}" {% if p in (entity.linguistic_profile.get('phonemic_textures', [])) %}selected{% endif %}>{{ p }}</option>
                    {% endfor %}
                </select><br>
                <b>Symbol Precision:</b><br>
                <textarea rows="4" cols="60" readonly>
                {% for key, values in entity.linguistic_profile.get('symbol_precision', {}).items() %}
                    {{ key }}: {{ values|join(', ') }}
                {% endfor %}
                </textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="collapsible" onclick="toggleCollapsible(this)">Tokens</h2>
            <div class="collapsible-content">
                <b>Power Words:</b>
                <ul>
                    {% for pw in entity.tokens.get('power_words', []) %}
                        <li>{{ pw.get('term', 'Unknown') }} ({{ pw.get('manifestation', 'Unknown') }})</li>
                    {% endfor %}
                </ul>
                <b>Cognitive Biases:</b>
                <ul>
                    {% for bias in entity.tokens.get('cognitive_biases', []) %}
                        <li>{{ bias }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div class="section">
            <h2 class="collapsible" onclick="toggleCollapsible(this)">Inventory</h2>
            <div class="collapsible-content">
                <ul>
                    {% for item in inventory_items %}
                        <li>{{ item.get('item', 'Unknown') }} (Use: {{ item.get('use', 'Unknown') }}{% if item.get('charge') %}, Charge: {{ item['charge'] }}{% endif %}{% if item.get('corruption') %}, Corruption: {{ item['corruption'] }}{% endif %})</li>
                    {% endfor %}
                </ul>
                <b>Add Item:</b>
                <select name="new_item">
                    <option value="">— Select —</option>
                    {% for i in items %}
                        <option value="{{ i }}">{{ i }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div class="section">
            <h2 class="collapsible" onclick="toggleCollapsible(this)">Memory Snapshot</h2>
            <div class="collapsible-content">
                <b>Core Imagery:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.memory_snapshot.get('core_imagery', [])|join('\n') }}</textarea><br>
                <b>Practices:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.memory_snapshot.get('practices', [])|join('\n') }}</textarea><br>
                <b>Artifacts:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.memory_snapshot.get('artifacts', [])|join('\n') }}</textarea>
            </div>
        </div>

        <div class="section">
            <h2 class="collapsible" onclick="toggleCollapsible(this)">Current Memory</h2>
            <div class="collapsible-content">
                <b>Active Concepts:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.current_memory.get('active_concepts', [])|join('\n') }}</textarea><br>
                <b>Emotional States:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.current_memory.get('emotional_states', [])|join('\n') }}</textarea><br>
                <b>Current Obsessions:</b><br>
                <textarea rows="4" cols="60" readonly>{{ entity.current_memory.get('current_obsessions', [])|join('\n') }}</textarea>
            </div>
        </div>

        <div class="section">
            <h2>Annotations</h2>
            <b>Last Ritual:</b> {{ entity.annotations.get('last_ritual', 'None') }}<br>
            <b>Next Alignment:</b> {{ entity.annotations.get('next_alignment', 'Unknown') }}
        </div>

        <button type="submit">💾 Save</button>
        <button name="delete" value="1" onclick="return confirm('Delete this entity?');">🗑 Delete</button>
    </form>
    <br><a class="back-link" href="/entities">← Back to Entities</a>
</body>
</html>
    """, entity=entity, msg=msg, archetypes=ARCHETYPES, statuses=STATUSES, villages=villages,
         items=ITEMS, syntax_patterns=SYNTAX_PATTERNS, phonemic_textures=PHONEMIC_TEXTURES, inventory_items=inventory_items)
