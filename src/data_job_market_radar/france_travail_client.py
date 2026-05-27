from .models.token import Token
from .models.settings import Settings
import httpx

# Encapsulate API calls

class FranceTravailApiError(RuntimeError):
    """
        Raised when France Travail API request fails
    """

class FranceTravailClient():
    def __init__(self, settings: Settings, token: Token):
        self.settings = settings
        self.token = token
    
    def _headers(self) -> dict[str, str]:
        if self.token.is_expired:
            raise FranceTravailApiError
        return {
            "Authorization" : self.token.authorization_header,
            "Accept" : "application/json"
        }
    
    def search_jobs(self, keywords: str, job_range: str):
        url = self.settings.search_url
        params = {
            "motsCles" : keywords,
            "range" : job_range
        }

        with httpx.Client() as client:
            jobs = client.get(url, headers=self._headers(), params=params)
        
        print(jobs.request.url)
        
        return jobs