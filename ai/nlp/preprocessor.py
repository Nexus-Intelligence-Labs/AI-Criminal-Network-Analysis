import re
import unicodedata


class TextPreprocessor:

    def __init__(self):
        pass

    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters while preserving
        meaningful investigative text.
        """

        return unicodedata.normalize("NFKC", text)

    def normalize_whitespace(self, text: str) -> str:
        """
        Replace repeated spaces, tabs and newlines
        with a single space.
        """

        return re.sub(r"\s+", " ", text).strip()

    def normalize_phone_spacing(self, text: str) -> str:
        """
        Normalize common spacing around Indian phone
        country code prefixes.

        Examples:
            +91 9876543210
            +91-9876543210

        become:
            +919876543210
        """

        text = re.sub(
            r"\+91[\s-]+(?=[6-9]\d{9})",
            "+91",
            text
        )

        return text

    def clean_text(self, text: str) -> str:
        """
        Run all preprocessing operations in sequence.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            return ""

        text = self.normalize_unicode(text)
        text = self.normalize_phone_spacing(text)
        text = self.normalize_whitespace(text)

        return text