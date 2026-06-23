import streamlit as st
import requests,evaluate
st.title("What are we learning today?")
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded" not in st.session_state:
    st.session_state["uploaded"] = False
files = st.file_uploader("Upload your documents", 
                          type=["pdf", "docx"], 
                          accept_multiple_files=True)

if files:
    upload_files = [("files", (f.name, f.getvalue())) for f in files]
    response = requests.post("http://127.0.0.1:8000/upload", files=upload_files)
    st.session_state["uploaded"] = True
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    question = st.chat_input("Ask a question")
    if question:
        payload={"question":question}
        resp= requests.post("http://127.0.0.1:8000/query", json=payload)
        answer=resp.json()["answer"]
        with st.chat_message("user"):
            st.write(question)
        
        with st.chat_message("assistant"):
            st.write(answer)
        st.session_state["messages"].append({"role": "user", "content": question})
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        score = resp.json()["score"]
        with st.expander("Evaluation Score"):
            st.write(score)

 