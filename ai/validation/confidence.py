class ConfidenceLevel:
    HIGH = "HIGH"
    REVIEW = "REVIEW"
    LOW = "LOW"


class ConfidenceScorer:
    def __init__(self, high_threshold=0.90, review_threshold=0.70):
        if not 0.0 <= review_threshold <= 1.0:
            raise ValueError("review_threshold must be between 0 and 1")

        if not 0.0 <= high_threshold <= 1.0:
            raise ValueError("high_threshold must be between 0 and 1")

        if review_threshold > high_threshold:
            raise ValueError(
                "review_threshold cannot be greater than high_threshold"
            )

        self.high_threshold = high_threshold
        self.review_threshold = review_threshold

    def classify(self, confidence: float) -> str:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        if confidence >= self.high_threshold:
            return ConfidenceLevel.HIGH

        if confidence >= self.review_threshold:
            return ConfidenceLevel.REVIEW

        return ConfidenceLevel.LOW