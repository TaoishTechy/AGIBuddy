class CrystalMemory:
    def __init__(self):
        self.fragments = {}

    def add_fragment(self, text, tag=None):
        key = f"frag_{len(self.fragments)}"
        self.fragments[key] = {
            "text": text,
            "tag": tag or "unlabeled"
        }

    def get_all_texts(self):
        return [frag["text"] for frag in self.fragments.values()]
