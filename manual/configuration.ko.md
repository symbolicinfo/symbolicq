# 설치와 설정

## 설치

패키지 index에서 설치:

```bash
pip install symbolicq
```

개발을 위해 source tree에서 설치:

```bash
pip install -e .[dev]
```

## 기본 서버

내장 `base_url`은 다음과 같습니다.

```text
https://q.symbolicinfo.com
```

명시적인 설정이 없으면 `SymbolicQBackend()`와 `SymbolicQClient()`는 이 endpoint를 사용합니다.

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend()
print(backend.client.base_url)
```

## 결정 순서

`base_url`과 `api_key`는 다음 순서로 결정됩니다. 비어 있지 않은 첫 번째 값이 사용됩니다.

1. 명시적인 constructor argument
2. `SYMBOLICQ_API_URL` / `SYMBOLICQ_API_KEY` 환경 변수
3. `API_URL` / `API_KEY` 환경 변수
4. 내장 기본 URL. 기본 API key는 없음

## 환경 변수

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

명시적인 constructor 값이 여전히 우선합니다.

```python
from symbolicq import SymbolicQBackend

backend = SymbolicQBackend(
    base_url="https://q.symbolicinfo.com",
    api_key="your-secret-token",
    timeout=60.0,
)
```

API key가 설정되면 모든 request에 다음 header가 포함됩니다.

```text
Authorization: Bearer your-secret-token
```

## Health Check

```python
from symbolicq import SymbolicQClient

client = SymbolicQClient()
print(client.health())
```

서버가 healthy 상태이면 API.md에 문서화된 `/health` JSON payload를 반환합니다.
