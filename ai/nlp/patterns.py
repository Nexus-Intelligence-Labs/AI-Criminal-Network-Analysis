# Domain-specific EntityRuler patterns
# These patterns improve recall for investigative data.


ENTITY_PATTERNS = [

    # --------------------------------------------------
    # Common Indian / South Asian person names
    # --------------------------------------------------

    {
        "label": "PERSON",
        "pattern": "Rahul Sharma"
    },
    {
        "label": "PERSON",
        "pattern": "Priya"
    },
    {
        "label": "PERSON",
        "pattern": "Amit Kumar"
    },
    {
        "label": "PERSON",
        "pattern": "Ravi Kumar"
    },

    # --------------------------------------------------
    # Common locations
    # --------------------------------------------------

    {
        "label": "GPE",
        "pattern": "Hyderabad"
    },
    {
        "label": "GPE",
        "pattern": "Bengaluru"
    },
    {
        "label": "GPE",
        "pattern": "Mumbai"
    },
    {
        "label": "GPE",
        "pattern": "Delhi"
    },
    {
        "label": "GPE",
        "pattern": "Chennai"
    },

    # --------------------------------------------------
    # Organizations
    # --------------------------------------------------

    {
        "label": "ORG",
        "pattern": "State Bank of India"
    },
    {
        "label": "ORG",
        "pattern": "Indian Railways"
    },
    {
        "label": "ORG",
        "pattern": "Cyber Crime Police"
    },
]