# AI / NLP

AI and NLP pipelines for extracting investigative intelligence from
structured and unstructured data.

## Responsibilities

The AI layer is responsible for:

- Named Entity Recognition
- Entity extraction
- Relationship extraction
- Event extraction
- Entity resolution
- Deduplication
- Confidence scoring
- NLP pipeline orchestration

## Planned Technologies

- Python
- spaCy
- Hugging Face Transformers
- Sentence Transformers
- PyTorch
- scikit-learn
- Pandas
- NumPy

## Important Principle

The AI system must not invent evidence.

Extracted information and explanations must remain traceable to the
underlying source records.

## Structure

```text
ai/
├── nlp/                       NLP and NER
├── entity_resolution/        Entity matching and deduplication
├── relationship_extraction/  Relationship extraction
├── pipelines/                Pipeline orchestration
├── models/                   Model-related resources
└── tests/                    AI tests
