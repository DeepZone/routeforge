# Contributing to RouteForge

## Setup

```bash
git clone https://github.com/DeepZone/routeforge.git
cd routeforge
cp .env.example .env
docker compose up --build
```

## Backend Tests

```bash
cd backend
pytest -q
```

## Frontend Build

```bash
cd frontend
npm run build
```

## Pull Request Guidelines

- Keep pull requests focused and easy to review.
- Update documentation together with user-facing behavior changes.
- Add or update tests when behavior changes.
- Do not break existing API endpoints without explicit versioning and migration notes.

## Read-only safety principle

RouteForge is read-only by design.

## Do not add write operations without explicit design discussion

Do not add write operations (registry writes, ROA creation, router deployment, or similar mutating workflows) without an explicit design discussion and maintainer approval.
