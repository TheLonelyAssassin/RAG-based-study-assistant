import faiss
import chunking
import numpy as np
import os,pickle

def retrieve(query, chunks, embeddings, top_k=3):
	embeddings_np = np.array(embeddings).astype('float32')
	query_embedding=chunking.embed_chunks(query)
	query_vector = np.array([query_embedding]).astype('float32')
	ind=faiss.IndexFlatL2(384)
	ind.add(embeddings_np)
	faiss.write_index(ind,"index.faiss")
	top_k = min(3, len(chunks))
	distances, indices=ind.search(query_vector,top_k)
	return [chunks[i] for i in indices[0]]