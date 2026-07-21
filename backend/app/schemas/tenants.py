from pydantic import BaseModel


class TenantResponse(BaseModel):
    id: int
    nome: str

    model_config = {"from_attributes": True}
