from transformers import GPT2LMHeadModel, GPT2Tokenizer
from embedder.embedder import Embedder
from vector_database.vector_database import VectorDB

# Load the GPT-2 model and tokenizer from Hugging Face
model_name = "gpt2" 
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Initialize the embedder and vector database
embedder = Embedder()
vector_db = VectorDB(path='vector_database/data', collection_name="test3")

def generate_answer(query, context):
    # Combine the query and the context (top chunks) to generate a prompt
    prompt = f"Question: {query}\n\nContext: {context}\n\nAnswer:"

    # Tokenize the input prompt and generate an answer
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=1024, num_return_sequences=1, no_repeat_ngram_size=2, pad_token_id=tokenizer.eos_token_id)
    
    # Decode the output and return the generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text[len(prompt):].strip()  # Return the answer part of the generated text

while True:
    QUERY = input("Ask question to the bot! -  ")
    query_embedding = embedder.encode_query(QUERY)

    top_k = vector_db.query_embeddings(query_embedding)
    top_chunks_list = [point.payload['text'] for point in top_k]
    top_chunks_string = '\n'.join(top_chunks_list)
    
    print(f"Top chunks are: {top_chunks_string}")

    answer_to_query = generate_answer(QUERY, top_chunks_string)
    
    print(f"\n\nANSWER TO THE QUERY: {answer_to_query}")
