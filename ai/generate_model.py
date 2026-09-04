"""Generate the versioned, offline NER model artifact used by EntityExtractor."""

import json
from pathlib import Path

from nlp.patterns import ENTITY_PATTERNS


def generate_model() -> Path:
    """Write the deterministic local entity model and return its path."""
    output_path = Path(__file__).parent / "models" / "investigative_ner_rules.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name": "investigative-ner-rules",
        "version": 1,
        "description": "Offline entity-recognition rules for investigative demo data.",
        "entity_patterns": ENTITY_PATTERNS,
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


if __name__ == "__main__":
    print(generate_model())
