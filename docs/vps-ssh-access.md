# VPS SSH access (Hostinger + Tailscale)

When OpenClaw runs on a VPS (e.g. Hostinger) and you have SSH from your Mac (e.g. via Tailscale), the Cursor agent can run OpenClaw commands on the VPS by SSHing from your machine.

**Hostinger Docker project name:** `openclaw-ridl`. OpenClaw runs inside the container **`openclaw-ridl-openclaw-1`**. Run OpenClaw CLI via `docker exec` (see below). To get a shell inside the container: `docker exec -it openclaw-ridl-openclaw-1 bash`.

**Important:** All `ssh openclaw-vps "..."` commands are run **from your Mac**. Do not run them on the VPS itself (the VPS has no `openclaw-vps` host in its SSH config).

## Step-by-step setup

### Step 1: Open your SSH config on your Mac

- Open Terminal (or your preferred terminal app).
- Edit your SSH config:

  ```bash
  nano ~/.ssh/config
  ```

  (Or use `code ~/.ssh/config` if you prefer VS Code/Cursor; create the file if it does not exist.)

### Step 2: Add the VPS host block

Add the following block (use your actual Tailscale IP and username if different):

```
Host openclaw-vps
    HostName 100.114.26.58
    User root
```

- **HostName** must be the VPS Tailscale IP or Tailscale hostname (e.g. `100.114.26.58` or `myhost.your-tailnet.ts.net`).
- **User** is the SSH user on the VPS (e.g. `root` or another user).

Save and exit (`Ctrl+O` then `Enter`, then `Ctrl+X` in nano).

### Step 3: Ensure key-based login (no password prompt)

- Your Mac must have an SSH key and the public key must be on the VPS (e.g. in `~/.ssh/authorized_keys` for the user you use).
- If you already SSH into this VPS from your Mac without typing a password, you are done with this step.
- If you still get a password prompt, add your public key to the VPS:

  ```bash
  ssh-copy-id openclaw-vps
  ```

  (After this, `ssh openclaw-vps` should not ask for a password.)

### Step 4: Test SSH from your Mac

Run:

```bash
ssh openclaw-vps "echo ok"
```

- If you see `ok` and no password prompt, SSH is set up correctly.
- If you see permission or connection errors, check: Tailscale is running on both Mac and VPS, and the VPS firewall allows SSH (or Tailscale traffic).

### Step 5: (Optional) Verify OpenClaw on the VPS

Run this **from your Mac** (not from the VPS):

```bash
ssh openclaw-vps "docker exec openclaw-ridl-openclaw-1 openclaw channels status --probe"
```

Or list containers:

```bash
ssh openclaw-vps "docker compose -p openclaw-ridl ps"
```

Once these work from your Mac, the Cursor agent can run the same commands for you.

## One-time setup (summary)

1. **SSH host alias**  
   In `~/.ssh/config` on your Mac, add a `Host` entry for the VPS (see Step 2 above). Use the Tailscale IP or hostname.

2. **Key-based auth**  
   Ensure you can run `ssh openclaw-vps "echo ok"` without a password (Steps 3–4).

## Credential deployment (GWS OAuth)

After re-authenticating GWS on your Mac and exporting credentials, deploy them to the container and **fix ownership**:

```bash
# Copy to VPS host, then into container
scp ~/secrets/gws-reauth/credentials.json openclaw-vps:/tmp/cred-personal.json
ssh openclaw-vps "docker cp /tmp/cred-personal.json openclaw-ridl-openclaw-1:/data/openclaw-gws/config/credentials.json"

# CRITICAL: fix ownership — gateway runs as user `node`, not root
ssh openclaw-vps "docker exec openclaw-ridl-openclaw-1 chown node:node /data/openclaw-gws/config/credentials.json"
```

Repeat for rental credentials (`rental-credentials.json`). Without `chown node:node`, the cron pipeline silently fails because `docker exec` defaults to root (masking the issue) but the gateway's subprocesses run as `node`.

## How the agent uses it

The agent runs commands **from your Mac** via SSH. OpenClaw lives in the container `openclaw-ridl-openclaw-1`, so use `docker exec` (no `-it` for non-interactive):

- `ssh openclaw-vps "docker exec openclaw-ridl-openclaw-1 openclaw channels status --probe"`
- `ssh openclaw-vps "docker exec openclaw-ridl-openclaw-1 openclaw config set gateway.mode local"`
- `ssh openclaw-vps "docker compose -p openclaw-ridl ps"` (list containers)

To get a shell inside the container (interactive, from Mac):  
`ssh -t openclaw-vps "docker exec -it openclaw-ridl-openclaw-1 bash"`

The Cursor rule **VPS SSH (openclaw-vps)** uses host alias `openclaw-vps` and container `openclaw-ridl-openclaw-1`. If your alias or container name differs, edit `.cursor/rules/vps-ssh-openclaw.mdc`.

## Forum Topic Routing Migration Reference

The canonical operator checklist lives in `docs/cron-jobs.txt` under:
`PHASE 1 FORUM TOPIC ROUTING CHECKLIST (OPERATOR)`.

Use that section for:
- Forum/topic setup (`Triage Digest`, `System/Auth`, plus remaining topics)
- Route map env wiring (`triage_digest`, `system_auth`, etc.)
- Validation commands and fallback test procedure
