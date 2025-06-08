class DreamModule:
    def __init__(self, seed=0):
        self.tick_count = 0
        self.seed = seed

    def tick(self):
        self.tick_count += 1

    def evolve(self, entity):
        # Example evolution logic
        entity.stats["lexical_entropy"] += 0.01
        entity.memory.append(f"Dream tick {self.tick_count} for {entity.name}")
