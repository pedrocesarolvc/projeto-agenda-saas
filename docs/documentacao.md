# Projeto Agenda — SaaS de Agendamento Multi-tenant

> **Documentação em construção, escrita por etapas.**
> Cada etapa corresponde a um pedaço construível do projeto.

| Etapa | Conteúdo | Status |
|---|---|---|
| **1** | Visão, domínio e escopo | ✅ escrita |
| **2** | Multi-tenancy — isolamento por tenant | ✅ escrita |
| **3** | Autenticação e permissões — JWT por tenant e perfis | ✅ escrita |
| **4** | Modelagem — o desenho relacional | ✅ escrita |
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

# Etapa 3 — Autenticação e permissões

## 3.1 O que esta etapa faz, e o que ela reaproveita

Esta etapa responde três perguntas sobre cada requisição que chega:

1. **Quem é você?** — autenticação (o login)
2. **De qual negócio você é?** — o tenant, primeira camada da autorização
3. **O que você pode fazer?** — o papel, segunda camada da autorização

A pergunta 1 é território que você já domina: JWT, hash de senha, login. Esta etapa não vai reexplicar isso — vai tratá-lo como base pronta e construir por cima. O que é novo, e o que importa aqui, são as perguntas 2 e 3: como o tenant entra no token, e como o papel recorta o que cada usuário faz.

A distinção que sustenta tudo, e que ficou firme na Etapa 1: autenticação é **quem você é**; autorização é **o que você pode**. São duas verificações separadas, nesta ordem — primeiro o sistema sabe quem você é, depois decide o que liberar.

## 3.2 A autenticação, em uma seção (porque você já sabe)

O fluxo padrão, só para fixar o contrato com o resto do projeto:

- No cadastro, a senha é guardada como **hash** (bcrypt ou argon2), nunca em texto puro.
- No login, o backend confere a senha contra o hash e, se bate, emite um **JWT**.
- Cada requisição seguinte manda o token; o backend valida a assinatura e confia no conteúdo.

Nada disso é específico deste projeto — é o mesmo login de qualquer aplicação. O que torna este login multi-tenant é **o que vai dentro do token**, e é aí que a etapa começa de verdade.

## 3.3 O tenant mora no token

Lembra do `:meu_tenant` que a Etapa 2 deixou pendente na seção 2.7 — a origem do valor que alimenta o filtro de isolamento? É aqui.

Quando o usuário faz login, o backend sabe a qual tenant ele pertence (está gravado no cadastro dele). Esse `tenant_id` entra no JWT, junto da identidade:

```
JWT (payload)
├── sub: id do usuário       ← quem é você
├── tenant_id: id do negócio ← de qual negócio você é
├── role: "dono"             ← seu papel (seção 3.5)
└── exp: validade
```

A partir daí, toda requisição carrega, no token, o tenant do usuário. O backend extrai o `tenant_id` do token e o usa no filtro de toda query. O elo que faltava na Etapa 2 está fechado: o filtro `WHERE tenant_id = :meu_tenant` recebe seu valor daqui.

## 3.4 O princípio que evita a falha mais comum de SaaS

Este é o ponto mais importante da etapa, e é curto: **o tenant vem sempre do token, nunca do que o cliente envia.**

Imagine que, em vez de tirar o tenant do token, o backend aceitasse o tenant que o frontend manda — na URL (`/agendamentos?tenant=5`) ou no corpo. Aí bastaria o usuário da Barbearia A trocar o número para `tenant=7` e ler os dados da Barbearia B. O isolamento inteiro da Etapa 2 cairia por uma linha de input.

A regra é absoluta:

> O cliente diz **quem** quer autenticar (login e senha). O servidor decide **qual tenant é esse** (a partir do cadastro, gravado no token). O cliente nunca escolhe seu próprio tenant.

Todo dado que decide permissão — tenant e papel — vem do token, que o servidor assinou e o cliente não pode forjar. Nada que venha do corpo ou da URL da requisição pode influenciar isolamento ou permissão. Esse é o tipo de princípio que, dito numa entrevista, mostra que você entende segurança de aplicação, não só sintaxe.

## 3.5 A segunda camada: papel (dono vs. atendente)

O tenant recortou quais dados você alcança. O **papel** recorta o que você faz com eles. É a autorização de segundo nível, e ela opera *dentro* do tenant.

Dois papéis no v1:

| Ação | Dono | Atendente |
|---|---|---|
| Ver a agenda | ✅ | ✅ |
| Marcar / remarcar / cancelar agendamento | ✅ | ✅ |
| Cadastrar e editar clientes | ✅ | ✅ |
| Criar / editar / remover serviços e preços | ✅ | ❌ |
| Gerenciar usuários do negócio | ✅ | ❌ |
| Ver relatórios do negócio | ✅ | ❌ |

O atendente toca o dia a dia (agenda e clientes); o dono controla a configuração do negócio (serviços, preços, equipe). A linha divisória é "operar" versus "configurar".

As duas camadas juntas, na ordem em que agem:

```
requisição chega
      │
      ▼
1. autenticada?      → o token é válido?           (senão: 401)
      │
      ▼
2. filtro de tenant  → só vê dados do próprio tenant (Etapa 2)
      │
      ▼
3. papel permite?    → esse papel pode esta ação?   (senão: 403)
      │
      ▼
   executa
```

Repare que o atendente da Barbearia A **não** é barrado de ver a agenda da B pelo passo 3 — ele é barrado no passo 2, porque aquele dado nem entra no universo dele. O papel só entra em cena depois que o tenant já filtrou. Primeiro o universo, depois o que se faz nele — exatamente a estrutura de duas camadas descrita na Etapa 1.

## 3.6 401 e 403: não são a mesma recusa

Uma distinção pequena que denota cuidado:

- **401 (Unauthorized)** — "não sei quem você é". Token ausente, inválido ou expirado. Falha de **autenticação**.
- **403 (Forbidden)** — "sei quem você é, mas você não pode isto". O atendente tentando criar um serviço. Falha de **autorização**.

Trocar um pelo outro é erro comum e confunde quem consome a API. 401 diz "faça login"; 403 diz "login não adianta, você não tem permissão". A distinção espelha exatamente autenticação vs. autorização — o tema da etapa inteira, agora nos códigos de status.

## 3.7 A permissão é decidida no servidor, sempre

A decisão de arquitetura que a Etapa 1 antecipou (seção 1.5), agora no lugar certo.

O frontend vai esconder o botão "criar serviço" do atendente — é boa experiência, ele não vê o que não pode usar. Mas esconder o botão **não é** a segurança. Um atendente que conheça a rota pode chamá-la direto, sem passar pela tela. Se o backend não verificar o papel, a chamada passa.

Portanto:

> Esconder no frontend é conveniência. Barrar no backend é segurança. As duas coexistem, mas só a segunda protege.

Toda ação restrita é verificada no servidor, na entrada da rota, independentemente do que o frontend mostrou ou escondeu. O frontend nunca é a fronteira de segurança — ele é a camada de conforto sobre uma fronteira que mora no backend.

## 3.8 Onde isso vive no código

Da estrutura de pastas da Etapa 1, esta etapa preenche `backend/app/auth/`:

- emissão e validação do JWT
- extração de `sub`, `tenant_id` e `role` do token a cada requisição
- uma dependência do FastAPI que entrega "o usuário atual" (com tenant e papel) para as rotas
- uma verificação de papel reutilizável, para marcar rotas que exigem "dono"

O ponto de design: o `tenant_id` extraído aqui é o mesmo que a `core/tenancy.py` (Etapa 2) injeta no filtro. Autenticação e isolamento se encontram neste valor — o token o fornece, a camada de tenancy o consome. Duas etapas, um dado, um fluxo.

## 3.9 Como testar

Autenticação e permissão são determinísticas — e, como no isolamento da Etapa 2, o teste que importa é o que tenta furar a regra:

- Login com senha certa emite token; com senha errada, nega
- Requisição sem token → 401
- Requisição com token expirado ou adulterado → 401
- Atendente tentando criar um serviço → 403
- Dono criando um serviço → sucesso
- O teste que junta as duas camadas: um usuário tentando passar um `tenant_id` no corpo ou na URL diferente do seu token → o valor do corpo é ignorado, o do token prevalece. Prova que o tenant não é forjável pelo cliente.
- Dono da Barbearia A não consegue gerenciar usuários da B (as duas camadas agindo: tenant barra antes, papel barraria depois)

O penúltimo é o mais valioso: ele prova, em código, o princípio da seção 3.4 — o tenant vem do token, não do cliente. É o teste que fecha o vazamento mais comum de sistema multi-tenant.

## 3.10 Glossário desta etapa

| Termo | O que é |
|---|---|
| **Autenticação** | Provar quem você é. Resulta no token |
| **Autorização** | Decidir o que você pode. Tem duas camadas aqui: tenant e papel |
| **Hash de senha** | A senha guardada de forma irreversível (bcrypt, argon2), nunca em texto puro |
| **Claim** | Um campo dentro do JWT (`sub`, `tenant_id`, `role`, `exp`) |
| **Papel / role** | O nível de permissão do usuário dentro do tenant — dono ou atendente |
| **401 Unauthorized** | "Não sei quem você é" — falha de autenticação |
| **403 Forbidden** | "Sei quem você é, mas não pode" — falha de autorização |
| **Dependência (FastAPI)** | Função que o framework injeta na rota — aqui, "o usuário atual" com tenant e papel |
| **Tenant a partir do token** | O princípio de que tenant e papel vêm do token assinado, nunca de input do cliente |

---

# Etapa 4 — Modelagem

## 4.1 O que esta etapa faz

Desenhar as tabelas: quais entidades existem, o que cada uma guarda, e como elas se ligam.

Terreno familiar — é modelagem relacional, que você já conhece. Por isso esta etapa é mais leve nas explicações e mais densa nas decisões. Duas coisas a carregam de peso, e são as que valem atenção: onde o `tenant_id` entra (consequência da Etapa 2) e o que a estrutura precisa oferecer para a regra de conflito da Etapa 5 funcionar. O resto é desenho.

## 4.2 As cinco entidades

O domínio de agendamento se resolve com cinco tabelas:

| Entidade | O que representa | Tem `tenant_id`? |
|---|---|---|
| `tenant` | O negócio (a barbearia). A raiz do isolamento | Não — ela é o tenant |
| `usuario` | Quem opera o sistema: dono ou atendente | Sim |
| `cliente` | Quem recebe o serviço (o freguês da barbearia) | Sim |
| `servico` | O que o negócio oferece: nome, duração, preço | Sim |
| `agendamento` | Um horário marcado: liga cliente, serviço e tempo | Sim |

A pergunta que decide o `tenant_id`, da Etapa 2: *"esse dado pertence a um negócio específico ou ao sistema inteiro?"*. A tabela `tenant` é a única que não pertence a um negócio — ela lista os negócios. Todas as outras pertencem a um, e carregam a coluna.

Note a diferença entre `usuario` e `cliente`, que confunde no começo: o **usuário** opera o sistema (faz login, marca horários); o **cliente** é atendido (não tem login, é um registro na agenda). O barbeiro é usuário; o freguês é cliente. Dois conceitos, duas tabelas.

## 4.3 Os relacionamentos

```
        tenant  (o negócio)
          │
          │ 1 : N          um negócio tem vários de cada
    ┌─────┼─────────┬──────────────┐
    ▼     ▼         ▼              ▼
 usuario cliente  servico      agendamento
                                 │  │  │
              ┌──────────────────┘  │  └──────────────┐
              ▼                     ▼                  ▼
          cliente               servico            (tenant)
       quem será atendido    o que será feito    dono da linha
```

Em palavras:

- Um tenant tem muitos usuários, clientes, serviços e agendamentos. (1:N em tudo)
- Um agendamento pertence a um cliente e a um serviço — é a tabela que amarra as pontas.
- Todo agendamento, cliente, serviço e usuário aponta de volta para o seu tenant.

O agendamento é a entidade central do domínio: é onde cliente, serviço e tempo se encontram, e é sobre ela que a regra de negócio da Etapa 5 vai operar.

## 4.4 A tabela de agendamento, em detalhe

Porque é a que a Etapa 5 vai usar, vale desenhá-la inteira:

```sql
CREATE TABLE agendamento (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   BIGINT NOT NULL REFERENCES tenant(id),
    cliente_id  BIGINT NOT NULL REFERENCES cliente(id),
    servico_id  BIGINT NOT NULL REFERENCES servico(id),
    inicio      TIMESTAMPTZ NOT NULL,
    fim         TIMESTAMPTZ NOT NULL,
    status      TEXT NOT NULL DEFAULT 'marcado',
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Três decisões embutidas aqui, cada uma com um porquê:

**`inicio` e `fim`, não `inicio` + `duração`.** Guardar os dois extremos do intervalo torna a detecção de conflito (Etapa 5) uma comparação direta entre intervalos. Se guardasse só o início e a duração, toda checagem de sobreposição teria que recalcular o fim — trabalho repetido e fonte de erro. A duração vem do `servico`; o fim é calculado uma vez, na criação, e gravado.

**`TIMESTAMPTZ`, não `TIMESTAMP`.** O TZ é fuso horário. Agendamento é sobre tempo, e tempo sem fuso é ambíguo — "14h" em qual referência? Guardar com fuso evita a classe inteira de bugs de horário que aparece quando o servidor está num fuso e o usuário em outro. Num projeto brasileiro isso pode parecer over-engineering, mas é o padrão correto e custa nada adotar desde o início.

**`status` como texto com um default.** O ciclo de vida do agendamento (marcado → concluído, ou → cancelado) é a segunda regra da Etapa 5. A coluna nasce aqui; as transições válidas são lógica de negócio, não de banco.

## 4.5 O tenant_id e a integridade

Uma sutileza que separa modelagem ingênua de modelagem correta, e que conecta direto com a Etapa 2.

Todo agendamento tem um `tenant_id`, um `cliente_id` e um `servico_id`. A pergunta que quase ninguém faz: o cliente e o serviço apontados são do **mesmo tenant** do agendamento?

Nada no desenho básico impede um agendamento do tenant A apontar para um cliente do tenant B. As chaves estrangeiras garantem que o cliente *existe* — não que ele pertence ao tenant certo. Se a aplicação não cuidar disso, você teria um vazamento de tenant escondido dentro de uma referência, o mesmo risco da Etapa 2 por outra porta.

A defesa, no v1: quando a aplicação cria um agendamento, ela valida — na camada de serviço — que `cliente_id` e `servico_id` pertencem ao `tenant_id` do usuário logado. É a mesma disciplina da Etapa 2 (o tenant vem do token, e tudo é conferido contra ele), agora aplicada às referências entre tabelas. Vale mencionar no README como cuidado consciente; é o tipo de detalhe que um avaliador atento procura.

## 4.6 Índices que importam

Modelar não é só criar tabelas — é prever como serão consultadas. Dois índices ganham destaque:

**`tenant_id` em toda tabela do domínio.** Como toda query filtra por tenant (Etapa 2), a coluna `tenant_id` é a mais consultada do banco. Sem índice nela, cada consulta varre a tabela inteira. Um índice em `tenant_id` (muitas vezes composto, como `(tenant_id, inicio)` no agendamento) é o que mantém o sistema rápido conforme cresce.

**`(tenant_id, inicio, fim)` no agendamento.** A busca de conflito da Etapa 5 pergunta "existe agendamento neste tenant que se sobreponha a este intervalo?". Um índice sobre tenant e tempo torna essa pergunta rápida. A modelagem, aqui, já está preparando o terreno da próxima etapa.

Não é preciso encher o banco de índices no v1 — mas esses dois refletem os dois padrões de acesso que definem o sistema (filtrar por tenant, buscar por tempo), e mencioná-los mostra que você modela pensando em consulta, não só em armazenamento.

## 4.7 SQLModel e as migrations

Da estrutura da Etapa 1, esta etapa preenche `backend/app/modelos/`.

**SQLModel** (ou SQLAlchemy) descreve essas tabelas como classes Python, e é a mesma escolha dos outros dois projetos — consistência de stack. Cada entidade vira uma classe; os relacionamentos viram referências entre elas.

**Alembic** cuida das migrations — o versionamento do schema. Cada mudança na estrutura (uma coluna nova, uma tabela nova) vira um arquivo de migration versionado, que pode ser aplicado e revertido. Num projeto que evolui por etapas, isso importa: quando a Etapa 5 ou o roadmap pedirem uma coluna nova, a migration registra a mudança sem recriar o banco do zero. Mencionar migrations no README sinaliza que você pensa no ciclo de vida do schema, não só no seu estado atual.

## 4.8 Como testar

Modelagem se testa de forma mais indireta que as etapas anteriores — o que se verifica é que a estrutura sustenta as operações e a integridade:

- Criar uma entidade de cada e recuperá-la devolve os mesmos dados
- Um agendamento liga corretamente a seu cliente e serviço
- A restrição de chave estrangeira barra um `cliente_id` inexistente
- Um agendamento não aceita `cliente_id` de outro tenant (a validação da 4.5)
- `inicio` e `fim` sobrevivem ao round-trip com o fuso correto (a decisão `TIMESTAMPTZ` da 4.4)
- A migration aplica e reverte sem erro num banco limpo

O quarto teste é o mais valioso — ele prova que a integridade entre tenants, o risco da seção 4.5, está fechada. É o parente, na camada de dados, do teste dos dois tenants da Etapa 2.

## 4.9 Glossário desta etapa

| Termo | O que é |
|---|---|
| **Entidade** | Uma "coisa" do domínio que vira uma tabela (tenant, cliente, agendamento...) |
| **Relacionamento 1:N** | Um registro de um lado liga-se a vários do outro (um tenant, muitos clientes) |
| **Chave estrangeira (FK)** | Coluna que referencia o id de outra tabela, garantindo que o alvo existe |
| **TIMESTAMPTZ** | Timestamp com fuso horário. O tipo correto para tempo, evita ambiguidade |
| **usuario vs. cliente** | Usuário opera o sistema (tem login); cliente é atendido (é um registro) |
| **Integridade entre tenants** | Garantir que as referências de um agendamento pertencem ao mesmo tenant |
| **SQLModel** | Biblioteca que descreve tabelas como classes Python |
| **Migration** | Arquivo versionado que registra uma mudança de schema (via Alembic) |
| **Índice composto** | Índice sobre mais de uma coluna (ex.: `tenant_id, inicio`), para consultas frequentes |

---

## Próxima etapa

**Etapa 5 — Regra de negócio:** o conflito de horário (a checagem de sobreposição que a modelagem já preparou com o índice composto) e a transição de status do agendamento.
