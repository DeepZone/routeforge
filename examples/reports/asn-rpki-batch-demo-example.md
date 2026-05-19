# ASN-RPKI Batch Demo Report Example

> Demo data, not for operational use.

## Input

- ASN: `AS64501`
- Batch limit: `25`
- Mode: Demo

## Batch summary

- Checked prefixes: `8`
- Prefixes seen: `8`
- valid: `5`
- invalid_asn: `1`
- invalid_length: `1`
- unknown: `1`
- errors: `0`

## Interpretation

- Majority valid indicates baseline ROA coverage exists.
- `invalid_asn` indicates at least one prefix appears with a non-authorized origin.
- `invalid_length` indicates a max-length mismatch risk.
- `unknown` means no conclusive validation result was available for that prefix.

## Follow-up actions

1. Review invalid entries first (`invalid_asn`, `invalid_length`).
2. Confirm announcements against intended origin policy.
3. Treat unknown results as investigation backlog, not immediate acceptance.
