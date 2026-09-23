# Lab signature notes

A record of the signatures the contributor built against **one lab
application**, each scoped by `destination-address` to a single test host.
They show how the workflow played out; they are **not** a library to deploy.
Every row is **[unverified]** outside that lab, and several would cause heavy
false positives on real traffic.

| Name | Context | Pattern idea | Direction | Lab action | Risk outside the lab |
|---|---|---|---|---|---|
| `CUSTOM-HTTP-BRUTEFORCE` | `http-post-url-parsed` + time binding | 5+ requests to a login path | client-to-server | close-client-and-server | Blocks legitimate retries and shared-NAT users; tune count and window |
| `CUSTOM-SQL-INJECTION` | `stream` | `UNION` … `SELECT` | client-to-server | close-client-and-server | Matches ordinary text containing both words; prefer a parsed context |
| `CUSTOM-XSS-INJECTION` | `stream` | bare `script`, `onerror`, `onload` | client-to-server | close-client-and-server | **Severe:** `script` is a substring of `description`, `subscription`, `JavaScript` |
| `CUSTOM-CMD-INJECTION` | `http-post-variable-parsed` | `&&`, `;`, `\|` | client-to-server | close-client-and-server | **Severe:** these characters occur in normal form input |
| `CUSTOM-SQL-TAUTOLOGY` | `stream` | quote + SQL comment sequence | client-to-server | close-client-and-server | Moderate; review against real form data |
| `CUSTOM-DIR-LISTING` | `stream` | `Index of /` | server-to-client | no-action (info) | Low; monitor only by design |
| `CUSTOM-SENSITIVE-FILE-ACCESS` | `stream` | `.bak` `.old` `.swp` `.sql` `.env` | client-to-server | close-client-and-server | Matches those strings anywhere in the stream, not only in paths; prefer a URL context |

## What the lab taught

- **`close-client-and-server` was the most consistent action** for this lab's
  HTTP test traffic; `drop-packet` and `drop-connection` did not reliably do
  better. That is a result for one traffic shape, not a default.
- **Commit is not load.** The policy compiled in the background after commit,
  and detection lagged the commit message. Poll
  `show security idp policy-commit-status`.
- **Stored state produces false passes.** A persisted-XSS test matched an
  earlier run's stored payload and reported success for an attempt that had
  actually been blocked. Use run-unique markers.
- **A missing `application-services` binding looks like a bad signature.**
  Every signature went silent at once; the cause was the policy binding, not
  the patterns.

## Before reusing any row

1. Replace bare-word and single-character patterns with specific ones, using
   `\[...\]` for case-insensitive matching.
2. Prefer a parsed HTTP context over `stream` when the traffic is HTTP.
3. Run a false-positive test with realistic traffic in `no-action` first.
4. Keep the `destination-address` scope until that review is complete.
