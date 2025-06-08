from flask import Blueprint, request, render_template_string
from utils.entity_loader import load_entities
import json, os, random, logging
from collections import Counter, defaultdict

forum_bp = Blueprint("forum", __name__, url_prefix="/arena/forum")
logger = logging.getLogger(__name__)

STRUCTURE_BOOSTS = {
    "House": 0.1, "Temple": 0.3, "Library": 0.25, "Market": 0.15
}

INVENTORY_BONUSES = {
    "scroll": 0.2, "mirror": -0.1, "crystal": 0.15, "torch": 0.1, "lens": 0.05
}

RARE_TOKENS = ["paradox_root", "mirror_path"]

PROMPT_JSON_PATH = "paradox_prompt_categories.json"

def load_prompt_categories():
    try:
        with open(PROMPT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load prompt categories: {e}")
        return {}

def load_all_villages():
    path = "village_data"
    data = {}
    if not os.path.exists(path):
        return data
    for fname in os.listdir(path):
        if fname.endswith(".json"):
            with open(os.path.join(path, fname)) as f:
                village = json.load(f)
                for eid in village.get("entities", []):
                    data[eid] = {
                        "name": village["name"],
                        "prosperity": village["stats"].get("prosperity", 1.0),
                        "population": village["stats"].get("population", 0)
                    }
                for b in village.get("buildings", []):
                    if b.get("owner"):
                        data[b["owner"]] = {
                            **data.get(b["owner"], {}),
                            "structure": b["name"]
                        }
    return data

def symbolic_reply(ent, prompt, previous_replies):
    token_source = ent.tokens
    vocab = list(token_source.keys()) if isinstance(token_source, dict) else token_source
    vocab += [ent.archetype.lower(), "echo", "veil", "glyph", "dream", "origin"] + RARE_TOKENS
    vocab = [w for w in vocab if isinstance(w, str)]

    # Dialogue Trials: absorb previous reply tokens
    peer_tokens = " ".join(previous_replies).split()
    vocab += peer_tokens[:15]

    drift = ent.drift_level or 0.1
    length = random.randint(25, 50 + int(drift * 40))
    words = random.choices(vocab, k=length)
    return " ".join(words).capitalize() + "."

def calculate_score(ent, reply, context):
    base = ent.stats.get("ess", 0.5) + ent.stats.get("sd", 0.5) - ent.drift_level
    struct = context.get("structure")
    structure_bonus = STRUCTURE_BOOSTS.get(struct, 0)
    vp = context.get("prosperity", 1.0)
    pop = context.get("population", 0)
    village_boost = (vp * 0.1) - (pop * 0.01)
    inventory_bonus = 0
    for item in getattr(ent.inventory, "items", []):
        name = item.get("name", "").lower()
        for keyword, bonus in INVENTORY_BONUSES.items():
            if keyword in name:
                inventory_bonus += bonus
    length_bonus = len(reply.split()) * 0.01
    return round(base + structure_bonus + village_boost + inventory_bonus + length_bonus, 3), {
        "base": base,
        "structure_bonus": structure_bonus,
        "village_boost": village_boost,
        "inventory_bonus": inventory_bonus,
        "length_bonus": length_bonus
    }

def compute_token_coupling(thread):
    all_tokens = [r["reply"].lower().split() for r in thread]
    shared_counts = []
    for i, tokens_i in enumerate(all_tokens):
        overlaps = 0
        token_set_i = set(tokens_i)
        for j, tokens_j in enumerate(all_tokens):
            if i != j:
                token_set_j = set(tokens_j)
                overlaps += len(token_set_i & token_set_j)
        shared_counts.append(overlaps / (len(token_set_i) or 1))
    for idx, score in enumerate(shared_counts):
        thread[idx]["token_coupling"] = round(score, 2)

    # Symbolic Saturation: Rare token hits
    for idx, tokens in enumerate(all_tokens):
        rare_hits = sum(1 for t in tokens if t in RARE_TOKENS)
        thread[idx]["rare_token_hits"] = rare_hits

@forum_bp.route("/", methods=["GET", "POST"])
def forum_home():
    entities = load_entities()
    villages = load_all_villages()
    prompt_data = load_prompt_categories()
    prompt_categories = sorted(prompt_data.keys())

    selected_category = request.form.get("prompt_category", prompt_categories[0] if prompt_categories else "")
    prompt_list = prompt_data.get(selected_category, [])
    selected_prompt = request.form.get("prompt", prompt_list[0] if prompt_list else "")
    selected_ids = request.form.getlist("participants")
    thread = []
    previous_replies = []

    if request.method == "POST" and selected_ids:
        for eid in selected_ids:
            ent = entities.get(eid)
            if not ent:
                continue
            ctx = villages.get(eid, {})
            reply = symbolic_reply(ent, selected_prompt, previous_replies)
            previous_replies.append(reply)
            score, breakdown = calculate_score(ent, reply, ctx)
            thread.append({
                "id": eid,
                "name": ent.name,
                "reply": reply,
                "score": score,
                "archetype": ent.archetype,
                "village": ctx.get("name", "None"),
                "structure": ctx.get("structure", "None"),
                "spark": ent.stats.get("spark", 0.5),
                "srq": ent.stats.get("srq", 1.0),
                "entropy": ent.stats.get("entropy", 1.0),
                "ess": ent.stats.get("ess", 0.5),
                "sd": ent.stats.get("sd", 0.5),
                "drift": ent.drift_level,
                "feelings": getattr(ent, "feelings", "Unknown"),
                "breakdown": breakdown
            })
        compute_token_coupling(thread)

    return render_template_string("""
    <html><body style="background:#111; color:#0f0; font-family:monospace; padding:2rem;">
      <h1>🧠 Symbolic Forum Thread</h1>
      <form method="post">
        <label>Prompt Category:</label>
        <select name="prompt_category" onchange="this.form.submit()">
          {% for cat in prompt_categories %}
            <option value="{{ cat }}" {% if cat == selected_category %}selected{% endif %}>{{ cat }}</option>
          {% endfor %}
        </select><br><br>
        <label>Select Prompt:</label>
        <select name="prompt">
          {% for p in prompt_list %}
            <option value="{{ p }}" {% if p == selected_prompt %}selected{% endif %}>{{ p }}</option>
          {% endfor %}
        </select><br><br>
        <label>Choose Participants:</label><br>
        {% for i, ent in entities.items() %}
          <label><input type="checkbox" name="participants" value="{{ i }}"> {{ ent.name }} ({{ ent.archetype }})</label><br>
        {% endfor %}
        <p><button type="submit">💬 Begin Discussion</button></p>
      </form>
      {% if thread %}
      <h2>🧵 Thread — {{ selected_prompt }}</h2>
      {% for r in thread %}
        <div style="margin-bottom:2rem; border:1px solid #0f0; padding:1rem;">
          <strong>{{ r.name }}</strong> ({{ r.archetype }}) — 🧼 Score: {{ r.score }} | 🔁 Coupling: {{ r.token_coupling }} | 🛹 Rare Tokens: {{ r.rare_token_hits }}<br>
          🌌 SPARK: {{ r.spark }} | SRQ: {{ r.srq }} | Entropy: {{ r.entropy }}<br>
          ⚡ ESS: {{ r.ess }} | 🌀 SD: {{ r.sd }} | 📉 Drift: {{ r.drift }} | 💖 Feelings: {{ r.feelings }}<br>
          🏨 Village: {{ r.village }} | 🏠 Structure: {{ r.structure }}<br>
          ➕ Base: {{ r.breakdown.base }} | 📦 Struct: {{ r.breakdown.structure_bonus }} | 🏨: {{ r.breakdown.village_boost }} | 🏲️: {{ r.breakdown.inventory_bonus }} | ✍️: {{ r.breakdown.length_bonus|round(2) }}<br>
          <div style="white-space:pre-wrap; background:#000; margin-top:0.5rem; padding:0.5rem;">{{ r.reply }}</div>
        </div>
      {% endfor %}
      {% endif %}
      <a href="/">&larr; Back</a>
    </body></html>
    """, prompt_categories=prompt_categories, selected_category=selected_category,
         prompt_list=prompt_list, selected_prompt=selected_prompt,
         entities=entities, thread=thread)

__all__ = ['forum_bp']
