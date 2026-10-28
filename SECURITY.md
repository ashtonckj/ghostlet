# Security Policy

## What Ghostlet touches

Ghostlet is meant to be harmless by design. Any change that widens this list needs a strong
reason and a maintainer's approval.

| Touches | Why |
|---------|-----|
| Time of last input (`GetLastInputInfo`) | To know when you are idle. Never keys, mouse positions, or screen contents. |
| Mouse cursor position, while ghosts are out | So ghosts appear near it and flee away from it. |
| `%APPDATA%\Ghostlet\settings.json` | Your settings. |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` → `Ghostlet` | Only when "Launch at Windows sign-in" is on. Removed when turned off. |
| Local named pipe `ghostlet-<username>` | Stops a second copy from starting and opens Settings in the copy that is already running instead. |

Ghostlet makes **no network connections** and asks for **no admin rights**. It has no
accounts, analytics, telemetry, or auto-update.

## Supported versions

Only the latest release gets security fixes.

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Report privately through GitHub: **Security** tab → **Report a vulnerability**.
Include the steps to reproduce it, what an attacker could gain, and your Ghostlet and
Windows versions.

You should hear back within 7 days. Once a fix ships, we will credit you unless you
would rather stay anonymous.

## Downloads

Only download `Ghostlet.exe` from this repository's Releases page. The exe is not code-signed
yet, so Windows SmartScreen may warn you. If you prefer, build it yourself from source
(see [CONTRIBUTING.md](CONTRIBUTING.md)).
