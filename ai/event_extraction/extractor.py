from models.schemas import Event


class EventExtractor:
    """Extract structured events from investigative text."""

    EVENT_KEYWORDS = {
        "CALL": ["called", "call", "phone call", "telephoned"],
        "TRANSFER": ["transferred", "transfer", "sent", "paid"],
        "TRAVEL": ["travelled", "traveled", "went", "visited"],
        "MEETING": ["met", "meeting", "met with"],
        "LOCATION": ["located", "found", "stayed", "resided"],
    }

    def __init__(self):
        pass

    def extract(
        self,
        text: str,
        source_record: str,
        entities=None,
    ) -> list[Event]:
        """Extract events supported directly by the supplied text."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not isinstance(source_record, str):
            raise TypeError("source_record must be a string")

        if not text.strip():
            return []

        entities = entities or []

        events = []
        lowered_text = text.lower()

        for event_type, keywords in self.EVENT_KEYWORDS.items():
            matched_keyword = None

            for keyword in keywords:
                if keyword in lowered_text:
                    matched_keyword = keyword
                    break

            if matched_keyword is None:
                continue

            participants = self._find_participants(
                text,
                entities,
            )

            event = Event(
                event_type=event_type,
                participants=participants,
                source_record=source_record,
                confidence=0.90,
            )

            events.append(event)

        return events

    def _find_participants(self, text: str, entities: list) -> list[str]:
        """Return PERSON entities that occur in the supplied text."""

        participants = []

        for entity in entities:
            entity_type = entity.get("entity_type")

            if hasattr(entity_type, "value"):
                entity_type = entity_type.value

            if entity_type != "PERSON":
                continue

            name = entity.get("name")

            if name and name in text and name not in participants:
                participants.append(name)

        return participants