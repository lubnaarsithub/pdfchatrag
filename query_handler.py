from embedding_manager import get_top_similar_texts  # Ensure this imports correctly
from transformers import pipeline

# Initialize a summarization model for condensing answers
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

def generate_response(user_question):
    # Retrieve the top 3 relevant texts from the database
    top_similarities = get_top_similar_texts(user_question, top_n=5)

    # If no relevant text, return an error message
    if not top_similarities:
        return "Sorry, I couldn't find relevant information in the document.", None, None

    # Sort by similarity to get the most relevant results
    top_similarities.sort(key=lambda x: x[0], reverse=True)

    # Select contexts until a maximum token count or relevance threshold
    max_token_count = 300  # Adjust as needed
    combined_context, token_count = "", 0

    for sim in top_similarities:
        # Add context if under token limit
        token_count += len(sim[1].split())
        if token_count <= max_token_count:
            combined_context += f"{sim[1]}\n\n"
        else:
            break

    # Summarize if the combined context is too lengthy
    if len(combined_context.split()) > 150:  # Adjust threshold as necessary
        summarized = summarizer(combined_context, max_length=100, min_length=50, do_sample=False)
        answer = summarized[0]['summary_text']
    else:
        answer = combined_context.strip()

    # Metadata (unique pages and PDFs)
    unique_pages = sorted(set(sim[2] for sim in top_similarities))
    unique_pdfs = sorted(set(sim[3] for sim in top_similarities))

    # Formatting the final answer
    formatted_answer = f"Answer: {answer}\n\nSource: Page(s) {', '.join(map(str, unique_pages))} in PDF(s): {', '.join(unique_pdfs)}"

    return formatted_answer, unique_pages, unique_pdfs
