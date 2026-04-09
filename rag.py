"""
I used Claude to generate the base structure of this file so that I could embed the runbooks.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Runbook Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
print(type(model))

runbook_folder = os.fsencode("runbooks/")

docs = []
for file in os.listdir(runbook_folder):
    rb = os.fsdecode(file)
    if rb.endswith(".md"):
        with open(os.path.join("runbooks/", rb), "r") as f:
            docs.append(f.read())

embeddings = model.encode(docs, normalize_embeddings=True)

np.savez_compressed(
    "compressed_runbooks.npz",
    embeddings=embeddings,
    documents=np.array(docs)
)

# Example for query matching
data = np.load("compressed_runbooks.npz", allow_pickle=True)
embeddings = data["embeddings"]
docs = data["documents"].tolist()

query = "I'm facing an issue with latency for my API server that is very long, while also getting intermittent server errors."

query = "Represent this sentence for searching relevant passages: " + query

query_embedding = model.encode(
    [query],
    normalize_embeddings=True
)[0]

def cosine_similarity(a, b):
    return np.dot(a, b)

scores = np.dot(embeddings, query_embedding)

top_k = 1
top_indices = np.argsort(scores)[::-1][:top_k]

print("\nQuery:", query)
print("\nTop matches:\n")

for i in top_indices:
    print(f"Score: {scores[i]:.4f}")
    print(f"Text: {docs[i]}")
    print("-" * 50)