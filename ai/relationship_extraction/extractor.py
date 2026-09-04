import json
import os
from typing import Optional

from google import genai
from pydantic import BaseModel, Field

from models.schemas import Relationship


class GeminiRelationshipItem(BaseModel):
    """
    Structured response model for one extracted relationship.
    """

    source: str = Field(
        description="Exact source entity name from the text."
    )

    relationship: str = Field(
        description="Supported relationship type."
    )

    target: str = Field(
        description="Exact target entity name from the text."
    )

    timestamp: Optional[str] = Field(
        default=None,
        description=(
            "Explicit timestamp from the source text, "
            "or null when unavailable."
        ),
    )

    source_record: Optional[str] = Field(
        default=None,
        description=(
            "Source record identifier."
        ),
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score between 0.0 and 1.0."
        ),
    )


class GeminiRelationshipResponse(BaseModel):
    """
    Structured Gemini response containing relationships.
    """

    relationships: list[
        GeminiRelationshipItem
    ] = Field(
        default_factory=list,
        description=(
            "Relationships explicitly supported by "
            "the source text."
        ),
    )


class GeminiRelationshipClient:
    """
    Gemini API client for relationship extraction.

    The API key is read from GEMINI_API_KEY.
    The model can be changed with GEMINI_MODEL.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key=None,
        model=None,
        client=None,
    ):
        self.api_key = (
            api_key
            or os.getenv(
                "GEMINI_API_KEY"
            )
        )

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                self.DEFAULT_MODEL,
            )
        )

        self.client = client

    def connect(self):
        """Create the Gemini client lazily."""

        if self.client is not None:
            return

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def generate_relationships(
        self,
        prompt: str,
    ):
        """
        Generate structured relationship output
        using Gemini and a Pydantic response schema.
        """

        if not isinstance(
            prompt,
            str,
        ):
            raise TypeError(
                "prompt must be a string"
            )

        if not prompt.strip():
            raise ValueError(
                "prompt cannot be empty"
            )

        self.connect()

        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": (
                        "application/json"
                    ),
                    "response_schema": (
                        GeminiRelationshipResponse
                    ),
                },
            )
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        try:
            parsed = json.loads(
                response.text
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini returned invalid JSON."
            ) from exc

        return parsed


class RelationshipExtractor:
    """
    Extract investigative relationships using Gemini.

    Every returned relationship is validated through the
    project's Pydantic Relationship model.
    """

    ALLOWED_RELATIONSHIPS = {
        "KNOWS",
        "CALLED",
        "TRANSFERRED_TO",
        "ASSOCIATED_WITH",
        "TRAVELLED_WITH",
        "LOCATED_AT",
        "OWNS",
        "USED",
        "INVOLVED_IN",
    }

    def __init__(
        self,
        client=None,
    ):
        self.client = (
            client
            or GeminiRelationshipClient()
        )

    def build_prompt(
        self,
        source_text: str,
        source_record: str,
    ) -> str:
        """Build a strict evidence-grounded prompt."""

        if not isinstance(
            source_text,
            str,
        ):
            raise TypeError(
                "source_text must be a string"
            )

        if not source_text.strip():
            raise ValueError(
                "source_text cannot be empty"
            )

        if not isinstance(
            source_record,
            str,
        ):
            raise TypeError(
                "source_record must be a string"
            )

        if not source_record.strip():
            raise ValueError(
                "source_record cannot be empty"
            )

        return f"""
You are an investigative information extraction system.

Your task is to extract ONLY relationships that are
explicitly supported by the supplied source text.

CRITICAL RULES:

1. Never invent evidence.
2. Never assume a relationship that is not stated.
3. Do not infer guilt, criminal intent, or causality.
4. Extract only relationships between entities explicitly
   present in the source text.
5. Use the exact entity names appearing in the source text.
6. Use null for timestamp when no timestamp is explicitly
   available.
7. Use the supplied source record ID when available.
8. Confidence must be between 0.0 and 1.0.
9. Return an empty relationships list when no supported
   relationship exists.

Allowed relationship types:

- KNOWS
- CALLED
- TRANSFERRED_TO
- ASSOCIATED_WITH
- TRAVELLED_WITH
- LOCATED_AT
- OWNS
- USED
- INVOLVED_IN

SOURCE RECORD:
{source_record}

SOURCE TEXT:
{source_text}
"""

    def _validate_relationship(
        self,
        relationship,
        source_record,
    ):
        """Validate and normalize one relationship."""

        if isinstance(
            relationship,
            GeminiRelationshipItem,
        ):
            relationship = (
                relationship.model_dump()
            )

        if not isinstance(
            relationship,
            dict,
        ):
            raise ValueError(
                "Each relationship must be a dictionary."
            )

        relationship_type = str(
            relationship.get(
                "relationship",
                "",
            )
        ).strip().upper()

        if (
            relationship_type
            not in self.ALLOWED_RELATIONSHIPS
        ):
            raise ValueError(
                "Unsupported relationship type: "
                f"{relationship_type}"
            )

        source = str(
            relationship.get(
                "source",
                "",
            )
        ).strip()

        target = str(
            relationship.get(
                "target",
                "",
            )
        ).strip()

        if not source:
            raise ValueError(
                "Relationship source cannot be empty."
            )

        if not target:
            raise ValueError(
                "Relationship target cannot be empty."
            )

        timestamp = relationship.get(
            "timestamp"
        )

        if timestamp is not None:
            timestamp = str(
                timestamp
            ).strip()

            if not timestamp:
                timestamp = None

        returned_source_record = (
            relationship.get(
                "source_record"
            )
        )

        if not returned_source_record:
            returned_source_record = (
                source_record
            )

        confidence = float(
            relationship.get(
                "confidence",
                1.0,
            )
        )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Relationship confidence must be "
                "between 0.0 and 1.0."
            )

        return Relationship(
            source=source,
            relationship=relationship_type,
            target=target,
            timestamp=timestamp,
            source_record=(
                returned_source_record
            ),
            confidence=confidence,
        )

    def parse_relationships(
        self,
        response_data,
        source_record,
    ):
        """
        Parse Gemini structured output and validate it
        through the project's Relationship model.
        """

        if isinstance(
            response_data,
            GeminiRelationshipResponse,
        ):
            response_data = (
                response_data.model_dump()
            )

        elif isinstance(
            response_data,
            str,
        ):
            try:
                response_data = json.loads(
                    response_data
                )

            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Invalid JSON response."
                ) from exc

        if not isinstance(
            response_data,
            dict,
        ):
            raise TypeError(
                "response_data must be a dictionary."
            )

        relationships = response_data.get(
            "relationships",
            [],
        )

        if not isinstance(
            relationships,
            list,
        ):
            raise ValueError(
                "'relationships' must be a list."
            )

        validated = []

        for item in relationships:

            relationship = (
                self._validate_relationship(
                    item,
                    source_record,
                )
            )

            validated.append(
                relationship
            )

        return validated

    def extract(
        self,
        source_text: str,
        source_record: str,
    ):
        """
        Perform Gemini-powered relationship extraction.
        """

        prompt = self.build_prompt(
            source_text,
            source_record,
        )

        response = (
            self.client.generate_relationships(
                prompt
            )
        )

        return self.parse_relationships(
            response,
            source_record,
        )