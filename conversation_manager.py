from config import get_database
from pymongo.errors import PyMongoError

db = get_database()

def store_conversation(question, response):
    """
    Store a conversation in the database.

    Parameters:
    - question (str): The question asked by the user.
    - response (str): The response generated by the system.

    Returns:
    None
    """
    # Validate inputs
    if not question or not response:
        print("Question and response must not be empty.")
        return

    try:
        conversation_collection = db['conversations']
        conversation = {
            'question': question,
            'response': response
        }
        conversation_collection.insert_one(conversation)
        print("Conversation stored successfully.")  # Log success
    except PyMongoError as e:
        print(f"Failed to store conversation: {str(e)}")  # Log detailed error
