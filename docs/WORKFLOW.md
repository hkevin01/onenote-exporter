# Development Workflow

## Branching strategy
- main: stable
- feature/*: feature branches
- fix/*: bugfix branches

## CI/CD
- GitHub Actions CI lints and runs tests on pushes and PRs
- Dependabot weekly for pip and GitHub Actions
- Releases via GitHub Releases (manual)

## Code review
- Small PRs preferred
- Include context and screenshots when relevant
- Ensure CI is green before review
