from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
import pandas as pd

class TextAnalyzerService:
    def __init__(self, model_choice: str):
        # Load model and tokenizer from Hugging Face
        self.model_name = model_choice
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)

    def analyze_text(self, text: str):
        # Tokenize input text
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs).logits
        predicted_token_class = torch.argmax(outputs, dim=2)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        return list(zip(tokens, predicted_token_class[0].tolist()))

    def anonymize_text(self, text: str, entities: list):
        # Example anonymization: Replace PII entities with placeholders
        anonymized_text = text
        for token, label in entities:
            if label == 1:  # Assuming 1 is the label for PII entities
                anonymized_text = anonymized_text.replace(token, "[ANONYMIZED]")
        return anonymized_text

    def deanonymize_text(self, text: str):
        # Example deanonymization: Replace placeholders with the original tokens
        return text.replace("[ANONYMIZED]", "<original>")

# Example usage:
if __name__ == "__main__":
    # Load your CSV file
    df = pd.read_csv("reviews.csv")

    # Initialize text analyzer service with model choice
    text_analyzer_service = TextAnalyzerService(model_choice="obi/deid_roberta_i2b2")

    # Lists to store anonymized and deanonymized text
    anonymized_texts = []
    deanonymized_texts = []

    # Iterate through rows of the DataFrame
    for _, row in df.iterrows():
        text = row.iloc[0]  # Assuming text is in the first column

        # Analyze text to extract entities
        entities = text_analyzer_service.analyze_text(text)

        # Anonymize text
        anonymized_text = text_analyzer_service.anonymize_text(text, entities)

        # Deanonymize text
        deanonymized_text = text_analyzer_service.deanonymize_text(anonymized_text)

        # Store the anonymized and deanonymized texts
        anonymized_texts.append(anonymized_text)
        deanonymized_texts.append(deanonymized_text)

    # Add the new columns to the DataFrame
    df['Anonymized_Text'] = anonymized_texts
    df['Deanonymized_Text'] = deanonymized_texts

    # Save the modified DataFrame to a new CSV file
    df.to_csv("output_anonymized.csv", index=False)
