# Security Policy

## Scope

SignalFlow is a read-only research application: a FastAPI backend serves a
fixed, precomputed historical dataset over `GET` endpoints, and a React
frontend renders it. There is **no authentication, no database, no
user-submitted data, and no write path anywhere in the system**. This
significantly limits the categories of vulnerability that apply here — most
of the OWASP Top 10 (injection, broken authentication, CSRF, insecure
deserialization of user input) don't have an entry point to exploit,
because there is no untrusted input for them to act on.

What *does* apply, and what this project actually does about it:

| Concern | Status |
|---|---|
| Secrets in the repository | None exist. No API keys, tokens, or credentials are required to run this project (see Installation in `README.md`). |
| CORS | Restricted to the local Vite dev origins (`localhost:5173` / `127.0.0.1:5173`) and `GET` only — see `backend/app/main.py`. |
| Cross-site scripting (XSS) | No `dangerouslySetInnerHTML`, `innerHTML`, or `eval` anywhere in the frontend. All dynamic content is rendered through JSX text interpolation, which React escapes by default. |
| Reverse tabnabbing | Every external link (`target="_blank"`) uses `rel="noreferrer"`. |
| Dependency vulnerabilities | Audited with `pip-audit` and `npm audit` as of the last update to this file — zero known vulnerabilities in this project's declared dependencies. Re-run both before relying on this claim in the future; it is not continuously monitored. |
| Injection (SQL, command, etc.) | No database and no shell/subprocess execution of user input anywhere in the codebase. |

## Reporting a Vulnerability

This is a personal research/portfolio project, not a production service
handling real user data. If you find a genuine security issue anyway (for
example, a way to make the API leak more than it intends to, or a supply-chain
issue in a dependency), please open a GitHub issue describing it. There is no
formal disclosure program or bounty — this is a best-effort, single-maintainer
project.

## What This Project Does Not Claim

This document intentionally does not use language like "enterprise-grade,"
"hardened," or "production-ready." The security posture here is appropriate
for what the project actually is: a small, read-only, keyless, no-auth
research tool. Deploying this publicly on the open internet would require
revisiting the CORS policy and adding basic rate limiting at minimum — see
the Future Improvements section of `README.md`.
