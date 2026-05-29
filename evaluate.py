import requests
def  evaluater(question, context, answer):
	payload1 ={
    "model": "mistral",
    "prompt": f"Given this context:{context}, the question:{question} ,and the answer: {answer}, is every claim in the answer supported by the context? Reply with a score from 0-10 and explain why." ,
    "stream": False
}	
	response = requests.post("http://localhost:11434/api/generate", json=payload1)
	return response.json()["response"]