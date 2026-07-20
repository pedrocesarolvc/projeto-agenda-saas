# Projeto Agenda — SaaS de Agendamento Multi-tenant

> **Documentação em construção, escrita por etapas.**
> Cada etapa corresponde a um pedaço construível do projeto.

| Etapa | Conteúdo | Status |
|---|---|---|
| **1** | Visão, domínio e escopo | ✅ escrita |
| **2** | Multi-tenancy — isolamento por tenant | ✅ escrita |
| 3 | Autenticação e permissões — JWT por tenant e perfis | ⬜ pendente |
| 4 | Modelagem — o desenho relacional | ⬜ pendente |
| 5 | Regra de negócio — conflito de horário e status | ⬜ pendente |
| 6 | CRUD de produção — paginação, filtro, busca, validação | ⬜ pendente |
| 7 | Entrega — API, interface, testes e Docker | ⬜ pendente |

---

# Etapa 1 — Visão, domínio e escopo

## 1.1 O que este projeto prova

Os outros dois projetos do portfólio provam que você faz o **difícil e o novo**: segurança e LGPD (SecureFlow), IA aplicada e infraestrutura de dados (RAG).

Este prova outra coisa, e é de propósito: que você faz o **comum, bem-feito**. Cadastro, login, permissões, uma agenda que não deixa marcar dois no mesmo horário, uma listagem que pagina e filtra. É o trabalho que a maioria das vagas realmente pede no dia a dia — e é justo o que um portfólio só de projetos impressionantes deixa em dúvida.

O objetivo deste projeto não é ser o mais chamativo dos três. É **remover o motivo de não te chamar**: a dúvida silenciosa de "será que ele entrega o feijão-com-arroz, ou só persegue o que é vistoso?".

## 1.2 O domínio: agendamento

Um SaaS onde pequenos negócios de serviço — barbearia, estúdio, oficina — gerenciam seus agendamentos.

O dono cadastra os serviços que oferece (corte, barba, coloração), define seus horários de atendimento, e registra os agendamentos dos clientes. Um atendente da mesma barbearia acessa a mesma agenda, com permissões menores. Cada negócio vê **apenas os seus próprios dados** — nunca os de outro negócio que usa o mesmo sistema.

Por que agendamento, e não um CRUD qualquer: porque agendamento tem **regra de negócio de verdade**. "Não pode marcar dois clientes no mesmo horário com o mesmo profissional" é uma regra que existiria em qualquer linguagem, em qualquer banco — é lógica de domínio pura, não detalhe técnico. É isso que separa um projeto de "cadastro de tarefas" (sem regra) de um projeto que demonstra pensar sobre um problema real.

## 1.3 Os dois conceitos que sustentam tudo

Este projeto gira em torno de duas ideias. Uma é nova para este portfólio; a outra o projeto herda de conhecimento que já existe.

**Multi-tenancy (a ideia central, Etapa 2).** Vários negócios ("tenants", inquilinos) usam a mesma aplicação e o mesmo banco, isolados uns dos outros. A Barbearia A jamais vê um agendamento da Barbearia B. Como garantir esse isolamento é a pergunta que define a arquitetura — e o ponto onde um CRUD comum vira, se malfeito, uma falha de segurança.

**Autenticação e permissões (Etapa 3).** Quem é você, de qual negócio você é, e o que você pode fazer. O login com JWT é território conhecido; o que este projeto acrescenta é **amarrar o token ao tenant** e distinguir perfis (dono vê tudo do seu negócio; atendente vê menos).

As duas se cruzam num ponto: a identidade não diz só "sou fulano", diz "sou fulano, da Barbearia A, no papel de dono". Isolamento e permissão andam juntos.

## 1.4 Escopo do v1

A seção mais importante, como nos outros projetos. Um projeto terminado vale mais que um ambicioso e abandonado. O v1 é deliberadamente enxuto: prova os cinco pontos que o mercado quer ver, e nada além.

### O que o v1 precisa provar

Estes cinco são a régua. Se o projeto os demonstra, cumpriu seu papel:

1. **Multi-tenancy** — isolamento real entre negócios
2. **Autenticação e autorização** — JWT amarrado ao tenant, e permissão por perfil
3. **Regra de negócio** — o agendamento com conflito de horário e transição de status
4. **Modelagem relacional sólida** — as entidades e seus relacionamentos no PostgreSQL
5. **CRUD de produção** — paginação, filtro, busca e validação, não só inserir e listar

### Entra no v1

| Item | Detalhe |
|---|---|
| Cadastro de negócio (tenant) | Criar uma conta de negócio, que vira um tenant isolado |
| Usuários por negócio | Dono e atendente, com permissões diferentes |
| Serviços | CRUD dos serviços oferecidos (nome, duração, preço) |
| Clientes | CRUD dos clientes do negócio |
| Agendamentos | Marcar, remarcar, cancelar — com a regra de conflito |
| Agenda | Listagem com filtro por dia, por profissional, por status |

### Fica no roadmap

| Item | Por que fica de fora |
|---|---|
| Pagamento / cobrança online | Domínio inteiro à parte; não demonstra multi-tenant nem regra de agenda |
| Notificação por e-mail/SMS ao cliente | Depende de serviço externo; é integração, não o núcleo |
| Múltiplos profissionais com agendas separadas | Enriquece a regra de conflito, mas complica a modelagem cedo demais |
| Relatórios e dashboard financeiro | Bom no v2; não é o que este projeto precisa provar |
| Autoatendimento (cliente marca sozinho) | Exige portal público separado; dobra a superfície |
| Recorrência (agendamento semanal fixo) | Regra de negócio avançada; o conflito simples já prova o ponto |

**Regra anti-crescimento, como nos outros projetos:** nada sai do roadmap e entra no v1 antes de todo o v1 estar funcionando.

## 1.5 Decisões de arquitetura

**Multi-tenancy por discriminador de coluna (`tenant_id`), não schema nem banco por tenant.**
Toda tabela do domínio carrega uma coluna `tenant_id`, e todo acesso filtra por ela. É a abordagem que a maioria dos SaaS reais usa, demonstra o conceito sem virar projeto de infraestrutura, e concentra a dificuldade num ponto claro (não esquecer o filtro) que é ótimo de discutir em entrevista. As alternativas — um schema ou um banco por tenant — resolvem isolamento com mais força, mas custam complexidade operacional que não acrescenta nada ao que este projeto quer provar. Detalhado na Etapa 2.

**Mesma stack dos outros dois projetos.**
Python, FastAPI, PostgreSQL, Pydantic, SQLModel/SQLAlchemy, pytest, Docker. Nenhuma tecnologia nova por tecnologia nova: o desafio aqui é *padrão bem-feito*, não ferramenta exótica. Reusar a stack também mostra consistência no portfólio — três projetos, uma base sólida, domínios diferentes.

**A regra de negócio mora numa camada de serviço, não na rota.**
A verificação de conflito de horário não pode viver dentro do handler HTTP. Ela fica numa camada de serviço, testável sem subir a API. É a fronteira borda/núcleo de novo: a rota traduz HTTP, o serviço decide as regras. Detalhado na Etapa 5.

**Permissão verificada no servidor, sempre.**
O frontend pode esconder um botão que o atendente não deve ver, mas a decisão real é sempre no backend. Esconder no front é conveniência; barrar no back é segurança. Detalhado na Etapa 3.

## 1.6 Estrutura de pastas

Diferente dos outros dois projetos do portfólio, aqui o frontend é protagonista, não vitrine. Na prática são duas aplicações convivendo — uma API e uma interface — e a raiz reflete isso, com `backend/` e `frontend/` separados. É o layout que o mercado espera de um SaaS e o que mantém o `docker-compose` limpo (Etapa 7).

```
projeto-agenda/
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI: sobe o app e registra as rotas
│   │   ├── config.py           # configuração via variável de ambiente
│   │   ├── database.py         # conexão e sessão do banco
│   │   ├── modelos/            # entidades (Etapa 4) — tenant, usuario, cliente, servico, agendamento
│   │   ├── schemas/            # schemas Pydantic (entrada/saída da API)
│   │   ├── auth/               # Etapa 3 — JWT, tenant no token, permissão por papel
│   │   ├── core/               # o coração do multi-tenancy
│   │   │   └── tenancy.py      # a camada central que injeta o filtro tenant_id (Etapa 2)
│   │   ├── servicos/           # Etapa 5 — regra de negócio (conflito de horário, status)
│   │   └── rotas/              # endpoints, um arquivo por recurso
│   ├── tests/
│   │   └── ...                 # inclui o teste dos dois tenants (Etapa 2)
│   ├── alembic/                # migrations do banco
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── componentes/        # UI reutilizável
│   │   ├── paginas/            # telas: login, agenda, clientes, serviços
│   │   ├── api/                # cliente HTTP que fala com o backend
│   │   └── hooks/              # estado e lógica de tela
│   ├── package.json
│   └── ...
│
├── docs/
│   └── documentacao.md         # esta documentação, por etapas
├── docker-compose.yml          # sobe backend + frontend + postgres (Etapa 7)
└── README.md
```

Duas pastas do backend merecem destaque, porque são onde moram as decisões desta e das próximas etapas:

**`core/tenancy.py`** — o ponto único por onde o filtro de `tenant_id` é injetado (a defesa de Nível 1 da Etapa 2). Isolar isso num arquivo próprio não é organização estética: é a arquitetura que torna "esquecer o filtro" difícil. Se o isolamento de tenant morasse espalhado pelas rotas, ele voltaria a depender da memória do programador.

**`servicos/`** — onde a regra de negócio vive, separada das rotas (a decisão de arquitetura da seção 1.5). A verificação de conflito de horário fica aqui, testável sem subir a API.

Como nos outros projetos, **pasta nasce quando o código nasce.** O esqueleto acima é o destino, não o ponto de partida: no ciclo de código da Etapa 2–3 existem `core/`, `auth/`, `modelos/` e `rotas/`; `servicos/` surge na Etapa 5. Não se criam pastas vazias à espera do futuro.

## 1.7 A conexão com o resto do portfólio

Não planejada, mas real e vale explorar em entrevista: o coração do multi-tenancy é **isolamento de dados — impedir que o dado de um vaze para outro.** É o mesmo tema do SecureFlow (impedir que dado sensível vaze para onde não deve), visto por outro ângulo.

Os três projetos, juntos, contam uma história consistente: **você trata vazamento de dados como um reflexo.** No SecureFlow, PII que não pode escapar. No RAG, a resposta que não pode inventar além da fonte. Aqui, o tenant que não pode ver o dado do outro. Três domínios, a mesma disciplina.

## 1.8 Glossário desta etapa

| Termo | O que é |
|---|---|
| **Tenant** | Um inquilino do sistema — aqui, um negócio (uma barbearia). Cada um isolado dos demais |
| **Multi-tenant** | Uma única aplicação e um único banco servindo vários tenants, sem que um veja o dado do outro |
| **`tenant_id`** | A coluna que marca a qual tenant cada linha pertence. A base do isolamento |
| **Autenticação** | Provar quem você é (login) |
| **Autorização / permissão** | Definir o que você pode fazer, uma vez identificado |
| **Perfil / papel** (*role*) | O nível de permissão de um usuário — aqui, dono ou atendente |
| **JWT** | O token que carrega a identidade do usuário entre requisições |
| **Camada de serviço** | Onde mora a regra de negócio, separada da rota HTTP |
| **CRUD** | *Create, Read, Update, Delete* — as operações básicas sobre uma entidade |

---

# Etapa 2 — Multi-tenancy

## 2.1 O que esta etapa resolve

Uma pergunta só: **como vários negócios usam o mesmo sistema sem nunca ver o dado um do outro?**

Toda a etapa é a resposta a isso. E a resposta tem uma parte fácil (o conceito, que você já pegou) e uma parte perigosa (garantir que o isolamento não vaze — a seção 2.5 em diante). É na parte perigosa que mora o valor desta etapa para o seu portfólio.

## 2.2 O prédio de apartamentos

A imagem que fixa o conceito: o sistema é um **prédio**. Cada negócio é um **apartamento**. Todos compartilham o mesmo endereço, a mesma estrutura, o mesmo encanamento — mas a chave de um apartamento não abre a porta do outro.

- O **prédio** é a sua aplicação e o seu banco de dados. Um só, para todos.
- Cada **apartamento** é um tenant — uma barbearia.
- A **chave** é o que amarra cada usuário ao seu tenant (Etapa 3).

O que multi-tenancy **não** é: um sistema separado para cada cliente. Isso seria construir um prédio inteiro para cada morador — cada barbearia com sua própria aplicação, seu próprio servidor. Caro, impossível de manter, e some a economia de escala que faz um SaaS ser um SaaS. Multi-tenant é o oposto: **uma estrutura, muitos inquilinos.**

## 2.3 As três estratégias de isolamento

Há três formas de separar os apartamentos, do mais separado ao mais compartilhado:

| Estratégia | O isolamento | Analogia |
|---|---|---|
| **Banco por tenant** | Cada tenant tem seu próprio banco de dados | Cada morador num prédio diferente |
| **Schema por tenant** | Um banco, mas cada tenant tem seu schema | Mesmo prédio, andares privativos |
| **Discriminador de coluna** | Um banco, tabelas compartilhadas, uma coluna `tenant_id` marca o dono de cada linha | Mesmo andar, apartamentos numerados |

Elas trocam **isolamento** por **simplicidade**. Banco por tenant é o mais isolado e o mais caro de operar (migrar 500 bancos a cada mudança de schema). Discriminador de coluna é o mais simples e o que exige mais disciplina para não vazar.

## 2.4 A escolha: `tenant_id` em toda tabela

**Decisão do v1: discriminador de coluna.** Toda tabela do domínio — clientes, serviços, agendamentos — ganha uma coluna `tenant_id`. Cada linha sabe a que negócio pertence.

```
agendamentos
├── id
├── tenant_id   ←  a coluna que marca o dono
├── cliente_id
├── servico_id
├── inicio
├── fim
└── status
```

Três razões:

1. **É o que a maioria dos SaaS reais usa.** Demonstrar essa estratégia é demonstrar o padrão de mercado, não um exercício acadêmico.
2. **Concentra a dificuldade num ponto discutível.** O risco é um só e é nomeável (a seção 2.5), o que rende uma ótima conversa de entrevista.
3. **Não vira projeto de infraestrutura.** Schema ou banco por tenant arrastam complexidade operacional (migrations múltiplas, conexões dinâmicas) que não acrescenta nada ao que este projeto quer provar.

O custo dessa escolha é exatamente o que vem a seguir — e é o motivo de esta etapa existir como ponto de desaceleração.

## 2.5 A armadilha: o isolamento depende de você lembrar

Aqui está o coração da etapa. Leia devagar.

Com `tenant_id`, o isolamento **não é automático.** O banco não impede, sozinho, que a Barbearia A leia a linha da Barbearia B. O que impede é o **filtro que você escreve em toda query:**

```sql
SELECT * FROM agendamentos WHERE tenant_id = :meu_tenant AND ...
```

Esse `WHERE tenant_id = ...` é a parede entre os apartamentos. E a parede só existe onde você a constrói. **Esquecer o filtro em uma única query derruba a parede naquele ponto** — e o dado de um tenant aparece para outro.

O perigo não é teórico, e não é um bug comum. É uma **falha de segurança**: vazamento de dados entre clientes, o pior defeito que um SaaS pode ter. E ele é traiçoeiro porque:

- **Não estoura.** A query funciona, retorna dados, a tela preenche. Nada quebra. Só que retorna dados demais.
- **Passa em testes ingênuos.** Se você testa com um tenant só, nunca vê o vazamento — porque não há um segundo tenant cujo dado apareça.
- **Some no meio de dezenas de queries certas.** Vinte e nove queries filtram direito; a trigésima esquece. É a trigésima que vaza.

O `GET /agendamentos/{id}` é o caso clássico. Buscar por id parece seguro — o id é único, certo? Mas `SELECT * FROM agendamentos WHERE id = :id` **sem** o `AND tenant_id = :meu_tenant` deixa a Barbearia A ler o agendamento da B só sabendo (ou adivinhando) o id. O filtro por id não substitui o filtro por tenant. Os dois andam sempre juntos.

## 2.6 A defesa: não confiar na memória do programador

A lição que separa o projeto de estudante do projeto de engenheiro: **se o isolamento depende de lembrar, ele vai falhar** — porque uma hora alguém esquece. A solução profissional não é "prometer lembrar sempre". É tornar o filtro **difícil de esquecer**, ou impossível.

Há uma escada de defesas, da mais frágil à mais robusta:

**Nível 0 — filtrar à mão em cada query.** O que descrevemos. Funciona, mas depende 100% da disciplina humana. É onde não se quer parar.

**Nível 1 — centralizar o acesso ao dado.** Nenhuma rota fala com o banco direto. Todo acesso passa por uma camada (um repositório, uma função de consulta) que recebe o tenant atual e injeta o filtro. Você escreve o `WHERE tenant_id` num lugar só, e todas as queries herdam. Esquecer fica muito mais difícil, porque não há query solta espalhada pelo código.

**Nível 2 — o banco impõe, não confia.** O PostgreSQL tem **Row-Level Security (RLS)**: você declara uma política no banco dizendo "nesta tabela, só se enxerga linhas do tenant atual", e o banco **recusa** devolver as outras — mesmo que a query esqueça o filtro. A parede deixa de depender do código e passa a ser estrutural.

**Decisão do v1:** Nível 1 obrigatório (uma camada central que injeta o `tenant_id`), com RLS mencionado como reforço no roadmap. Centralizar já elimina a esmagadora maioria do risco e é simples. RLS é a defesa mais forte, mas tem custo de configuração e complexidade de depuração que, para o v1, é melhor declarar do que implementar às pressas.

O ponto que vale para a entrevista: **saber que RLS existe, e que a defesa correta é não depender da memória do programador, vale mais do que qualquer código.** É a diferença entre "eu filtro sempre" (frágil) e "eu projetei o sistema para que esquecer não seja possível" (engenharia).

## 2.7 De onde vem o "meu_tenant"

Uma pergunta natural: esse `:meu_tenant` do filtro — de onde ele sai a cada requisição?

Ele vem da identidade do usuário logado, e é o elo com a Etapa 3. Quando o usuário faz login, o tenant dele fica gravado no token. Cada requisição carrega o token; o backend extrai o `tenant_id` dele e usa no filtro.

O ponto crítico, que a Etapa 3 vai aprofundar: **o tenant vem sempre do token, nunca do que o cliente manda no corpo ou na URL.** Se o frontend enviasse "quero os agendamentos do tenant 5", bastaria trocar o número para ler o dado alheio. O tenant é decidido pelo servidor, a partir de quem está autenticado — não é um parâmetro que o cliente escolhe. Guardar isso agora evita a falha de segurança mais comum de sistema multi-tenant.

## 2.8 O que muda na modelagem

Consequência direta desta etapa, que a Etapa 4 (modelagem) vai detalhar: **o `tenant_id` não é uma coluna a mais numa tabela. É uma coluna em quase todas.**

Clientes, serviços, agendamentos, usuários — tudo que pertence a um negócio carrega o `tenant_id`. As únicas tabelas sem ele são as que existem *acima* dos tenants: a própria tabela de tenants (o cadastro dos negócios), e eventual configuração global do sistema.

Uma boa pergunta de teste para qualquer tabela nova: *"esse dado pertence a um negócio específico ou ao sistema inteiro?"*. Pertence a um negócio → tem `tenant_id`. É do sistema → não tem.

## 2.9 Como testar

E aqui está o teste que **prova** o isolamento — e que a maioria dos projetos esquece de escrever, justamente o que torna o vazamento invisível:

**O teste dos dois tenants.** Crie dois negócios, A e B. Cadastre um agendamento em cada. Autenticado como A, tente ler, listar, editar e apagar o agendamento de B — e verifique que **todas** falham (retornam vazio ou negam acesso). Esse teste, e só ele, prova que a parede existe.

Casos a cobrir:

- Listar agendamentos como A não traz nenhum de B
- `GET /agendamentos/{id}` de B, autenticado como A → negado (o caso clássico da 2.5)
- Editar/cancelar recurso de B como A → negado
- Um tenant recém-criado enxerga zero dados de outros
- Buscar/filtrar como A nunca faz aparecer linha de B, em nenhuma combinação de filtro

O segundo caso é o mais valioso da suíte inteira: ele afirma, em código, que o `GET` por id respeita o tenant. É o teste que um vazamento faria falhar — e tê-lo é a prova de que você conhece o risco e o fechou.

Teste com **dois** tenants, sempre. Um teste com um tenant só é cego para exatamente o defeito que esta etapa existe para evitar.

## 2.10 Glossário desta etapa

| Termo | O que é |
|---|---|
| **Isolamento de tenant** | A garantia de que um tenant nunca acessa o dado de outro |
| **Discriminador de coluna** | Estratégia multi-tenant em que uma coluna `tenant_id` marca o dono de cada linha |
| **Shared database** | Um único banco servindo todos os tenants (o caso deste projeto) |
| **Row-Level Security (RLS)** | Recurso do PostgreSQL que faz o banco impor o filtro de tenant, sem depender do código |
| **Camada de acesso a dados** | O ponto único por onde todas as queries passam, onde o filtro de tenant é injetado |
| **Vazamento entre tenants** | A falha de segurança em que o dado de um tenant aparece para outro |
| **Tenant a partir do token** | O princípio de que o tenant vem sempre da identidade autenticada, nunca de input do cliente |

---

## Próxima etapa

**Etapa 3 — Autenticação e permissões:** o JWT que você já conhece, agora amarrado ao tenant, e a segunda camada da autorização — o papel (dono vs. atendente).
