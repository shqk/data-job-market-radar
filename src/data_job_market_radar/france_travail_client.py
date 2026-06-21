import httpx

from .models.settings import Settings
from .models.token import Token

# Encapsulate API calls


class FranceTravailApiError(RuntimeError):
    """
    Raised when France Travail API request fails
    """


class FranceTravailClient:
    def __init__(self, settings: Settings, token: Token):
        self.settings = settings
        self.token = token

    def _headers(self) -> dict[str, str]:
        if self.token.is_expired:
            raise FranceTravailApiError("Access token is expired.")
        return {
            "Authorization": self.token.authorization_header,
            "Accept": "application/json",
        }

    def search_jobs(self, keywords: str, job_range: str) -> httpx.Response:
        url = self.settings.search_url
        params = {"motsCles": keywords, "range": job_range}

        try:
            with httpx.Client() as client:
                jobs = client.get(url, headers=self._headers(), params=params, timeout=30.0)
                jobs.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise FranceTravailApiError(
                f"France Travail search endpoint returned status "
                f"{exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise FranceTravailApiError("Could not reach France Travail search endpoint.") from exc

        return jobs
