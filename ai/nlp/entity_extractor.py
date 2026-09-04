import json
import re
from pathlib import Path
from typing import Any

try:
    import spacy
except ImportError:  # The extractor has a dependency-free fallback.
    spacy = None

try:
    from transformers import pipeline
except ImportError:  # Transformer inference is optional for local development.
    pipeline = None

try:
    from .patterns import ENTITY_PATTERNS
except ImportError:  # Supports running tests from the ai/ directory.
    from nlp.patterns import ENTITY_PATTERNS


class EntityExtractor:

    def __init__(self, use_transformer: bool = False):
        """Create an extractor with local rules and optional NLP backends.

        ``use_transformer`` is disabled by default because downloading model
        weights during API startup makes local development and tests fragile.
        """
        self.nlp = None
        self.transformer_ner = None
        self.rule_patterns = self._load_rule_patterns()

        if spacy is not None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                ruler = self.nlp.add_pipe("entity_ruler", before="ner")
                ruler.add_patterns(self.rule_patterns)
            except (OSError, ValueError):
                # The packaged rule model remains available when spaCy's
                # downloadable language model is not installed.
                self.nlp = None

        if use_transformer and pipeline is not None:
            self.transformer_ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
            )

        # Indian vehicle registration numbers
        self.vehicle_pattern = re.compile(
            r"\b[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}\b"
        )

        # Indian phone numbers
        self.phone_pattern = re.compile(
            r"(?<!\d)(?:\+91[- ]?|0)?[6-9]\d{9}(?!\d)"
        )

    def _add_entity(
        self,
        entities,
        entity_type,
        name,
        source_id,
        confidence,
        start=None,
        end=None
    ):

        name = name.strip()

        if not name:
            return

        entity = {
            "entity_id": f"E{len(entities) + 1:03d}",
            "entity_type": entity_type,
            "name": name,
            "source": source_id,
            "confidence": round(float(confidence), 2)
        }

        if start is not None:
            entity["_start"] = start

        if end is not None:
            entity["_end"] = end

        entities.append(entity)

    def extract_entities(self, text: str, source_id: str):

        entities = []

        # --------------------------------------------------
        # 1. spaCy NER
        # --------------------------------------------------

        doc_entities = self.nlp(text).ents if self.nlp is not None else []

        for ent in doc_entities:

            if ent.label_ == "PERSON":

                self._add_entity(
                    entities,
                    "PERSON",
                    ent.text,
                    source_id,
                    0.90,
                    ent.start_char,
                    ent.end_char
                )

            elif ent.label_ in ["GPE", "LOC"]:

                self._add_entity(
                    entities,
                    "LOCATION",
                    ent.text,
                    source_id,
                    0.90,
                    ent.start_char,
                    ent.end_char
                )

            elif ent.label_ == "ORG":

                self._add_entity(
                    entities,
                    "ORGANIZATION",
                    ent.text,
                    source_id,
                    0.90,
                    ent.start_char,
                    ent.end_char
                )

        # --------------------------------------------------
        # 2. Transformer NER
        # --------------------------------------------------

        transformer_entities = (
            self.transformer_ner(text) if self.transformer_ner is not None else []
        )

        transformer_entities.sort(
            key=lambda x: x.get("start", 0)
        )

        merged_transformer_entities = []

        for ent in transformer_entities:

            label = ent["entity_group"]

            if label == "PER":
                entity_type = "PERSON"

            elif label == "LOC":
                entity_type = "LOCATION"

            elif label == "ORG":
                entity_type = "ORGANIZATION"

            else:
                continue

            start = ent.get("start")
            end = ent.get("end")

            if start is None or end is None:
                continue

            if not merged_transformer_entities:

                merged_transformer_entities.append({
                    "entity_type": entity_type,
                    "start": start,
                    "end": end,
                    "score": ent["score"]
                })

                continue

            previous = merged_transformer_entities[-1]

            gap = text[previous["end"]:start]

            if (
                previous["entity_type"] == entity_type
                and gap.strip() == ""
                and start <= previous["end"] + 1
            ):

                previous["end"] = end

                previous["score"] = max(
                    previous["score"],
                    ent["score"]
                )

            else:

                merged_transformer_entities.append({
                    "entity_type": entity_type,
                    "start": start,
                    "end": end,
                    "score": ent["score"]
                })

        for ent in merged_transformer_entities:

            name = text[ent["start"]:ent["end"]]

            self._add_entity(
                entities,
                ent["entity_type"],
                name,
                source_id,
                ent["score"],
                ent["start"],
                ent["end"]
            )

        # --------------------------------------------------
        # 3. Local model rules (available without downloads)
        # --------------------------------------------------

        for pattern in self.rule_patterns:
            label = pattern["label"]
            entity_type = {
                "PERSON": "PERSON",
                "GPE": "LOCATION",
                "LOC": "LOCATION",
                "ORG": "ORGANIZATION",
            }.get(label)
            if entity_type is None or not isinstance(pattern.get("pattern"), str):
                continue

            matches = re.finditer(re.escape(pattern["pattern"]), text, re.IGNORECASE)
            for match in matches:
                self._add_entity(
                    entities,
                    entity_type,
                    match.group(),
                    source_id,
                    0.95,
                    match.start(),
                    match.end(),
                )

        # --------------------------------------------------
        # 4. Vehicle extraction
        # --------------------------------------------------

        for match in self.vehicle_pattern.finditer(text):

            self._add_entity(
                entities,
                "VEHICLE",
                match.group(),
                source_id,
                0.95,
                match.start(),
                match.end()
            )

        # --------------------------------------------------
        # 5. Phone extraction
        # --------------------------------------------------

        for match in self.phone_pattern.finditer(text):

            self._add_entity(
                entities,
                "PHONE",
                match.group(),
                source_id,
                0.95,
                match.start(),
                match.end()
            )

        # --------------------------------------------------
        # 6. Deduplicate
        # --------------------------------------------------

        entities = self._deduplicate(entities)

        # --------------------------------------------------
        # 7. Re-number entity IDs
        # --------------------------------------------------

        for i, entity in enumerate(entities, start=1):

            entity["entity_id"] = f"E{i:03d}"

            entity.pop("_start", None)
            entity.pop("_end", None)

        return entities

    @staticmethod
    def _load_rule_patterns() -> list[dict[str, Any]]:
        """Load the generated local model when present, otherwise use defaults."""
        model_path = (
            Path(__file__).parent.parent
            / "models"
            / "investigative_ner_rules.json"
        )
        if model_path.exists():
            try:
                payload = json.loads(model_path.read_text(encoding="utf-8"))
                patterns = payload.get("entity_patterns")
                if isinstance(patterns, list):
                    return patterns
            except (OSError, json.JSONDecodeError):
                pass
        return ENTITY_PATTERNS

    def _deduplicate(self, entities):

        # Exact duplicates
        unique = {}

        for entity in entities:

            key = (
                entity["entity_type"],
                entity["name"].lower().strip()
            )

            if key not in unique:

                unique[key] = entity

            elif entity["confidence"] > unique[key]["confidence"]:

                unique[key] = entity

        entities = list(unique.values())

        # Sort by position and prefer longer entities
        entities.sort(
            key=lambda x: (
                x.get("_start", 0),
                -(x.get("_end", 0) - x.get("_start", 0))
            )
        )

        final_entities = []

        for entity in entities:

            start = entity.get("_start")
            end = entity.get("_end")

            should_keep = True

            if start is not None and end is not None:

                for existing in final_entities:

                    existing_start = existing.get("_start")
                    existing_end = existing.get("_end")

                    if existing_start is None or existing_end is None:
                        continue

                    if entity["entity_type"] != existing["entity_type"]:
                        continue

                    overlap = (
                        start < existing_end
                        and end > existing_start
                    )

                    if overlap:

                        current_length = end - start
                        existing_length = (
                            existing_end - existing_start
                        )

                        if existing_length > current_length:

                            should_keep = False
                            break

                        elif existing_length == current_length:

                            if existing["confidence"] >= entity["confidence"]:

                                should_keep = False
                                break

            if should_keep:

                final_entities.append(entity)

        return final_entities
