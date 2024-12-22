from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine, OperatorConfig
from presidio_anonymizer.operators import Operator, OperatorType
from pprint import pprint
from presidio_analyzer.nlp_engine import TransformersNlpEngine
from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerResult,
    RecognizerRegistry,
    PatternRecognizer,
    Pattern,
)
from typing import List, Optional, Tuple, Dict
from presidio_anonymizer.entities import (
    RecognizerResult,
    OperatorResult,
    OperatorConfig,
)
from presidio_anonymizer.operators import Decrypt
from typing import List, Optional, Tuple, Dict
from deanonymizer import InstanceCounterDeanonymizer
from anonymizer import InstanceCounterAnonymizer

import spacy
from spacy_transformers import TransformerModel

class TextAnalyzerService:
    """
    A service class for text analysis, anonymization, and deanonymization.
    """

    def __init__(self, model_choice: str = "obi/deid_roberta_i2b2"):
        """
        Initialize the TextAnalyzerService with a specified transformer model.

        :param model_choice: The transformer model to use for analysis. Defaults to "obi/deid_roberta_i2b2".
        """
        self.model_choice = model_choice
        
        # Load the transformer model using spaCy and spacy-transformers
        try:
            self.nlp_engine = spacy.load("en_core_web_lg")  # Load the spaCy model
            transformer = TransformerModel.from_pretrained(model_choice)  # Load Hugging Face model
            self.nlp_engine.add_pipe(transformer, last=True)
        except Exception as e:
            raise ValueError(f"Error initializing NLP engine: {e}")
        
        self.analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine)
        self.anonymizer = AnonymizerEngine()
        self.anonymizer.add_anonymizer(InstanceCounterAnonymizer)
        self.deanonymizer_engine = DeanonymizeEngine()
        self.deanonymizer_engine.add_deanonymizer(InstanceCounterDeanonymizer)
        self.entity_mapping = dict()

    def analyze_text(self, text: str) -> List[RecognizerResult]:
        """
        Analyze the given text to identify entities.

        :param text: The text to analyze.
        :return: A list of RecognizerResult objects representing the entities found.
        """
        try:
            results = self.analyzer.analyze(text=text, language="en")
            return results
        except Exception as e:
            print(f"An error occurred during text analysis: {e}")
            return []

    def anonymize_text(
        self,
        text: str,
        analyze_results: List[RecognizerResult],
        operator: str,
        mask_char: Optional[str] = None,
        number_of_chars: Optional[str] = None,
        encrypt_key: Optional[str] = None,
    ) -> Tuple[str, dict]:
        """
        Anonymize the given text using the specified operator.

        :param text: The text to anonymize.
        :param analyze_results: The results of text analysis.
        :param operator: The anonymization operator to use.
        :param mask_char: The character to use for masking (if applicable).
        :param number_of_chars: The number of characters to mask (if applicable).
        :param encrypt_key: The encryption key (if applicable).
        :return: A tuple containing the anonymized text and the entity mapping.
        """
        operator_config = None

        if operator == "mask":
            operator_config = {
                "masking_char": mask_char,
                "chars_to_mask": number_of_chars,
                "from_end": False,
            }
        elif operator == "encrypt":
            encrypt_key = "WmZq4t7w!z%C&F)J"
            operator_config = {"key": encrypt_key}
        elif operator == "highlight":
            operator_config = {"lambda": lambda x: x}

        try:
            res = self.anonymizer.anonymize(
                text,
                analyze_results,
                {
                    "DEFAULT": OperatorConfig(params={"entity_mapping": self.entity_mapping})
                },
            )
            return res, self.entity_mapping
        except Exception as e:
            print(f"An error occurred during text anonymization: {e}")
            return "", {}

    def deanonymize_text(self, anonymized_result) -> str:
        """
        Deanonymize the given anonymized text.

        :param anonymized_result: The anonymized text result.
        :return: The deanonymized text.
        """
        try:
            deanonymized = self.deanonymizer_engine.deanonymize(
                anonymized_result.text,
                anonymized_result.items,
                {"DEFAULT": OperatorConfig(params={"entity_mapping": self.entity_mapping})},
            )
            return deanonymized
        except Exception as e:
            print(f"Error during deanonymization: {e}")
            return ""
