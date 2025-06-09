import os
import json
import zipfile
from datetime import datetime
from flask import Flask, render_template_string, request
import logging
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App Setup and Blueprints
from dashboard_entity_manager import entity_bp
from dashboard_arena_forum import forum_bp as forum_arena_bp
from dashboard_prompt_extension import prompt_ui
from village_dashboard import village_bp
from world_map import world_bp
from utils.entity_loader import load_entities, save_entities

app = Flask(__name__)
app.register_blueprint(entity_bp, url_prefix="/entities")
app.register_blueprint(forum_arena_bp, url_prefix="/arena/forum")
app.register_blueprint(prompt_ui, url_prefix="/prompts")
app.register_blueprint(village_bp, url_prefix="/village")
app.register_blueprint(world_bp, url_prefix="/world")

# Comprehensive archetype list
ARCHETYPES = [
    "witch", "sage", "warrior", "mystic", "android", "merchant", "quest_giver",
    "alchemist", "rogue", "priest", "engineer", "oracle", "nomad", "guardian"
]

# Utility Functions
def read_lines_with_fallback(path):
    encodings = ["utf-8", "latin-1", "utf-16"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return [line.strip() for line in f if line.strip()], enc
        except UnicodeDecodeError:
            continue
    logger.warning(f"Failed to read {path} with any encoding")
    return [], None

_village_cache = None
def load_village_data():
    global _village_cache
    if _village_cache is not None:
        logger.debug("Using cached village data")
        return _village_cache

    path = "village_data"
    villages = []
    if not os.path.exists(path):
        logger.warning("village_data/ directory not found")
        return villages

    logger.debug(f"Checking village_data path: {os.path.abspath(path)}")
    for fname in os.listdir(path):
        if fname.endswith(".json"):
            fpath = os.path.join(path, fname)
            logger.debug(f"Processing file: {fpath}")
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    raw_content = f.read()
                    logger.debug(f"Raw content of {fname}: {raw_content}")
                    data = json.loads(raw_content)
                    data.setdefault("name", fname.replace(".json", ""))
                    try:
                        pop = data.get("stats", {}).get("population", data.get("population", 0))
                        data["population"] = int(pop)
                        data["stability"] = float(data.get("stability", 0.0))
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Invalid population/stability in {fname}: {e}")
                        data["population"] = 0
                        data["stability"] = 0.0
                    if not isinstance(data, dict):
                        logger.error(f"Invalid JSON structure in {fname}: {data}")
                        continue
                    villages.append(data)
                    logger.debug(f"Loaded village: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"Malformed JSON in {fname}: {e}")
            except Exception as e:
                logger.error(f"Error loading {fname}: {e}")
    _village_cache = villages
    return villages

def get_world_stats():
    try:
        from world_map import get_world_metrics
        return get_world_metrics()
    except (ImportError, AttributeError):
        logger.debug("Using enhanced mock world stats")
        return {
            "regions": 6,
            "nodes": 25,
            "connections": 40,
            "active_nodes": 15,
            "energy_flow": 78.5
        }

# Symbolic Training
@app.route("/train")
def symbolic_training():
    logger.info("Starting symbolic training")
    entities = load_entities()
    training_logs = []
    training_path = "training_data"
    trained = 0

    def flatten_json(data):
        lines = []
        if isinstance(data, dict):
            for value in data.values():
                lines += flatten_json(value)
        elif isinstance(data, list):
            for item in data:
                lines += flatten_json(item)
        else:
            lines.append(str(data))
        return [line.strip() for line in lines if line.strip()]

    def extract_file_lines(fpath):
        ext = os.path.splitext(fpath)[1].lower()
        logger.debug(f"Processing file: {fpath}")
        try:
            if ext in [".txt", ".md"]:
                return read_lines_with_fallback(fpath)
            elif ext == ".json":
                with open(fpath, "r", encoding="utf-8") as f:
                    return flatten_json(json.load(f)), "utf-8"
            elif ext == ".pdf":
                from PyPDF2 import PdfReader
                pdf = PdfReader(fpath)
                lines = []
                for page in pdf.pages:
                    content = page.extract_text()
                    if content:
                        lines.extend([line.strip() for line in content.splitlines() if line.strip()])
                return lines, "pdf"
        except Exception as e:
            logger.error(f"Error processing {fpath}: {e}")
            return [], str(e)
        return [], None

    if not os.path.exists(training_path):
        logger.warning("No training_data/ directory found")
        training_logs.append("⚠️ No training_data/ directory found.")
    else:
        for fname in os.listdir(training_path):
            fpath = os.path.join(training_path, fname)
            ext = os.path.splitext(fname)[1].lower()

            if ext == ".zip":
                try:
                    with zipfile.ZipFile(fpath, "r") as zipf:
                        extract_dir = os.path.join(training_path, "_unzipped")
                        zipf.extractall(extract_dir)
                        for inner in os.listdir(extract_dir):
                            inner_path = os.path.join(extract_dir, inner)
                            lines, enc = extract_file_lines(inner_path)
                            if lines:
                                for ent in entities.values():
                                    if not hasattr(ent, "memory"):
                                        ent.memory = []
                                    ent.memory.extend(lines)
                                    ent.stats["emotional_signal_strength"] = round(
                                        min(ent.stats.get("emotional_signal_strength", 0.5) + 0.01, 1.5), 3
                                    )
                                training_logs.append(f"📦 {inner} ({len(lines)} lines, {enc})")
                                trained += 1
                            else:
                                training_logs.append(f"❌ {inner}: unreadable ({enc})")
                except Exception as e:
                    logger.error(f"Error processing zip {fname}: {e}")
                    training_logs.append(f"❌ {fname}: zip error ({str(e)})")
            elif ext in [".txt", ".md", ".json", ".pdf"]:
                lines, enc = extract_file_lines(fpath)
                if lines:
                    for ent in entities.values():
                        if not hasattr(ent, "memory"):
                            ent.memory = []
                        ent.memory.extend(lines)
                        ent.stats["emotional_signal_strength"] = round(
                            min(ent.stats.get("emotional_signal_strength", 0.5) + 0.01, 1.5), 3
                        )
                    training_logs.append(f"📚 {fname} ({len(lines)} lines, {enc})")
                    trained += 1
                else:
                    training_logs.append(f"❌ {fname}: unreadable ({enc})")

    try:
        save_entities(entities)
        logger.info(f"Saved {len(entities)} entities after training")
    except Exception as e:
        logger.error(f"Error saving entities: {e}")
        training_logs.append(f"⚠️ Error saving entities: {str(e)}")

    return render_template_string("""
    <html>
    <head>
        <title>🧠 Symbolic Training</title>
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
            }
            h1 {
                color: var(--neon-cyan);
                text-shadow: var(--shadow);
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
            @keyframes glitch {
                0% { transform: translate(0); }
                10% { transform: translate(-2px, 2px); }
                20% { transform: translate(2px, -2px); }
                30% { transform: translate(0); }
            }
        </style>
    </head>
    <body>
        <h1>🧠 Symbolic Training Complete</h1>
        {% if logs %}
            <ul>{% for line in logs %}<li>{{ line }}</li>{% endfor %}</ul>
        {% else %}
            <p>⚠️ No training files processed.</p>
        {% endif %}
        <p>Trained {{ count }} entity memories.</p>
        <a href="/">← Back to Dashboard</a>
    </body>
    </html>
    """, logs=training_logs, count=trained)

# Homepage Dashboard
@app.route("/")
def index():
    logger.info("Loading dashboard")
    entities = load_entities()
    villages = load_village_data()
    world_stats = get_world_stats()

    # Entity Metrics
    entity_count = len(entities)
    archetype_counts = Counter(getattr(ent, "archetype", "unknown") for ent in entities.values())
    # Initialize archetypes with all defined ones plus "unknown"
    archetypes = {arch: 0 for arch in ARCHETYPES + ["unknown"]}
    # Update with actual counts
    for arch, count in archetype_counts.items():
        archetypes[arch] = count
        if arch not in ARCHETYPES and arch != "unknown":
            logger.debug(f"Found undefined archetype: {arch}")

    statuses = Counter(getattr(ent, "status", "unknown") for ent in entities.values())
    avg_stats = {
        "symbolic_density": 0,
        "emotional_signal_strength": 0,
        "drift_level": 0,
        "lexical_entropy": 0
    }
    total_memory_lines = sum(len(getattr(ent, "memory", [])) for ent in entities.values())
    avg_memory_lines = round(total_memory_lines / entity_count, 1) if entity_count else 0

    for ent in entities.values():
        for stat in avg_stats:
            avg_stats[stat] += ent.stats.get(stat, 0)

    for stat in avg_stats:
        avg_stats[stat] = round(avg_stats[stat] / entity_count, 3) if entity_count else 0

    # Village Metrics
    village_count = len(villages)
    total_population = sum(v.get("population", 0) for v in villages)
    avg_stability = round(sum(v.get("stability", 0.0) for v in villages) / village_count, 2) if village_count else 0
    avg_population = round(total_population / village_count, 1) if village_count else 0

    # Chart Data
    archetype_labels = list(archetypes.keys())
    archetype_values = list(archetypes.values())
    status_labels = list(statuses.keys())
    status_values = list(statuses.values())

    return render_template_string("""
    <html>
    <head>
        <title>🔥 AGIBuddy Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                overflow-x: hidden;
            }
            h1 {
                color: var(--neon-cyan);
                text-shadow: var(--shadow);
                text-align: center;
                animation: glitch 2s infinite;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                display: grid;
                gap: 1rem;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }
            .card {
                background: var(--card-bg);
                border: 1px solid var(--neon-cyan);
                border-radius: 8px;
                padding: 1rem;
                box-shadow: var(--shadow);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 0 20px var(--neon-cyan);
            }
            .card h2 {
                color: var(--neon-pink);
                margin-top: 0;
                text-shadow: 0 0 5px var(--neon-pink);
            }
            .metric {
                margin: 0.5rem 0;
                font-size: 0.9rem;
            }
            .collapsible {
                cursor: pointer;
                color: var(--neon-pink);
                font-weight: bold;
                transition: text-shadow 0.3s;
            }
            .collapsible:hover {
                text-shadow: 0 0 5px var(--neon-pink);
            }
            .collapsible-content {
                display: none;
            }
            .collapsible.active + .collapsible-content {
                display: block;
            }
            a {
                color: var(--neon-pink);
                text-decoration: none;
                transition: text-shadow 0.3s;
            }
            a:hover {
                text-shadow: 0 0 5px var(--neon-pink);
            }
            canvas {
                max-width: 100%;
                margin: 1rem 0;
            }
            .nav-links {
                text-align: center;
                margin: 2rem 0;
            }
            .nav-links a {
                margin: 0 1rem;
                font-size: 1.2rem;
            }
            @keyframes glitch {
                0% { transform: translate(0); }
                10% { transform: translate(-2px, 2px); }
                20% { transform: translate(2px, -2px); }
                30% { transform: translate(0); }
            }
            @media (max-width: 600px) {
                .container { grid-template-columns: 1fr; }
                h1 { font-size: 1.5rem; }
                .nav-links a { display: block; margin: 0.5rem 0; }
            }
        </style>
    </head>
    <body>
        <h1>🔥 AGIBuddy Dashboard</h1>
        <div class="nav-links">
            <a href="/entities">📋 Entities</a>
            <a href="/arena/forum">⚔️ Arena</a>
            <a href="/prompts">🗣️ Prompts</a>
            <a href="/village">🏘️ Village</a>
            <a href="/world">🌍 World</a>
            <a href="/train">🧠 Training</a>
        </div>
        <div class="container">
            <!-- Entity Metrics -->
            <div class="card">
                <h2>🧠 Entities ({{ entity_count }})</h2>
                <div class="metric">Avg Symbolic Density: {{ avg_stats.symbolic_density }}</div>
                <div class="metric">Avg Emotional Strength: {{ avg_stats.emotional_signal_strength }}</div>
                <div class="metric">Avg Drift Level: {{ avg_stats.drift_level }}</div>
                <div class="metric">Avg Lexical Entropy: {{ avg_stats.lexical_entropy }}</div>
                <div class="metric">Avg Memory Lines: {{ avg_memory_lines }}</div>
                <div class="collapsible">📊 Archetype Distribution</div>
                <div class="collapsible-content">
                    <canvas id="archetypeChart"></canvas>
                </div>
                <div class="collapsible">📊 Status Distribution</div>
                <div class="collapsible-content">
                    <canvas id="statusChart"></canvas>
                </div>
            </div>

            <!-- Village Metrics -->
            <div class="card">
                <h2>🏘️ Villages ({{ village_count }})</h2>
                <div class="metric">Total Population: {{ total_population }}</div>
                <div class="metric">Avg Population: {{ avg_population }}</div>
                <div class="metric">Avg Stability: {{ avg_stability }}</div>
                <div class="collapsible">📋 Village List</div>
                <div class="collapsible-content">
                    {% for village in villages %}
                        <div class="metric">{{ village.name }} (Pop: {{ village.population }}, Stability: {{ village.stability }})</div>
                    {% endfor %}
                </div>
            </div>

            <!-- World Metrics -->
            <div class="card">
                <h2>🌍 World Map</h2>
                <div class="metric">Regions: {{ world_stats.regions }}</div>
                <div class="metric">Nodes: {{ world_stats.nodes }}</div>
                <div class="metric">Connections: {{ world_stats.connections }}</div>
                <div class="metric">Active Nodes: {{ world_stats.active_nodes }}</div>
                <div class="metric">Energy Flow: {{ world_stats.energy_flow }}</div>
            </div>

            <!-- Training Metrics -->
            <div class="card">
                <h2>🧠 Training Activity</h2>
                <div class="metric">Last Training: {{ last_training or 'Never' }}</div>
                <div class="metric">Trained Entities: {{ entity_count }}</div>
                <a href="/train">Run Training</a>
            </div>
        </div>

        <script>
            // Chart.js Setup
            const archetypeCtx = document.getElementById('archetypeChart').getContext('2d');
            new Chart(archetypeCtx, {
                type: 'bar',
                data: {
                    labels: {{ archetype_labels|tojson }},
                    datasets: [{
                        label: 'Archetypes',
                        data: {{ archetype_values|tojson }},
                        backgroundColor: 'rgba(0, 255, 255, 0.5)',
                        borderColor: 'rgba(0, 255, 255, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        x: { ticks: { color: '#0ff', autoSkip: false, maxRotation: 45, minRotation: 45 } },
                        y: { beginAtZero: true, ticks: { color: '#0ff' } }
                    },
                    plugins: { legend: { labels: { color: '#0ff' } } }
                }
            });

            const statusCtx = document.getElementById('statusChart').getContext('2d');
            new Chart(statusCtx, {
                type: 'pie',
                data: {
                    labels: {{ status_labels|tojson }},
                    datasets: [{
                        data: {{ status_values|tojson }},
                        backgroundColor: ['#0ff', '#f0f', '#ff0', '#f00', '#0f0', '#00f', '#fff'],
                    }]
                },
                options: {
                    plugins: { legend: { labels: { color: '#0ff' } } }
                }
            });

            // Collapsible Sections
            document.querySelectorAll('.collapsible').forEach(item => {
                item.addEventListener('click', () => {
                    item.classList.toggle('active');
                });
            });
        </script>
    </body>
    </html>
    """,
    entity_count=entity_count,
    avg_stats=avg_stats,
    avg_memory_lines=avg_memory_lines,
    archetype_labels=archetype_labels,
    archetype_values=archetype_values,
    status_labels=status_labels,
    status_values=status_values,
    village_count=village_count,
    total_population=total_population,
    avg_population=avg_population,
    avg_stability=avg_stability,
    villages=villages,
    world_stats=world_stats,
    last_training=datetime.now().strftime("%Y-%m-%d %H:%M:%S") if os.path.exists("training_data") else None)

# Error Handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}")
    return render_template_string("""
    <html>
    <head>
        <title>500 Error</title>
        <style>
            :root {
                --neon-green: #0f0;
                --neon-pink: #f0f;
                --neon-cyan: #0ff;
                --bg-dark: #111;
            }
            body { background: var(--bg-dark); color: #fc3; font-family: 'JetBrains Mono', monospace; padding: 2rem; }
            h1 { color: #f00; text-shadow: 0 0 10px #f00; }
            pre { background: #222; padding: 1rem; border: 1px solid #f00; }
        </style>
    </head>
    <body>
        <h1>🔥 Internal Server Error</h1>
        <pre>{{ error }}</pre>
    </body>
    </html>
    """, error=error), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {error}")
    return render_template_string("""
    <html>
    <head>
        <title>404 Not Found</title>
        <style>
            :root {
                --neon-green: #0f0;
                --neon-pink: #f0f;
                --neon-cyan: #0ff;
                --bg-dark: #111;
            }
            body { background: var(--bg-dark); color: #fc3; font-family: 'JetBrains Mono', monospace; padding: 2rem; }
            h1 { color: #f00; text-shadow: 0 0 10px #f00; }
            pre { background: #222; padding: 1rem; border: 1px solid #f00; }
        </style>
    </head>
    <body>
        <h1>🚫 404 - Not Found</h1>
        <pre>{{ error }}</pre>
    </body>
    </html>
    """, error=error), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
