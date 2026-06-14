from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone


class Token(BaseModel):
    access_token: str
    scope: str
    token_type: str
    expires_in: int

    # Fonction appelée à la création de l'objet => Field(datetime.now(timezone.utc)) n'est pas suffisant car le timestamp est calculé à l'import du fichier et pas à une nouvelle instance
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def expires_at(self) -> datetime:
        safety_margin_seconds = 60
        return self.created_at + timedelta(
            seconds=max(0, self.expires_in - safety_margin_seconds)
        )

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    @property
    def authorization_header(self) -> str:
        return f"{self.token_type} {self.access_token}"
