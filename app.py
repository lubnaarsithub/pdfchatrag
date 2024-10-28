from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from pdf_parser import extract_text_from_pdf
from embedding_manager import store_embeddings
from query_handler import generate_response
from conversation_manager import store_conversation

app = FastAPI()

UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Query(BaseModel):
    question: str

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Check the file extension instead of content_type
    print(f"File Headers: {file.headers}")
    if not file.filename.endswith('.pdf'):
        print(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    
    try:
        # Save the uploaded PDF to the uploads folder
        with open(file_location, "wb") as f:
            f.write(await file.read())
        print(f"File saved at: {file_location}")  # Debugging: Print where the file is saved
        
        # Extract text from the uploaded PDF
        extracted_text_chunks = extract_text_from_pdf(file_location)
        print(f"Extracted text chunks: {len(extracted_text_chunks)}")  # Debugging: Print the number of text chunks extracted
        
        # Store embeddings for the extracted text
        store_embeddings(extracted_text_chunks, file.filename)
        print(f"Embeddings stored for file: {file.filename}")  # Debugging: Confirm embeddings were stored
        
        return {"message": "PDF uploaded and processed successfully."}
    except Exception as e:
        print(f"Error during PDF processing: {str(e)}")  # Debugging: Print any exception that occurs
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.post("/chat")
async def chat(query: Query):
    user_question = query.question
    print(f"Received question: {user_question}")  # Debugging: Print the user question
    try:
        # Generate the response for the user's question
        answer, page_number, pdf_name = generate_response(user_question)
        print(f"Generated response: {answer}, Page: {page_number}, PDF: {pdf_name}")  # Debugging: Print the response details
        
        # Store the conversation for future reference
        store_conversation(user_question, answer)
        print(f"Conversation stored. Question: {user_question}, Answer: {answer}")  # Debugging: Confirm the conversation was stored
        
        return {
            "answer": answer,
            "page_number": page_number,
            "pdf_name": pdf_name
        }
    except Exception as e:
        print(f"Error generating response: {str(e)}")  # Debugging: Print any exception that occurs during response generation
        return {"error": f"Failed to generate response: {str(e)}"}
