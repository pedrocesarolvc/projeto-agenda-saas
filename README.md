# Projeto Agenda

SaaS de agendamento multi-tenant para pequenos negócios de serviço (barbearias, estúdios, oficinas).

![A agenda em funcionamento](docs/agenda.gif)

> *GIF ainda não gravado — grave uma navegação rápida pela agenda (marcar um horário clicando num espaço livre, arrastar para remarcar, ver o 409 acontecer) e salve em `docs/agenda.gif`. É a imagem que mais representa este projeto (seção 7.7 da documentação); vale mais que qualquer parágrafo aqui embaixo.*

## Como rodar

```bash
git clone <este-repositorio>
cd projeto-agenda
docker compose up
```

- **Interface**: http://localhost:5173
- **API**: http://localhost:8000 (docs interativos em `/docs`)
- **Postgres**: `localhost:5432` (usuário/senha `postgres`, banco `projeto_agenda`)

O backend aplica as migrations automaticamente ao subir (`alembic upgrade head`); não precisa rodar nada à parte. Crie o primeiro negócio pela tela de cadastro (`/registrar`) — não há usuário seed.

Para parar: `Ctrl+C`. Para remover os containers: `docker compose down` (acrescente `-v` para também apagar os dados do Postgres e começar do zero).

### Modo desenvolvimento (sem Docker, com hot-reload)

Útil para editar o código e ver o resultado sem reconstruir imagem. Precisa de Python 3.12+, Node 20+ e um Postgres acessível (o mais simples é subir só o banco via Docker: `docker compose up postgres`).

**Backend** — um terminal:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# aponta para o Postgres do docker-compose (ou outro Postgres seu)
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/projeto_agenda   # Linux/Mac: export
set SECRET_KEY=uma-chave-qualquer-para-dev

alembic upgrade head
uvicorn app.main:app --reload
```

API em http://localhost:8000, recarregando a cada alteração em `backend/app/`.

**Frontend** — outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Interface em http://localhost:5173, recarregando a cada alteração em `frontend/src/`. Por padrão já aponta para `http://localhost:8000`; para mudar, crie `frontend/.env.local` com `VITE_API_URL=http://outro-endereco`.

## O que existe

Vários negócios operando isolados na mesma aplicação, com autenticação por papel (dono/atendente), uma regra de conflito de horário à prova de concorrência, CRUD de produção com paginação/filtro/busca, e uma interface de agenda visual. As sete etapas de construção estão documentadas passo a passo em [`docs/documentacao.md`](docs/documentacao.md).

| Recurso | Rotas |
|---|---|
| Auth | `POST /auth/login`, `POST /auth/registrar-negocio`, `GET /auth/me` |
| Tenant | `GET /tenants/me` |
| Serviços | CRUD completo em `/servicos` (escrita restrita a dono) |
| Clientes | CRUD completo em `/clientes` |
| Agendamentos | CRUD em `/agendamentos` + `PATCH /agendamentos/{id}/status` |

## Decisões de arquitetura (o porquê)

**Multi-tenancy por `tenant_id`, não schema nem banco por tenant.** Toda tabela do domínio carrega a coluna, e o filtro é injetado num ponto único (`core/tenancy.py`), nunca escrito à mão em cada rota — a defesa contra o erro mais comum de SaaS multi-tenant é não confiar na memória do programador. O teste que prova isso é o mais valioso do projeto: dois negócios completos, e um tentando alcançar o dado do outro por toda rota (listar, buscar, ler por id, editar, remarcar) — todas falham (`tests/test_e2e.py`).

**JWT amarrado ao tenant.** O token carrega `sub`, `tenant_id` e `role`; nenhum dos três vem de um parâmetro que o cliente escolhe — vêm sempre do cadastro do usuário, decididos pelo servidor no login. Um `tenant_id` forjado no corpo da requisição é ignorado, nunca lido.

**A race condition do agendamento, fechada em duas camadas.** Marcar dois clientes no mesmo horário é impedido por uma verificação em código (mensagem amigável, "esse horário já está ocupado") *e* por uma `EXCLUDE` constraint no Postgres (`tenant_id WITH =, tstzrange(inicio, fim) WITH &&`) — a garantia real sob concorrência. Testado com duas threads reais disputando o mesmo horário contra Postgres (`tests/test_race_condition.py`): a constraint decide, não a sorte de qual requisição chegou primeiro.

**A regra de negócio mora na camada de serviço, não na rota.** `app/servicos/` decide o domínio (conflito de horário, máquina de estados do agendamento); `app/rotas/` só traduz HTTP. Testável sem subir a API.

**Backend seguro, interface conveniente — nunca o contrário.** O atendente não vê o botão de gerenciar serviços porque a interface esconde o que ele não pode. Mas a permissão de verdade está no backend (`exigir_papel`, testado com atendente tentando criar/editar/remover serviço e recebendo 403) — esconder no front é conveniência, barrar no back é segurança.

## Testes

```bash
cd backend
pip install -r requirements.txt
pytest                                    # suite completa (SQLite, ~70 testes)
POSTGRES_TEST_URL=postgresql://... pytest tests/test_race_condition.py  # concorrência real
```

O teste dos dois tenants (`test_dois_tenants_um_nunca_alcanca_o_dado_do_outro_por_nenhuma_rota`) e o de conflito ponta a ponta (`test_conflito_de_horario_ponta_a_ponta`) exercitam o sistema só pela API — sem atalho direto no banco.

## Limitações e roadmap

O que ficou de fora do v1, deliberadamente — não como dívida, como mapa de até onde foi e por quê:

- **Paginação por cursor** — o v1 usa offset/limit com teto de 100; cursor é mais robusto em tabelas grandes.
- **Busca textual mais séria** — `ILIKE` resolve o v1; full-text search do Postgres (acentos, erros de digitação) é o passo natural.
- **Múltiplos profissionais com agendas separadas** — o agendamento não distingue profissional; a agenda é do negócio como um todo.
- **Convite/gestão de atendentes pela interface** — hoje só o dono é criado (via `/auth/registrar-negocio`); adicionar um atendente exige inserir direto no banco. A permissão de papel já existe e é testada (`Papel.ATENDENTE`), só falta a tela de convite.
- **Notificação ao cliente, recorrência, relatórios, autoatendimento** — cada um dobra a superfície do projeto sem provar um ponto novo dos cinco que o v1 existe para provar (isolamento, auth por papel, regra de negócio, modelagem, CRUD de produção).

## Documentação completa

Cada etapa de construção — visão e escopo, multi-tenancy, autenticação, modelagem, regra de negócio, CRUD de produção, entrega — está escrita em [`docs/documentacao.md`](docs/documentacao.md), com o porquê de cada decisão.
