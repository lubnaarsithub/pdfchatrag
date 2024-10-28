from pymongo import MongoClient
from urllib.parse import quote_plus

def get_mongo_client():
    # Replace with your MongoDB Atlas connection string components
    username = "salonirsithub" 
    password = "Sal@12345"       
    
    # Escape the username and password
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)
    
    # Create your connection string
    connection_string = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.h7nli.mongodb.net/?retryWrites=true&w=majority"
    
    return MongoClient(connection_string)

def get_database():
    client = get_mongo_client()
    return client['pdf_chat_db']  # Use your database name here
