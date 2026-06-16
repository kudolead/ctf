# Answer — SIEM Password Hunt

**Flag:** `flag{REPLACE_ME_siem_password_hunt}`
**Zip password:** `REPLACE1REPLACE2REPLACE3` (= part1 + part2 + part3)
**Join rule:** direct concatenation in checkpoint order (1 → 2 → 3).

## Fragments

| # | Stage | Where it's planted | Encoded as | Fragment |
|---|-------|--------------------|-----------|----------|
| 1 | Initial access | web/auth log | base64 in query string / UA | `REPLACE1` |
| 2 | Execution | process-creation log | PowerShell `-enc` payload | `REPLACE2` |
| 3 | Exfiltration | proxy/DNS log | upload path / beacon host | `REPLACE3` |

## Attack timeline

1. **Initial access** — _describe the suspicious request once implemented._
2. **Execution / persistence** — _describe the decoded command line._
3. **Exfiltration** — _describe the upload/beacon._

> Replace all placeholders once `build/build.py` is implemented, and keep the
> join rule identical in build, solve, and here.
