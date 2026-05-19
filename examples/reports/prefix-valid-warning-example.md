# Prefix Report Example: valid + warning context

> Demo data, not for operational use.

## Input

- Prefix: `203.0.113.0/24`
- Origin-AS: `AS64500`
- Mode: Demo

## Result overview

- Overall status: `WARNING`
- RPKI check: `OK` (`valid`)
- Registry/IRR plausibility check: `WARNING`

## Why this can happen

The prefix can be RPKI-valid while Registry/IRR signals are incomplete or ambiguous.  
In this demo case, route object hints are not strong enough for a confident positive assessment.

## Operator note

Use this as a triage signal:

1. Confirm route/route6 object status in authoritative tooling.
2. Confirm Origin-AS intent with current policy/process.
3. Keep RPKI and Registry results separate when communicating risk.
