# API auth only
import httpx
from .models.auth import Token
from .models.config import Settings

class AuthenticationError(RuntimeError):
    """Raised when France Travail auth fails."""

def get_access_token(settings: Settings) -> Token:
    
    body = {
        'grant_type' : 'client_credentials',
        'client_id' : settings.client_id,    
        'client_secret' : settings.client_secret,
        'scope' : settings.scope    
        }

    url = settings.token_url

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'realm' : '/partenaire'}
    
    try:
        response = httpx.post(url, params=params, data=body, headers=headers, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AuthenticationError(
            "Failed to retrieve France Travail access token"
        ) from exc
    
    try:
        return Token.model_validate(response.json())
    except ValueError as exc:
        raise AuthenticationError("France Travail token response is not valid JSON.") from exc
