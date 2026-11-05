# Security Policy

## Reporting a vulnerability

Do not open a public issue or pull request for a security report.

Report it privately through a GitHub security advisory:
<https://github.com/fabriziosalmi/websites-monitor/security/advisories/new>

If you cannot use GitHub advisories, email fabrizio.salmi@gmail.com with a
subject starting with `[websites-monitor-security]`.

Include the version you tested (the `version` field of `GET /health`), the
steps to reproduce, and the impact you observed. Fixes are coordinated with
the reporter, and the advisory is published once a fixed version is
available.

## Supported versions

Security fixes land on `main`. Run the latest image or the latest commit.

## Deploying safely

The API has no authentication, and every check makes outbound requests to
the host it is given, including addresses inside your network. Anyone who
can reach the API can therefore make the server send requests on their
behalf. That includes a web page opened by someone on the same network:
the API accepts cross-origin requests from any origin, so that the web UI
hosted on GitHub Pages can call it. Publish it only on a trusted network or
behind an authenticating reverse proxy. Docker Compose publishes it on 127.0.0.1 unless
`WM_BIND_ADDRESS` says otherwise.

The same applies to the MCP server over HTTP
(`websites-monitor mcp --transport streamable-http`), which has no
authentication either. Over stdio it is only reachable by the process that
starts it.
