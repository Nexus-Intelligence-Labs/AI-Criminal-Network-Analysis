import re

from models.schemas import CDRRecord


class CDRProcessor:
    PHONE_PATTERN = re.compile(
        r"^\+91[6-9]\d{9}$"
    )

    def normalize_phone(self, phone: str) -> str:
        if not isinstance(phone, str):
            raise TypeError("phone must be a string")

        phone = re.sub(r"[\s-]+", "", phone)

        if phone.startswith("0") and len(phone) == 11:
            phone = "+91" + phone[1:]

        elif len(phone) == 10 and phone[0] in "6789":
            phone = "+91" + phone

        if not self.PHONE_PATTERN.match(phone):
            raise ValueError(f"Invalid Indian phone number: {phone}")

        return phone

    def process(self, data: dict) -> CDRRecord:
        if not isinstance(data, dict):
            raise TypeError("CDR data must be a dictionary")

        caller = self.normalize_phone(data["caller"])
        receiver = self.normalize_phone(data["receiver"])

        return CDRRecord(
            caller=caller,
            receiver=receiver,
            timestamp=data["timestamp"],
            duration=float(data["duration"]),
            source_record=data["source_record"],
        )