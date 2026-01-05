# Lego - AOC Integration Changes

This document describes the changes needed in lego to support the AOC leaderboard integration.

## Summary

The AOC leaderboard needs minimal user data (name, username, GitHub username) from Abakus users. This integration adds a new OAuth scope "aoc" that provides limited access to user data.

## Changes Made

### 1. New OAuth Scope: "aoc"

**File**: `lego/settings/base.py` (line ~144)

Added a new OAuth scope that requests minimal permissions:

```python
"aoc": (
    "Minimal brukerinfo for Advent of Code leaderboard. "
    "Gir lesetilgang til navn, brukernavn og GitHub-brukernavn"
),
```

**Why**: The default "user" scope requests too many permissions (email, profile picture, gender, memberships). The "aoc" scope only requests what's needed.

### 2. MinimalUserSerializer

**File**: `lego/apps/users/serializers/users.py` (line ~46)

Added a new serializer that returns only essential fields:

```python
class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing users with only essential fields.
    Used by Advent of Code integration
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "full_name",
            "github_username",
        )
        read_only_fields = fields
```

**Why**: Returns only the fields needed for AOC matching, reducing data exposure and improving performance.

### 3. Users API Endpoint Updates

**File**: `lego/apps/users/views/users.py`

#### 3a. Support for `?minimal=true` query parameter (line ~50)

```python
def get_serializer_class(self):
    # Support minimal query parameter for list actions
    if self.action == "list" and self.request.query_params.get("minimal") == "true":
        return MinimalUserSerializer
    # ... rest of method
```

**Endpoint**: `GET /api/v1/users/?minimal=true`

**Why**: Allows clients to request only minimal user data when fetching user lists.

#### 3b. Scope-aware oauth2_userdata endpoint (line ~89)

```python
def oauth2_userdata(self, request):
    """
    Read-only endpoint used to retrieve information about the authenticated user.
    Returns minimal data if the OAuth scope is 'aoc'.
    """
    # Check if the request is using the 'aoc' scope
    token = getattr(request.auth, 'token', None) if hasattr(request, 'auth') else None
    scope = token.scope if token and hasattr(token, 'scope') else None

    if scope and 'aoc' in scope:
        # Use minimal serializer for aoc scope
        serializer = MinimalUserSerializer(request.user)
    else:
        # Use default OAuth2 serializer
        serializer = self.get_serializer(request.user)

    return Response(serializer.data)
```

**Why**: Automatically returns minimal data when using "aoc" scope, enforcing least-privilege access.

### 4. OAuth Authentication Updates

**File**: `lego/apps/oauth/authentication.py` (line ~30)

Added "aoc" scope to allowed scopes:

```python
# Allow "aoc" scope for oauth2_userdata and users list endpoints
if token.allow_scopes(["aoc"]):
    allowed_paths = [
        "/api/v1/users/oauth2_userdata/",
        "/api/v1/users/"
    ]
    if request.path in allowed_paths:
        return authentication
```

**Why**: Allows OAuth tokens with "aoc" scope to access the necessary endpoints.

## API Usage

### For AOC Integration

**1. OAuth Flow:**
```
GET /authorization/oauth2/authorize/?client_id=xxx&scope=aoc&redirect_uri=xxx&...
```

**2. Get current user (minimal):**
```
GET /api/v1/users/oauth2_userdata/
Authorization: Bearer <token>

Response:
{
  "id": 123,
  "username": "viljen",
  "full_name": "Viljen Jensen",
  "github_username": "viljen"
}
```

**3. Get all users (minimal):**
```
GET /api/v1/users/?minimal=true
Authorization: Bearer <token>

Response:
{
  "results": [
    {
      "id": 123,
      "username": "viljen",
      "full_name": "Viljen Jensen",
      "github_username": "viljen"
    },
    ...
  ]
}
```

## Deployment Checklist

When deploying to staging/production:

- [ ] Apply all 4 code changes listed above
- [ ] Restart lego server to load new scope
- [ ] Run `setup_aoc_oauth.py` script to create OAuth application
- [ ] Test OAuth flow with "aoc" scope
- [ ] Verify minimal data is returned

## Security Considerations

1. **Least Privilege**: The "aoc" scope only grants access to minimal user data
2. **Limited Endpoints**: OAuth authentication restricts "aoc" tokens to specific endpoints only
3. **No Write Access**: All endpoints are read-only for "aoc" scope
4. **User Consent**: Users must explicitly approve access during OAuth flow

## Backward Compatibility

These changes are fully backward compatible:
- Existing "user" and "all" scopes work unchanged
- Existing OAuth applications are not affected
- The MinimalUserSerializer is only used when explicitly requested
- No changes to existing API responses

## Testing

```bash
# Test OAuth flow with aoc scope
curl -X GET "http://localhost:8000/authorization/oauth2/authorize/?client_id=xxx&scope=aoc&..."

# Test minimal user data endpoint
curl -X GET "http://localhost:8000/api/v1/users/oauth2_userdata/" \
  -H "Authorization: Bearer <token>"

# Test minimal users list
curl -X GET "http://localhost:8000/api/v1/users/?minimal=true" \
  -H "Authorization: Bearer <token>"
```
