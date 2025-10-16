# 🔑 Nonce Handling in the API

## Overview
The `nonce` is a **pass-through identifier** used for request-response correlation. The API does NOT validate, modify, or track nonces - it simply receives them and echoes them back.

## Data Flow

### 1. **Incoming Request** (TaskRequest)
```json
{
  "email": "student@example.com",
  "secret": "...",
  "task": "my-app",
  "round": 1,
  "nonce": "ab12-xyz-789",  ← Received from client
  "brief": "...",
  "checks": [...],
  "evaluation_url": "https://example.com/notify",
  "attachments": [...]
}
```

### 2. **Processing** (No Nonce Validation)
- ✅ Nonce is **received** as part of TaskRequest
- ❌ Nonce is **NOT validated** (no uniqueness check, format check, or deduplication)
- ❌ Nonce is **NOT stored** in any database or cache
- ❌ Nonce is **NOT used** for authentication or request tracking

### 3. **Outgoing Evaluation** (EvaluationPayload)
```json
{
  "email": "student@example.com",
  "task": "my-app",
  "round": 1,
  "nonce": "ab12-xyz-789",  ← Same nonce passed back
  "repo_url": "https://github.com/user/my-app",
  "commit_sha": "abc123...",
  "pages_url": "https://user.github.io/my-app/"
}
```

## Code Implementation

### models.py
```python
class TaskRequest(BaseModel):
    # ... other fields ...
    nonce: str  # Required field, no validation

class EvaluationPayload(BaseModel):
    # ... other fields ...
    nonce: str  # Passed through from request
```

### main.py - Round 1
```python
evaluation_payload = EvaluationPayload(
    email=request.email,
    task=request.task,
    round=1,
    nonce=request.nonce,  # ← Simply copied from request
    repo_url=repo.html_url,
    commit_sha=commit_sha,
    pages_url=pages_url
)
```

### main.py - Round 2
```python
evaluation_payload = EvaluationPayload(
    email=request.email,
    task=request.task,
    round=2,
    nonce=request.nonce,  # ← Simply copied from request
    repo_url=repo.html_url,
    commit_sha=commit_sha,
    pages_url=pages_url
)
```

## Purpose of Nonce

The nonce allows the **evaluation server** (not this API) to:

1. **Correlate requests and responses**
   - Match the evaluation callback to the original request
   
2. **Prevent replay attacks** (if the evaluation server implements it)
   - Track which nonces have been used
   - Reject duplicate nonces

3. **Trace requests** (if the evaluation server implements it)
   - Debug which request led to which evaluation
   - Audit trail of processing

## What This API Does

✅ **Receives nonce** from incoming request  
✅ **Validates nonce exists** (Pydantic requires it)  
✅ **Passes nonce back** in evaluation payload  

## What This API Does NOT Do

❌ **Generate nonces** - Client provides them  
❌ **Validate nonce format** - Any string accepted  
❌ **Check uniqueness** - Duplicates allowed  
❌ **Store nonces** - No persistence  
❌ **Expire nonces** - No time-based validation  
❌ **Prevent replay** - Same nonce can be reused  

## Example Scenarios

### Scenario 1: Same Nonce, Different Rounds
```bash
# Round 1 with nonce "abc-123"
curl -X POST /api-endpoint -d '{"nonce": "abc-123", "round": 1, ...}'
# Returns: {"nonce": "abc-123", ...}

# Round 2 with same nonce "abc-123" ✅ ALLOWED
curl -X POST /api-endpoint -d '{"nonce": "abc-123", "round": 2, ...}'
# Returns: {"nonce": "abc-123", ...}
```

### Scenario 2: Duplicate Requests (No Prevention)
```bash
# First request with nonce "xyz-789"
curl -X POST /api-endpoint -d '{"nonce": "xyz-789", ...}'

# Duplicate request with same nonce ✅ ALLOWED
curl -X POST /api-endpoint -d '{"nonce": "xyz-789", ...}'
# Will process again - no deduplication
```

### Scenario 3: Evaluation Server Correlation
```
Client Request → API → GitHub → Evaluation Server
                    ↓
            nonce: "unique-123"
                    ↓
                Evaluation Server receives:
                {
                  "nonce": "unique-123",
                  "repo_url": "...",
                  ...
                }
                    ↓
                Server matches to original request
```

## Security Implications

⚠️ **This API does NOT prevent:**
- Replay attacks (same request sent multiple times)
- Race conditions (concurrent requests with same nonce)
- Nonce collision (different requests with same nonce)

💡 **Recommendation:** The evaluation server should:
- Track received nonces
- Reject duplicate nonces
- Implement nonce expiration
- Validate nonce format

## Summary

The nonce is a **simple pass-through correlation ID**:
- Client generates it
- API receives it
- API echoes it back
- Evaluation server uses it for correlation

**The API trusts the client to provide unique nonces.**

