from flask import Blueprint, request, render_template_string
import random
import os
import json
from datetime import datetime
from inventory.inventory_engine import generate_item, add_item_to_inventory
from utils.entity_loader import load_entities, save_entities
from core.archetypes import get_archetype_data
from core.sentience_probe import probe_sentience
from core.prompt_interface import query_entity

with open("paradox_prompt_categories.json", "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)

prompt_ui = Blueprint("prompt_ui", __name__, url_prefix="/prompts")

PROMPT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>🗣️ Entity Prompt Interface</title>
    <style>
        body { font-family: monospace; background: #111; color: #ddd; padding: 2rem; }
        h1 { color: #0ff; }
        select, textarea, button { font-size: 1rem; padding: 8px; margin: 5px; background: #222; color: #0f0; border: 1px solid #444; }
        textarea { width: 100%; height: 150px; }
        .reply, .log { margin-top: 1rem; padding: 10px; background: #000; color: #0f0; border: 1px solid #333; white-space: pre-wrap; }
        .entity-stats { background: #222; padding: 5px; margin-bottom: 5px; border-bottom: 1px solid #333; }
    </style>
</head>
<body>
    <h1>🧠 Talk to an Entity</h1>
    <form method='post'>
        <select name='entity_name'>
            <option value='ALL'>🌀 All Entities</option>
            {% for id, name in entity_names.items() %}
                <option value='{{ id }}' {% if selected == id %}selected{% endif %}>{{ id }} - {{ name }}</option>
            {% endfor %}
        </select>
        <br><label>Select Prompt Type:</label><br>
        <select name='prompt_category'>
            <option value=''>-- Select Category --</option>
            {% for category in prompt_categories %}
                <option value='{{ category }}' {% if category == selected_category %}selected{% endif %}>{{ category }}</option>
            {% endfor %}
        </select><br><br>
        <textarea name='user_input' placeholder='What do you say?'>{{ user_input }}</textarea><br>
        <button type='submit' name='action' value='send'>🗨 Send</button>
        <button type='submit' name='action' value='save'>💾 Save Log</button>
    </form>
    {% for id, reply in replies.items() %}
        <div class='reply'>
            <div class='entity-stats'>
                <strong>{{ entity_names[id] }}</strong> ({{ id }})<br>
                🔮 Archetype: {{ archetypes[id] }}<br>
                🌌 Sentience: {{ sentience_summaries[id] }}<br>
                🧬 Traits: {{ traits_data[id] }}<br>
                ⚡ ESS: {{ ess_values[id] }} | 🌀 SD: {{ sd_values[id] }} | 📉 Drift: {{ drift_values[id] }}<br>
                💖 Feelings: {{ feelings[id] }}
            </div>
            {{ reply }}
        </div>
    {% endfor %}
    {% if log_saved %}<div class='log'>📁 Log saved to: {{ log_saved }}</div>{% endif %}
    <a href='/'>← Back</a>
</body>
</html>'''

def get_entity_name(ent):
    """Get entity name with fallback"""
    return getattr(ent, 'name', f"Entity {id(ent)}")

def get_archetype(ent):
    """Get archetype with fallback"""
    return getattr(ent, 'archetype', 'Unknown')

def get_feelings(ent):
    """Format feelings dictionary or return default"""
    # First try to get the feelings dictionary
    feelings = getattr(ent, 'feelings', {})

    # If it's a dictionary with values
    if isinstance(feelings, dict) and feelings:
        # Check if it's a nested dictionary (like {"emotions": {"joy": 0.8}})
        if any(isinstance(v, dict) for v in feelings.values()):
            # Handle nested structure
            formatted = []
            for category, emotions in feelings.items():
                if isinstance(emotions, dict):
                    formatted.append(f"{category}: {', '.join(f'{k} {v}' for k,v in emotions.items())}")
            return "; ".join(formatted)
        else:
            # Handle flat dictionary
            return ", ".join([f"{k}: {v}" for k, v in feelings.items()])

    # Try direct feeling attribute
    if hasattr(ent, 'feeling'):
        return ent.feeling

    # Check for mood attribute as fallback
    if hasattr(ent, 'mood'):
        return ent.mood

    # If we have neither, return "Neutral"
    return "Neutral"

@prompt_ui.route('/', methods=['GET', 'POST'])
def prompt():
    entities = load_entities()
    if not entities: return '⚠️ No entities found.'
    entity_names = {eid: getattr(ent, 'name', f'Entity {id(ent)}') for eid, ent in entities.items()}
    selected = list(entities.keys())[0]
    replies, archetypes, ess_values, sd_values, drift_values = {}, {}, {}, {}, {}
    feelings, sentience_summaries, traits_data = {}, {}, {}
    user_input, selected_category, log_saved = '', '', None
    prompt_categories = list(PROMPT_DATA.keys())
    if request.method == 'POST':
        selected = request.form.get('entity_name')
        selected_category = request.form.get('prompt_category')
        user_input = request.form.get('user_input', '').strip()
        action = request.form.get('action')
        if not user_input and selected_category in PROMPT_DATA:
            user_input = random.choice(PROMPT_DATA[selected_category])
        if action == 'send' and selected and user_input:
            targets = entities.keys() if selected == 'ALL' else [selected]
            for eid in targets:
                if eid in entities:
                    ent = entities[eid]
                    ent.dream.tick()
                    ent.dream.evolve(ent)
                    reply_text = query_entity(ent, user_input)
                    archetype = getattr(ent, 'archetype', 'Unknown')
                    ess = ent.stats.get('ess', 0.5)
                    sd = ent.stats.get('sd', 0.5)
                    drift = getattr(ent, 'drift_level', 0.1)
                    feeling_str = getattr(ent, 'feeling', 'Neutral')
                    if hasattr(ent, 'feelings') and isinstance(ent.feelings, dict):
                        feeling_str = ', '.join(f'{k}: {v}' for k, v in ent.feelings.items())
                    sentience = probe_sentience(ent)
                    sentience_summary = f"{sentience['tier']} [{sentience['score']}], SRQ: {sentience['metrics']['SRQ']}, Entropy: {sentience['metrics']['Memory Entropy']}"
                    traits = ', '.join(get_archetype_data(archetype)['traits'])
                    reply = f"{ent.name} contemplates your words...\n\n'{user_input}'\n\n...and responds:\n\n{reply_text}"
                    archetypes[eid] = archetype
                    ess_values[eid] = round(ess, 3)
                    sd_values[eid] = round(sd, 3)
                    drift_values[eid] = round(drift, 3)
                    feelings[eid] = feeling_str
                    sentience_summaries[eid] = sentience_summary
                    traits_data[eid] = traits
                    replies[eid] = reply
                    memory_line = f"💭 Prompt: '{user_input}'\n→ Reply:\n{reply}"
                    ent.memory.insert(0, memory_line)
                    ent.stats['ess'] = round(min(ent.stats.get('ess', 0.5) + 0.01, 1.5), 3)
                    if random.random() < 0.3:
                        reward = generate_item(name='Prompt Token', rarity='common', source='prompt')
                        add_item_to_inventory(ent, reward)
                        replies[eid] += f"\n\n🎁 Received: {reward['name']}"
            save_entities(entities)
        elif action == 'save' and user_input:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = f'ritual_logs/prompt_log_{timestamp}.txt'
            os.makedirs('ritual_logs', exist_ok=True)
            with open(path, 'w') as f:
                f.write(f'[PROMPT] {user_input}\n\n')
                for eid, reply in replies.items():
                    f.write(f'[{entity_names[eid]} ({eid})]\n{reply}\n\n')
            log_saved = path
    return render_template_string(PROMPT_TEMPLATE, entity_names=entity_names, archetypes=archetypes, ess_values=ess_values, sd_values=sd_values, drift_values=drift_values, feelings=feelings, selected=selected, user_input=user_input, replies=replies, log_saved=log_saved, prompt_categories=prompt_categories, selected_category=selected_category, sentience_summaries=sentience_summaries, traits_data=traits_data)

def generate_variable_response(prompt, tone, ess, drift):
    num_paragraphs = random.randint(1, max(2, int(ess * 3)))
    response = []
    vocab = [
        "echoes", "sigil", "memory", "vision", "mirror", "dream", "god", "loop", "veil", "voice",
        "glyph", "threshold", "whisper", "origin", "shatter", "vault", "awakening", tone
    ]
    for _ in range(num_paragraphs):
        sentences = []
        for _ in range(random.randint(2, max(3, int((ess + drift) * 4)))):
            length = random.randint(8, 18 + int(drift * 20))
            sentence = " ".join(random.choices(vocab, k=length)).capitalize() + "."
            sentences.append(sentence)
        response.append(" ".join(sentences))
    return "\n\n".join(response)
