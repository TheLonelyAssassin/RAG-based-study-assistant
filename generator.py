import requests
def  generate(query, retrieved_chunks):
	context= "".join(retrieved_chunks)
	payload ={
    "model": "mistral",
    "prompt": f"You are a technical expert answering customer questions in the given task, the answer is only based on the context strictly, so the context is provided. Context is: {context}. The question from the user is:{query}. Now, answer the question based solely on the context, as clearly as possible, without hallucination, and include any code if the context provides it. If the answer cannot be found in the context, say 'I don't have enough information to answer this." ,
    "stream": False
}	
	response = requests.post("http://localhost:11434/api/generate", json=payload)
	return response.json()["response"]
