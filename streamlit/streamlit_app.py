import streamlit as st
import requests,os,json

uploaded_files = st.file_uploader("Choose a PDF file", accept_multiple_files=True)
upload_state = st.text_area("Upload Status", "", key="upload_state")



def upload():
    if uploaded_files is None:
        st.session_state["upload_state"] = "Upload files here,none selected yet!"
    else:
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                r = requests.post("http://documaster:8080/documaster/upload", files={"file": uploaded_file})
                if r.status_code == 200:
                    st.session_state["upload_state"] = f"{os.path.basename(uploaded_file.name)} uploaded sucessfully"
                else:
                    st.session_state["upload_state"]= f"Error uploading {os.path.basename(uploaded_file.name)}"
                    
st.button("Upload file to Documaster", on_click=upload)


q = st.text_input('Enter your query: ')
doc_list = st.text_input('Enter a list of documents to search against,separated by commas. Leave blank to search all documents: ')

def query():
    if isinstance(q, str) and len(q) > 10:
        payload = {"query": q}
        if isinstance(doc_list, str) and len(doc_list) > 0:
            payload["documents"] = [d.strip() for d in doc_list.split(",")]
        st.text_area("Query & selected documents, if any", f"Query : {q},Selected Documents(if any):{payload.get('documents')}", key="query")
        r = requests.post("http://documaster:8080/documaster/query",json.dumps(payload), headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            answer = r.json()["Answer"]
            st.text_area("Answer", answer, key="answer")
        else:
            st.text_area("Answer", f"Error querying Documaster: {r.text}", key="answer")
    else:
        st.text_area("Answer", "Enter a query longer than 10 characters", key="answer")
st.button("Query Documaster", on_click=query)