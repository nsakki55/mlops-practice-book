from pydantic import BaseModel


class AdRequest(BaseModel):
    impression_id: str
    logged_at: str
    user_id: int
    app_code: int
    os_version: str
    is_4g: int
