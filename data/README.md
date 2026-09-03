# Data

Development datasets and data-ingestion resources.

## Data Sources

The project may use:

- FIR / police reports
- CDR / communication records
- Financial transactions
- Surveillance records
- Social intelligence
- Criminal history
- Intelligence reports
- Vehicle records
- Organization/company data

## Dataset Strategy

The prototype will use a combination of:

- Public datasets where appropriate
- Synthetic datasets

Synthetic datasets should contain intentionally planted relationships
that allow the system to demonstrate hidden-network discovery across
multiple sources.

## Structure

```text
data/
├── fir/
├── cdr/
├── financial/
├── surveillance/
├── social/
├── criminal_history/
├── intelligence_reports/
├── vehicles/
└── organizations/
