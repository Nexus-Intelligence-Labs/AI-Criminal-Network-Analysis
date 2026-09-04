from nlp.preprocessor import TextPreprocessor
from nlp.entity_extractor import EntityExtractor


class NLPPipeline:

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.entity_extractor = EntityExtractor()

    def process(self, text: str, source_id: str):

        cleaned_text = self.preprocessor.clean_text(text)

        if not cleaned_text:
            return {
                "source": source_id,
                "text": "",
                "entities": []
            }

        entities = self.entity_extractor.extract_entities(
            cleaned_text,
            source_id
        )

        return {
            "source": source_id,
            "text": cleaned_text,
            "entities": entities
        }