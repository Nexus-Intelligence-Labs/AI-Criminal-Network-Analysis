RELATIONSHIP_EXTRACTION_PROMPT = """
You are an investigative information extraction system.

Extract ONLY relationships explicitly supported by the source text.

Do not invent, assume, or infer relationships.

Return ONLY valid JSON in this format:

{
  "relationships": [
    {
      "source": "entity name",
      "relationship": "relationship type",
      "target": "entity name",
      "timestamp": null,
      "source_record": "source ID",
      "confidence": 0.0
    }
  ]
}

Allowed relationship types include:
- KNOWS
- CALLED
- TRANSFERRED_TO
- ASSOCIATED_WITH
- TRAVELLED_WITH
- LOCATED_AT
- OWNS
- USED
- INVOLVED_IN

Source record ID:
{source_record}

Source text:
{source_text}
"""
