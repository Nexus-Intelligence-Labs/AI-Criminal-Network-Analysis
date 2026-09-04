from pydantic import ValidationError

from models.schemas import Relationship


class RelationshipValidator:
    def validate(self, data: dict) -> Relationship:
        if not isinstance(data, dict):
            raise TypeError("relationship data must be a dictionary")

        try:
            return Relationship.model_validate(data)
        except ValidationError as exc:
            raise ValueError(
                f"Invalid relationship data: {exc}"
            ) from exc

    def validate_many(self, data: list[dict]) -> list[Relationship]:
        if not isinstance(data, list):
            raise TypeError("relationship data must be a list")

        return [self.validate(item) for item in data]