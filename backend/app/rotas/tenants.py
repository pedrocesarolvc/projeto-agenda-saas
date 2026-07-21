"""
Rotas de tenant (Etapa 7, secao 7.3): so o suficiente para a
interface mostrar em qual negocio o usuario esta -- "o tenant nao e
invisivel, e parte da experiencia". CRUD completo de tenant nao e
escopo do v1; o cadastro do negocio ja acontece via
POST /auth/registrar-negocio (Etapa 2 + 7).
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.auth.dependencies import get_usuario_atual
from app.core.tenancy import get_tenant_id_atual
from app.database import get_session
from app.modelos.tenant import Tenant
from app.schemas.tenants import TenantResponse

router = APIRouter(prefix="/tenants", tags=["tenants"], dependencies=[Depends(get_usuario_atual)])


@router.get("/me", response_model=TenantResponse)
def meu_negocio(
    tenant_id: int = Depends(get_tenant_id_atual),
    session: Session = Depends(get_session),
) -> TenantResponse:
    return TenantResponse.model_validate(session.get(Tenant, tenant_id))
