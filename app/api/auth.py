"""
Authentication & Authorization Module

Current Implementation:
- API Key authentication for development and CI/CD
- Header-based token validation
- Dependency injection for route protection

Future Integration:
- Azure AD / Azure Entra ID OAuth 2.0
- AWS IAM / Cognito
- Okta SSO
- Role-based access control (RBAC)

Security Notes:
- API keys should be rotated regularly
- Use environment variables, never hardcode
- In production, migrate to OAuth 2.0 / OIDC
- Implement token expiration and refresh logic
"""

from fastapi import Header, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from typing import Optional
import os
import secrets

# API Key Configuration
# In production, this should come from Azure Key Vault or AWS Secrets Manager
API_KEY = os.getenv("API_KEY", "")
API_KEY_NAME = "X-API-Key"

# FastAPI Security Scheme for automatic OpenAPI documentation
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header)
) -> dict:
    """
    Verify API key from request header.
    
    Designed for integration with:
    - Azure AD / Azure Entra ID (OAuth 2.0)
    - AWS IAM / Cognito
    - Okta SSO
    - Custom identity providers
    
    Current Implementation:
    - Simple API key comparison for development
    - Constant-time comparison to prevent timing attacks
    
    Args:
        x_api_key: API key from request header
    
    Returns:
        dict: Authentication context with user info
    
    Raises:
        HTTPException: 401 if authentication fails
    
    Example:
        @app.get("/protected")
        async def protected_route(auth: dict = Depends(verify_api_key)):
            return {"user": auth["user_id"]}
    """
    
    # Check if API key is configured
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API_KEY not set",
            headers={"WWW-Authenticate": "API Key"}
        )
    
    # Check if API key was provided
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "API Key"}
        )
    
    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API Key"}
        )
    
    # Return authentication context
    # In production, this would include user info from the identity provider
    return {
        "authenticated": True,
        "user_id": "api_key_user",  # TODO: Extract from JWT/OAuth token
        "role": "user",  # TODO: Extract from JWT claims or directory
        "tenant_id": "default",  # TODO: Multi-tenant support
        "scopes": ["chat:read", "chat:write"]  # TODO: Extract from token
    }


# TODO: Azure AD / OAuth 2.0 Integration
"""
Future implementation for Azure AD integration:

from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Azure AD Configuration
AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")
AZURE_AD_CLIENT_SECRET = os.getenv("AZURE_AD_CLIENT_SECRET")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2/v2.0/token"
)

async def verify_azure_ad_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            key=AZURE_AD_CLIENT_SECRET,
            algorithms=["RS256"],
            audience=AZURE_AD_CLIENT_ID
        )
        
        # Extract user information
        return {
            "authenticated": True,
            "user_id": payload.get("oid"),  # Object ID
            "email": payload.get("email"),
            "name": payload.get("name"),
            "role": payload.get("roles", ["user"])[0],
            "tenant_id": payload.get("tid"),
            "scopes": payload.get("scp", "").split()
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
"""


# Optional: Role-based authorization decorator
def require_role(required_role: str):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(auth: dict = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    """
    def role_checker(auth_context: dict = Security(verify_api_key)) -> dict:
        user_role = auth_context.get("role", "")
        
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return auth_context
    
    return role_checker


# Optional: Scope-based authorization
def require_scope(required_scope: str):
    """
    Decorator to enforce scope-based access control.
    
    Usage:
        @app.post("/chat")
        async def chat(auth: dict = Depends(require_scope("chat:write"))):
            return {"message": "Access granted"}
    """
    def scope_checker(auth_context: dict = Security(verify_api_key)) -> dict:
        user_scopes = auth_context.get("scopes", [])
        
        if required_scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        
        return auth_context
    
    return scope_checker
