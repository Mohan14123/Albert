from pydantic import BaseModel

class ProviderConfig(BaseModel):
    client_id: str
    client_secret: str
    scopes: list[str]
    redirect_uri: str
    api_base_url: str
