import streamlit as st
import requests

# API endpoints
UPLOAD_URL = "http://127.0.0.1:8000/upload-pdf/"
CHAT_URL = "http://127.0.0.1:8000/chat/"

# Custom Style
st.set_page_config(page_title="PDF Chat App", page_icon=":books:", layout="wide")

# Initialize session state to track PDF upload
if 'pdf_uploaded' not in st.session_state:
    st.session_state.pdf_uploaded = False
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# Sidebar for PDF Upload
st.sidebar.title("Upload Your PDF")
st.sidebar.write("Upload your PDF to interact with the document using natural language.")

# PDF Upload Section in the Sidebar
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

# Handling PDF Upload
if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_file_name:
    with st.spinner("Uploading and processing the PDF..."):
        files = {"file": uploaded_file}
        print(f"Uploading file: {uploaded_file.name}")  # Debugging: Print uploaded file info
        response = requests.post(UPLOAD_URL, files=files)
        print(f"Upload Response Status: {response.status_code}")  # Debugging: Check upload response status
        print(f"Upload Response: {response.text}")  # Debugging: Print the full upload response text

    if response.status_code == 200:
        st.session_state.pdf_uploaded = True  # Set the flag that the PDF has been uploaded
        st.session_state.uploaded_file_name = uploaded_file.name  # Store the file name to prevent re-upload
        st.sidebar.success("PDF uploaded and processed successfully!")
        st.sidebar.balloons()  # A fun element for success
    else:
        error_detail = response.json().get('detail', 'Please try again.')
        print(f"Upload Failed. Error: {error_detail}")  # Debugging: Print error message
        st.sidebar.error(f"Failed to upload PDF. {error_detail}")

# Main Page for Chat Interface
st.title("Chat with Your PDF Document")
st.write("Ask questions related to the uploaded document and get answers instantly.")

# Input field for the user's question
user_question = st.text_input("Enter your question:")

# "Send" button centered on the main page
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    send_button = st.button("Send", key="send_button")

# Fetch and display chat response if "Send" is clicked
if send_button and st.session_state.pdf_uploaded:  # Ensure that the chat is processed only if the PDF has been uploaded
    if user_question:
        with st.spinner("Fetching the response..."):
            print(f"User Question: {user_question}")  # Debugging: Print user's question
            chat_response = requests.post(CHAT_URL, json={"question": user_question})
            print(f"Chat Response Status: {chat_response.status_code}")  # Debugging: Check response status
            print(f"Chat Response: {chat_response.text}")  # Debugging: Print full chat response text
            
        if chat_response.status_code == 200:
            answer = chat_response.json().get("answer")
            print(f"Answer: {answer}")  # Debugging: Print the answer received from the server
            st.success(f"**Answer:** {answer}")
        else:
            error_message = chat_response.json().get('message', 'Please try again.')
            print(f"Chat Failed. Error: {error_message}")  # Debugging: Print error message
            st.error(f"Failed to get a response. {error_message}")
    else:
        print("No question entered.")  # Debugging: Notify when no question is entered
        st.warning("Please enter a question.")
elif not st.session_state.pdf_uploaded:
    st.warning("Please upload a PDF first.")
