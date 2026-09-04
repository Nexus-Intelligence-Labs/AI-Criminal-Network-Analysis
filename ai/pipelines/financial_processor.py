from models.schemas import FinancialTransaction


class FinancialProcessor:
    def process(self, data: dict) -> FinancialTransaction:
        if not isinstance(data, dict):
            raise TypeError("financial data must be a dictionary")

        amount = float(data["amount"])

        if amount < 0:
            raise ValueError("transaction amount cannot be negative")

        return FinancialTransaction(
            sender=str(data["sender"]).strip(),
            receiver=str(data["receiver"]).strip(),
            amount=amount,
            timestamp=data["timestamp"],
            source_record=data["source_record"],
        )