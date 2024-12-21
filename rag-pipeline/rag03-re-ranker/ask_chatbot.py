import requests
from vector_database.vector_database import VectorDB
from embedder.embedder import Embedder
from dotenv import load_dotenv

load_dotenv()

# Initialization
embedder = Embedder()
vector_db = VectorDB(similarity_method="dot", path='vector_database/data', collection_name="test_reranker")

def generate_answer_online(query, context_chunks):
    '''Function to query Open Assistant'''
    # Concatenate the context
    context = '\n'.join(context_chunks)
    input_text = f"Question: {query}\nContext: {context}\nAnswer:"

    # API request to Open Assistant
    response = requests.post(
        "https://api.open-assistant.io/v1/chat/completion",
        json={
            "model": "oasst-sft-6-llama-30b",
            "messages": [{"role": "user", "content": input_text}],
            "temperature": 0.7,
            "max_tokens": 150
        }
    )
    if response.status_code == 200:
        answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response available.")
        return answer.strip()
    else:
        return f"Error: Unable to fetch response (status code {response.status_code})"

def simple_rerank(query, chunks):
    '''Simple re-ranker (if external model unavailable)'''
    # Encode query and chunks, then rank by cosine similarity
    query_embedding = embedder.encode_query(query)
    chunk_embeddings = [embedder.encode_query(chunk) for chunk in chunks]
    
    # Calculate cosine similarity
    similarities = [
        (chunk, sum(q * c for q, c in zip(query_embedding, chunk_embedding)))
        for chunk, chunk_embedding in zip(chunks, chunk_embeddings)
    ]
    # Sort by similarity score (descending)
    return [chunk for chunk, _ in sorted(similarities, key=lambda x: x[1], reverse=True)]

while True:
    QUERY = input("Ask question to the bot! - ")

    # Encode the query and search for relevant chunks
    query_embedding = embedder.encode_query(QUERY)
    top_k = vector_db.query_embeddings(query_embedding, limit=10)

    # Extract the top k chunks from the vector database
    top_chunks_list = [point.payload['text'] for point in top_k]
    top_chunks_string = '\n'.join(top_chunks_list)

    # Re-rank the chunks
    top_n = 3
    re_ranked_list = simple_rerank(QUERY, top_chunks_list[:top_n])

    # Save chunks before and after re-ranking to a file
    file_name = "outputs.txt"
    with open(file_name, "w") as file:
        file.write("THE CHUNKS BEFORE RE-RANKING\n\n")
        for chunk in top_chunks_list:
            file.write(chunk + "\n\n")
        file.write("THIS IS AFTER RE-RANKING\n\n")
        for re_ranked_chunk in re_ranked_list:
            file.write(re_ranked_chunk + "\n\n")

    print("LLM Response : ")
    answer_to_query = generate_answer_online(QUERY, re_ranked_list)
    print(f"\n\nANSWER TO THE QUERY : {answer_to_query}")
