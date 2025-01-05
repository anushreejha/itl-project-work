import os
import time
from pdfminer.high_level import extract_text

# Input and output directories (
input_dir = "../../itl-project-work/pdf-parser/inputs"
output_dir = "../../itl-project-work/pdf-parser/outputs/pdfminer"
results_file = "../../itl-project-work/pdf-parser/results/pdfminer_results.txt"

os.makedirs(output_dir, exist_ok=True)

pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".pdf")]

# Open the results file to save time stats
with open(results_file, "w", encoding="utf-8") as result_file:
    result_file.write("PDF File,Processing Time (s)\n")  # Header for CSV-like output

    for pdf_file in pdf_files:
        try:
            # Track start time for processing
            start_time = time.time()

            # Extract the text from the PDF
            text = extract_text(pdf_file)

            # Track end time for processing
            end_time = time.time()
            processing_time = end_time - start_time

            output_file = os.path.join(output_dir, os.path.basename(pdf_file).replace(".pdf", "_pdfminer.txt"))

            # Save the extracted text to the output directory
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)

            # Write the results to the results file (PDF name, and time taken)
            result_file.write(f"{os.path.basename(pdf_file)},{processing_time:.2f}\n")

            # Print process status
            print(f"Processed {os.path.basename(pdf_file)} -> {output_file}")

        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            with open(results_file, "a", encoding="utf-8") as result_file:
                result_file.write(f"{os.path.basename(pdf_file)},Error,{e}\n")
