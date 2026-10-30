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
| `api.github.com` (one HTTPS GET) | An update check, at start-up and then once a day. It sends nothing about you, only what any web request carries (your IP address, and a `Ghostlet/<version>` user agent). Turn it off with **Settings → Check for updates**. |
| `github.com/<owner>/<repo>/releases/download/...` | Only when you click **Update** in the popup: downloads the new `Ghostlet.exe`. |

Those two GitHub requests are the only network use. Ghostlet asks for **no admin rights** and has
no accounts, analytics or telemetry.

## How updates are protected

- Only a `.exe` hosted on this repository's Releases page is ever downloaded or run.
- The download must match the size, and the SHA-256 checksum when GitHub provides one, that the
  release reports, and it must be a Windows program. Otherwise nothing is changed.
- The old exe is kept as `Ghostlet.exe.old` during the swap (removed on the next start), and is put back if
  swapping fails.
- Updates are **not code-signed**. Anyone who can publish a release on the repository can ship code
  to every user, so keep two-factor authentication on for maintainer accounts.

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
