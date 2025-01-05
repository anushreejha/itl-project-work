import os
import time
from dotenv import load_dotenv
from llama_parse import LlamaParse

# Load environment variable
load_dotenv()

# Retrieve the llama API key from the environment variables
api_key = os.getenv('LLAMA_API_KEY')

if api_key is None:
    raise ValueError("API Key is missing. Please check the .env file.")

# Initialize LlamaParse model with the loaded API key
parser = LlamaParse(
    api_key=api_key,  
    result_type="text",  # "text" or "markdown"
    num_workers=4,
    verbose=True,
    language="en",  
)

# Input and output directories
input_dir = "../../itl-project-work/pdf-parser/inputs"
output_dir = "../../itl-project-work/pdf-parser/outputs/llama_parse"
results_file = "../../itl-project-work/pdf-parser/results/llama_results.txt"


os.makedirs(output_dir, exist_ok=True)

pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]

# Open the results file to save time stats
with open(results_file, "w", encoding="utf-8") as result_file:
    result_file.write("PDF File,Processing Time (s)\n")  

    for pdf_file in pdf_files:
        try:
            # Track start time for processing
            start_time = time.time()

            # Extract the text from the PDF using LlamaParse
            documents = parser.load_data(pdf_file)  

            # Check if the result is a list and contains Document objects
            if isinstance(documents, list):
                # Extract text from each document in the list
                documents_text = "\n".join([doc.text for doc in documents if hasattr(doc, 'text')])

            # Track end time for processing
            end_time = time.time()
            processing_time = end_time - start_time

            output_file = os.path.join(output_dir, os.path.basename(pdf_file).replace(".pdf", "_llama.txt"))

            # Save the extracted text to the output directory
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(documents_text)

            # Write the results to the results file (PDF name, and time taken)
            result_file.write(f"{os.path.basename(pdf_file)},{processing_time:.2f}\n")

            # Print process status
            print(f"Processed {os.path.basename(pdf_file)} -> {output_file}")

        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            with open(results_file, "a", encoding="utf-8") as result_file:
                result_file.write(f"{os.path.basename(pdf_file)},Error,{e}\n")
