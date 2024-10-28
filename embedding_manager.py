from sentence_transformers import SentenceTransformer
import numpy as np
from config import get_database
from numpy.linalg import norm

# Initialize the database and model
db = get_database()
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(text):
    """Generate embeddings for the given text."""
    return model.encode(text, convert_to_tensor=True)  # Convert to tensor for optimized performance

def store_embeddings(text_chunks, pdf_name):
    """Store embeddings and metadata separately in the database."""
    embedding_collection = db['pdf_embeddings']
    metadata_collection = db['pdf_metadata']

    for chunk in text_chunks:
        # Generate embedding for the text
        embedding = generate_embeddings(chunk['text'])
        
        # Store embedding and metadata separately
        embedding_doc = {
            'embedding': embedding.tolist()  # Convert tensor to list for storage
        }
        embedding_id = embedding_collection.insert_one(embedding_doc).inserted_id
        
        metadata_doc = {
            'text': chunk['text'],
            'page_number': chunk['page_number'],
            'pdf_name': pdf_name,
            'embedding_id': embedding_id  # Reference to the embedding document
        }
        metadata_collection.insert_one(metadata_doc)

def get_top_similar_texts(query, top_n=3):
    """Retrieve the top N most similar texts and metadata, ensuring distinct results."""
    embedding_collection = db['pdf_embeddings']
    metadata_collection = db['pdf_metadata']
    
    # Generate embedding for the query
    query_embedding = generate_embeddings(query)
    
    # Fetch all metadata and corresponding embedding IDs
    metadata_docs = list(metadata_collection.find({}, {"text": 1, "embedding_id": 1, "page_number": 1, "pdf_name": 1}))

    similarities = []
    
    # Compute similarity between the query embedding and each stored embedding
    for doc in metadata_docs:
        embedding_id = doc['embedding_id']
        embedding_doc = embedding_collection.find_one({'_id': embedding_id}, {"embedding": 1})
        
        if embedding_doc:
            stored_embedding = np.array(embedding_doc['embedding'])
            # Calculate cosine similarity between the query and stored embeddings
            similarity = np.dot(query_embedding.numpy(), stored_embedding) / (norm(query_embedding.numpy()) * norm(stored_embedding))
            similarities.append((similarity, doc['text'], doc['page_number'], doc['pdf_name']))
    
    # Sort by similarity and return the top N results
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Filter out duplicate text results (based on text content)
    unique_texts = []
    unique_results = []
    
    for sim in similarities:
        if sim[1] not in unique_texts:
            unique_texts.append(sim[1])
            unique_results.append(sim)
        if len(unique_results) == top_n:
            break
    
    # Log top similarities for debugging
    print("Top Similarities:")
    for sim in unique_results:
        print(f"Similarity: {sim[0]}, Text: {sim[1][:30]}... (Page {sim[2]}, PDF: {sim[3]})")
    
    # Return the top N most similar texts, including their metadata
    return unique_results

