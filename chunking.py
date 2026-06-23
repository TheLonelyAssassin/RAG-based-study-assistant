from sentence_transformers import SentenceTransformer
import torch
import nltk
device1 = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SentenceTransformer("all-MiniLM-L6-v2",device=device1)
def load_and_chunk(max_sent, document, overlap):
    sentences = nltk.sent_tokenize(document)
    chunk = []
    c=0
    end = 0
    previous_start = 0
    while previous_start < len(sentences):
        end = previous_start + max_sent
        cont = " ".join(sentences[previous_start:end])
        chunk.append(cont)
        previous_start = previous_start + (max_sent - overlap)
    return chunk

def embed_chunks(chunks):
	return model.encode(chunks)
