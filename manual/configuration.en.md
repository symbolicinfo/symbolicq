# Installation and Configuration

## Install

Install from a package index:

```bash
pip install symbolicq
```

Install from the source tree for development:

```bash
pip install -e .[dev]
```

## Default Server

The built-in `base_url` is:

```text
https://q.symbolicinfo.com
```

Without explicit configuration, `SymbolicQBackend()` and `SymbolicQClient()` use that endpoint.

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
print(backend.client.base_url)
```

## Resolution Order

`base_url` and `api_key` are resolved in this order. The first non-empty value wins.

1. Explicit constructor argument
2. `SYMBOLICQ_API_URL` / `SYMBOLICQ_API_KEY` environment variables
3. `API_URL` / `API_KEY` environment variables
4. Built-in default URL, with no default API key

## Environment Variables

Bash:

```bash
export API_URL=https://q.symbolicinfo.com
export API_KEY=your-secret-token
```

PowerShell:

```powershell
$env:API_URL = "https://q.symbolicinfo.com"
$env:API_KEY = "your-secret-token"
```

Explicit constructor values still take precedence:

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend(
    base_url="https://q.symbolicinfo.com",
    api_key="your-secret-token",
    timeout=60.0,
)
```

When an API key is set, every request includes:

```text
Authorization: Bearer your-secret-token
```

## Health Check

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient()
print(client.health())
```

If the server is healthy, this returns the `/health` JSON payload documented in API.md.
