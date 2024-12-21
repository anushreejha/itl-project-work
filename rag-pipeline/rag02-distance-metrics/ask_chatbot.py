import os
from dotenv import load_dotenv
import cohere
from vector_database.vector_database import VectorDB
from embedder.embedder import Embedder

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("Cohere API key not found. Please add it to the .env file.")

# Initialize Cohere client
cohere_client = cohere.Client(COHERE_API_KEY)

embedder = Embedder()
vector_db = VectorDB(path='vector_database/data', collection_name="test_rec", similarity_method="cosine")

def generate_answer_online(query, context_chunks):
    # Concatenate the context
    context = '\n'.join(context_chunks)
    input_text = f"Question: {query}\nContext: {context}\nAnswer:"

    # API request to Cohere
    response = cohere_client.generate(
        model='command-xlarge-nightly',
        prompt=input_text,
        max_tokens=150,
        temperature=0.7,
    )

    return response.generations[0].text.strip()

# Main loop to process queries
while True:
    QUERY = input("Ask question to the bot! - ")

    query_embedding = embedder.encode_query(QUERY)
    top_k = vector_db.query_embeddings(query_embedding)

    # Extract the top k chunks from the vector database
    top_chunks_list = [point.payload['text'] for point in top_k]
    top_chunks_string = '\n'.join(top_chunks_list)
    print(f"Top chunks are: {top_chunks_string}")

    answer_to_query = generate_answer_online(QUERY, top_chunks_list)
    print(f"\n\nANSWER TO THE QUERY : {answer_to_query}")
