import requests
from vector_database.vector_database import VectorDB 
from embedder.embedder import Embedder

embedder = Embedder()
vector_db = VectorDB(path='vector_database/data', collection_name="test_rec")

def generate_answer_online(query, context_chunks):
    '''Function to query Open Assistant API'''
    # Concatenate the context
    context = '\n'.join(context_chunks)
    input_text = f"Question: {query}\nContext: {context}\nAnswer:"

    # API request to Open Assistant
    response = requests.post(
        "https://api.open-assistant.io/v1/chat/completion",
        json={
            "model": "oa_v1",
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
