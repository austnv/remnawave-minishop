# Cloudflare Pages deploy

This docs site is built with Astro Starlight and publishes to:

```text
https://minishop.minidoc.cc
```

## Cloudflare Pages settings

Create a Pages project connected to the GitLab repository and use:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Framework preset | `Astro` |
| Root directory | `docs-site` |
| Build command | `npm ci && npm run build` |
| Build output directory | `dist` |
| Node version | `22` |

The build script runs `scripts/sync-docs.mjs` before Astro builds the site. Keep editing the canonical Markdown files in the repository-level `docs/` directory.

## Custom domain

After the first successful Pages deploy:

1. Open the Pages project in Cloudflare.
2. Go to **Custom domains**.
3. Add `minishop.minidoc.cc`.
4. If `minidoc.cc` is already on Cloudflare DNS, accept the suggested DNS record and wait for TLS activation.

## Optional API automation

Do not use a root token for automation. Create a scoped Cloudflare API token and expose it locally as an environment variable only for the setup command.

Minimum useful permissions:

| Scope | Permission |
| --- | --- |
| Account | Cloudflare Pages: Edit |
| Zone: `minidoc.cc` | Zone: Read |
| Zone: `minidoc.cc` | DNS: Edit |

Cloudflare's GitLab integration still requires the Cloudflare GitLab app/OAuth connection to be authorized for the repository. If that is not connected yet, complete the GitLab connection in the Cloudflare dashboard first, or use a direct-upload Pages workflow instead of Git-connected deployments.
