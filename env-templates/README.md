# Environment Templates

Copy one shared template plus one service template to create runtime env files.

## Suggested steps

1. Copy `./.env.shared.example` to `.env.shared.<env>`.
2. Copy service template to `.env.<service-name>.<env>`.
3. Fill in real secrets locally.
4. Load shared first, then service file.

## Example

- `.env.shared.dev`
- `.env.iam-admin-service.dev`
