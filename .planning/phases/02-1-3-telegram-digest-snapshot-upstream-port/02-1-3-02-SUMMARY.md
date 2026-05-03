---
phase_plan: "02-1-3-02-PLAN.md"
status: completed
completed: "2026-05-03"
---

## Objective

Durably land the telegram digest snapshot patch pipeline in **`FirasY-TE/openclaw-ops`** (`~/openclaw-ops`), not in `openclaw/openclaw` VPS patches per cursor rule.

## Ops changes (`~/openclaw-ops/vps/`)

| File                                                 | Purpose                                                                                                                                                                          |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.openclaw-version`                                  | Full SHA `1c0672b74f66038fd4ee76fbf1c21715887149d8` — reliable `git fetch` for build script                                                                                      |
| `patches/0001-telegram-triage-digest-snapshot.patch` | Unified diff from Plan 01 (17073 bytes)                                                                                                                                          |
| `build-patched-openclaw.sh`                          | `set -euo pipefail`; clone/fetch/checkout; `git apply -p1`; `pnpm install`; `pnpm build`; `npm pack`; prints tarball path                                                        |
| `deploy.sh`                                          | `--with-core` + `OPENCLAW_PACK_TGZ` → `scp` tarball to host, `docker cp` into container, `docker exec CONTAINER npm install -g`; `--restart` → `docker compose restart openclaw` |
| `README.md`                                          | Patched rebuild flow, recursive `grep -rl OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID …/dist`, 4096 sentinel UAT                                                                     |

## Automated verification

```bash
bash -n ~/openclaw-ops/vps/build-patched-openclaw.sh
bash -n ~/openclaw-ops/vps/deploy.sh
grep -q with-core ~/openclaw-ops/vps/deploy.sh && grep -q 'docker exec' ~/openclaw-ops/vps/deploy.sh && echo OK
cd ~/openclaw-ops/vps && ./build-patched-openclaw.sh    # exits 0; ~7 min locally
```

## Patched tarball sample (scratch build host)

Example artifact path (ephemeral TMPDIR; path varies):

`/var/folders/.../T/openclaw-patched-build-68709/openclaw-2026.4.12.tgz`

`shasum -a 256` (single reproducibility sample — rerun script for pairwise compare):

```
4b5b1149199afe61fe51152ec673a2ed0dc2a9f40a0056d5d883d7ae9ac73a82
```

Emitted JS contains `OPENCLAW_TRIAGE_DIGEST_SNAPSHOT_CHAT_ID` (located under `dist/bot-*.js` in unpacked/published layout).

## Live VPS transcript

Not run from this workspace (needs network + Tailscale SSH). Operator: set `OPENCLAW_PACK_TGZ` to tarball from `./build-patched-openclaw.sh`, then `./deploy.sh --with-core --restart`; run README `grep -rl …` smoke on the container.

## Commit bookkeeping

Apply `git commit` in `~/openclaw-ops` with the staged `vps/*` subtree after review.

## Self-check: PASSED (automated); live deploy pending operator
