from .models.auth import Token
from .models.config import Settings

# Encapsulate API calls

class FranceTravailClient():
    def __init__(self, settings: Settings, token: Token):
        pass