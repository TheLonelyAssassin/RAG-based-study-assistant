import retriever
import chunking
import generator
import fitz 
from docx import Document
def emd_chunk(document ,max_sent=200,overlap=50): 
    chunk =chunking.load_and_chunk(max_sent, document,overlap)
    embeding = chunking.embed_chunks(chunk)
    return chunk,embeding
def retri_generate(question,chunk,embeding):
    info=retriever.retrieve(question, chunk, embeding, top_k=3)
    context = " ".join(info)
    answer= generator.generate(question,context)
    return answer,context
def read_docx(path):
    doc = Document(path)
    return " ".join([para.text for para in doc.paragraphs if para.text.strip()])
def read_pdf(path):
    doc = fitz.open(path)
    return "".join([page.get_text() for page in doc])
'''start = time.time()
document= read_pdf("D:\\NLP\\NLP\\_Jurafsky_ed3book_jan72023.pdf")
question="How is vectorization useful in NLP?"
print(f"PDF reading: {time.time()-start:.2f}s")
start = time.time()
answer, chunk, embeding = rag_pipeline(document, question, 10, 2)
print(f"Pipeline: {time.time()-start:.2f}s")
#print(answer)
start = time.time()
retrieved = retirver.retrieve(question, chunk, embeding, top_k=3)
context = " ".join(retrieved)
answer = generator.generate(question, retrieved)

score = evaluate.evaluater(question, context, answer)
print(f"evaluation: {time.time()-start:.2f}s")
print(score)'''