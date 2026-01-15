import faiss
import numpy as np
import json
import os


class ChunkMemoryIndex:
    def __init__(self, dim=768):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.chunk_ids = []  # Maps FAISS index ID (0,1,2) to your UUIDs

    def add(self, chunk_id, embedding):
        vec = np.array([embedding]).astype("float32")
        faiss.normalize_L2(vec)
        self.index.add(vec)
        self.chunk_ids.append(chunk_id)

    def search(self, query_embedding, k=3):
        vec = np.array([query_embedding]).astype("float32")
        faiss.normalize_L2(vec)

        # Check if index is empty
        if self.index.ntotal == 0:
            return []

        scores, ids = self.index.search(vec, k)
        results = []
        for idx, i in enumerate(ids[0]):
            if i != -1 and i < len(self.chunk_ids):
                results.append((self.chunk_ids[i], float(scores[0][idx])))
        return results

    # --- NEW SAVING & LOADING METHODS ---
    def save_local(self, folder_path, filename_prefix):
        """Saves both the FAISS index and the ID mapping"""

        # 1. Save FAISS Binary
        index_path = os.path.join(folder_path, f"{filename_prefix}.faiss")
        faiss.write_index(self.index, index_path)

        # 2. Save ID Mapping
        ids_path = os.path.join(folder_path, f"{filename_prefix}_ids.json")
        with open(ids_path, "w", encoding="utf-8") as f:
            json.dump(self.chunk_ids, f)

        print(f"Index saved to: {index_path}")
        print(f"IDs saved to: {ids_path}")
        return index_path, ids_path

    def load_local(self, index_path, ids_path):
        """Loads index and IDs from disk"""
        if not os.path.exists(index_path) or not os.path.exists(ids_path):
            raise FileNotFoundError("Index or ID file not found.")

        # 1. Load FAISS Binary
        self.index = faiss.read_index(index_path)

        # 2. Load ID Mapping
        with open(ids_path, "r", encoding="utf-8") as f:
            self.chunk_ids = json.load(f)

        print(f"Loaded Index with {self.index.ntotal} vectors.")