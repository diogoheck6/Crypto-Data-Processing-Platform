# Projeto 1 — Crypto Data Processing Platform

## Visão geral

Este projeto será o **projeto principal do portfólio** para posicionamento em vagas de:

- **Python Backend**
- **Data Engineering / Data Platform**
- **Financial Systems**
- **Cloud / APIs / Processing Pipelines**

A proposta é construir uma plataforma de processamento de transações financeiras com foco em cripto, simulando um cenário real de mercado:

- ingestão de dados via CSV e API
- normalização e validação
- aplicação de regras complexas de negócio
- cálculo de cost basis e lucro/prejuízo
- processamento assíncrono para cargas maiores
- persistência e rastreabilidade
- API backend pronta para consumo
- possibilidade de frontend web
- deploy em cloud

A ideia não é fazer um projeto “bonitinho”.  
A ideia é fazer um projeto que **pareça e funcione como produto de engenharia real**.

---

## Objetivo estratégico

Construir uma plataforma que demonstre, ao mesmo tempo:

### Para vagas internacionais de Data Platform / Python

- processamento de grandes volumes de dados
- regras financeiras complexas
- pipelines de ingestão e transformação
- confiabilidade dos dados
- arquitetura limpa e sustentável
- deploy e operação em cloud

### Para vagas de Backend / IA / Integração

- APIs REST bem desenhadas
- arquitetura de backend moderna
- processamento assíncrono
- integração com fonte externa real
- observabilidade e qualidade de código
- possibilidade de consumo por serviços de IA ou analytics

---

## Nome do projeto

**Crypto Data Processing Platform**

Subtítulo sugerido para portfólio:

> Plataforma de processamento de transações financeiras com ingestão real, regras de negócio complexas, API backend e deploy em cloud.

---

## Problema que o projeto resolve

Sistemas financeiros que trabalham com cripto, investimento, contabilidade ou reconciliação precisam processar dados com características como:

- alto volume
- múltiplas fontes
- formatos inconsistentes
- regras específicas de negócio
- necessidade de auditoria
- necessidade de confiabilidade para análise

No caso de cripto, por exemplo, o sistema precisa interpretar eventos como:

- buy
- sell
- transfer
- fee
- deposit
- withdrawal
- conversões entre ativos

E transformar isso em algo útil:

- posição consolidada
- custo médio ou FIFO
- lucro / prejuízo
- base de cálculo
- relatórios confiáveis

---

## Problema real de negócio

Exemplo simples:

- usuário comprou BTC por 10 USD
- depois vendeu por 120 USD
- sistema precisa calcular:
  - custo de aquisição
  - lucro realizado
  - posição remanescente
  - possíveis inconsistências

Em cenário real, isso acontece com:

- milhares de transações
- múltiplos ativos
- taxas
- horários diferentes
- importações repetidas
- dados incompletos

Ou seja: o projeto simula **um motor de processamento financeiro orientado a dados**, não apenas um CRUD.

---

## Escopo funcional

### 1. Ingestão de dados

O sistema deve aceitar:

- upload de CSV manual
- CSV exportado da Binance
- integração com API da Binance (fase posterior)
- JSON para testes via API

### 2. Normalização

Transformar diferentes formatos em um modelo canônico interno.

Exemplo de modelo interno:

- user_id
- source
- transaction_id
- asset
- operation_type
- quantity
- unit_price
- total_value
- fee
- fee_asset
- occurred_at
- raw_payload

### 3. Validação

Regras de integridade:

- campos obrigatórios
- tipos válidos
- valores positivos
- datas válidas
- operação suportada
- duplicidade de transação
- consistência entre quantidade, preço e total

### 4. Regras de negócio

Implementar o coração do sistema:

- cost basis por FIFO
- custo médio ponderado (como evolução)
- lucro / prejuízo realizado
- posição por ativo
- tratamento de taxas
- tratamento de transferências
- separação entre eventos que afetam ou não a base de cálculo

### 5. Processamento

Executar o cálculo em:

- modo síncrono para cargas pequenas
- modo assíncrono para cargas maiores
- por lote
- com rastreamento de status

### 6. Persistência

Armazenar:

- transações normalizadas
- jobs de importação
- erros de validação
- resultados de processamento
- snapshots de posição
- relatórios gerados

### 7. Exposição via API

Disponibilizar dados por endpoints REST.

### 8. Relatórios

Gerar saídas úteis:

- resumo por ativo
- lucro / prejuízo
- inconsistências
- export CSV/JSON

### 9. Frontend (opcional, mas recomendado)

Interface simples para:

- upload de arquivos
- acompanhamento de jobs
- visualização de resultados
- dashboard operacional

---

## Arquitetura recomendada

## Escolha principal

A melhor opção para esse projeto é:

**Arquitetura limpa com inspiração hexagonal**

Motivo:

- conversa com teu posicionamento profissional
- organiza regras de negócio no centro
- separa domínio de infraestrutura
- facilita testes
- parece arquitetura real de produto
- é forte em entrevista

### Interpretação prática

Não precisa cair em academicismo.  
A ideia é usar o melhor dos dois mundos:

- **Clean Architecture** para separar camadas
- **Hexagonal** para isolar portas e adaptadores

---

## Estrutura conceitual da arquitetura

### Núcleo do domínio

Contém:

- entidades
- value objects
- regras de negócio
- serviços de domínio
- contratos abstratos

### Aplicação / casos de uso

Contém:

- importação de transações
- validação e normalização
- cálculo de cost basis
- geração de relatórios
- consulta de resultados

### Adaptadores de entrada

Contém:

- API FastAPI
- CLI administrativa
- jobs em fila

### Adaptadores de saída

Contém:

- repositórios PostgreSQL
- cliente Binance API
- storage de arquivos
- cache / fila Redis

---

## Stack recomendada

### Backend principal

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery ou RQ ou Dramatiq
- Pytest
- Docker

### Observabilidade e qualidade

- structlog ou logging estruturado
- pre-commit
- Ruff
- Black
- Mypy
- pytest-cov

### Cloud / deploy

- Azure Container Apps ou Azure App Service
- Azure Database for PostgreSQL
- Azure Blob Storage
- Azure Cache for Redis
- GitHub Actions

### Frontend (recomendado)

- Next.js
- TypeScript
- Tailwind CSS
- React Query ou fetch server actions, dependendo do estilo

---

## FastAPI ou Flask?

**FastAPI** é a escolha certa.

Porque:

- combina mais com mercado atual
- melhor documentação automática
- tipagem forte com Pydantic
- ótima experiência para APIs modernas
- conversa melhor com vagas como IPM

---

## Precisa de fila?

**Sim, faz sentido incluir fila.**

Mas de forma estratégica.

### Quando fila é realmente útil

- upload de arquivos grandes
- importações longas
- processamento por lote
- geração de relatórios
- reprocessamento de transações

### O que isso demonstra

- pensamento de produção
- desacoplamento entre requisição e processamento
- backend preparado para escalar
- entendimento real de operação

### Como aplicar sem complicar cedo demais

Fase 1:

- processamento síncrono

Fase 2:

- fila para jobs pesados

### Opções

- **RQ**: mais simples
- **Celery**: mais tradicional e robusto
- **Dramatiq**: elegante e moderna

### Recomendação

Se o objetivo é impacto com equilíbrio:

**Redis + RQ** no começo

Se quiser algo mais “enterprise-looking” depois:

**Celery + Redis**

---

## Banco de dados

### Principal

**PostgreSQL**

Porque:

- é padrão forte de mercado
- fica ótimo em portfólio
- suporta bem estrutura transacional
- combina com dados financeiros

### Redis

Usar para:

- fila
- cache de consultas
- controle de jobs
- rate limiting, se quiser evoluir

---

## Azure vale a pena?

**Sim. Muito.**

Especialmente para te posicionar melhor em vagas que citam cloud.

### O que usar na Azure

#### Opção mais simples e realista

- Azure App Service ou Azure Container Apps para API
- Azure Database for PostgreSQL
- Azure Blob Storage para arquivos

#### Evolução

- Azure Cache for Redis
- Azure Key Vault para secrets
- Azure Monitor / Application Insights

### Estratégia inteligente

Você pode fazer assim:

#### Etapa inicial

- rodar tudo local com Docker Compose

#### Etapa de produção do portfólio

- subir backend em Azure
- banco em cloud
- storage para uploads

Isso já é suficiente para falar em entrevista que o projeto foi preparado e publicado em ambiente real.

---

## Backend público é perigoso?

### Resposta curta

**Não, desde que você publique com responsabilidade.**

### O que NÃO fazer

- não expor credenciais
- não expor dados reais de usuário
- não deixar endpoints destrutivos sem proteção
- não usar chaves reais no repositório
- não publicar configurações sensíveis

### O que fazer

- usar `.env`
- usar variáveis de ambiente na cloud
- criar dados fake/demo
- limitar upload
- autenticação simples ou acesso demo
- documentar que é projeto educacional / portfólio

### Sobre domínio

Não precisa usar teu domínio principal.  
Você pode:

- manter no GitHub com README forte
- publicar backend em subdomínio depois
- publicar frontend em outro endereço
- ou deixar somente demo controlada

### Melhor estratégia de publicação

#### Opção segura

- backend privado ou parcialmente protegido
- frontend público com dados demo
- GIFs, screenshots e vídeo demo no portfólio

#### Opção forte de mercado

- backend publicado com autenticação demo
- frontend público com conta sandbox
- limites de uso

### Conclusão

Sim, pode publicar. Só precisa tratar como produto, não como script jogado na internet.

---

## Precisa de frontend?

### Resposta curta

**Sim, ajuda bastante.**

Mas não porque o backend precise.  
Porque **impacta mais no portfólio**.

### O que o frontend agrega

- mostra produto completo
- melhora demonstração visual
- facilita apresentar upload, status e resultados
- conecta com tua base de Next.js

### Melhor escolha

**Next.js + TypeScript**

Porque:

- conversa com teu stack atual
- fica profissional
- combina com portfólio
- permite página bonita e dashboard simples

### O que NÃO fazer

- não transformar o projeto em frontend-first
- o coração continua sendo backend + domínio + processamento

### Papel do frontend

O frontend deve ser:

- interface operacional
- tela de upload
- dashboard de jobs
- tabela de resultados
- detalhes do processamento

---

## Funcionalidades recomendadas

## MVP forte

### Backend

- upload CSV
- parser Binance CSV
- normalização
- validação
- cálculo FIFO básico
- persistência em PostgreSQL
- API para consultar resultados
- testes unitários
- Docker

### Frontend

- página de upload
- listagem de jobs
- status do processamento
- visualização de resultado resumido

---

## V1 robusta

### Backend

- autenticação simples
- histórico de importações
- tratamento de duplicidade
- relatórios exportáveis
- logs estruturados
- fila para processamento assíncrono
- retry para falhas temporárias

### Frontend

- dashboard com métricas
- detalhes por ativo
- detalhes do job
- tela de erros de validação

---

## V2 premium

### Backend

- integração com Binance API
- múltiplos usuários
- múltiplas fontes
- custo médio além de FIFO
- versionamento de regras
- snapshots de posição
- observabilidade em cloud
- documentação arquitetural forte

### Frontend

- autenticação
- filtros avançados
- comparativos por ativo
- UX melhorada

---

## Módulos de domínio sugeridos

### Entidades

- Transaction
- AssetPosition
- ProcessingJob
- ProcessingResult
- ValidationError

### Value Objects

- Money
- Quantity
- AssetSymbol
- TransactionType
- CostBasisMethod

### Serviços de domínio

- TransactionNormalizer
- TransactionValidator
- CostBasisCalculator
- ProfitLossCalculator
- PositionAggregator

### Casos de uso

- ImportTransactions
- ProcessTransactions
- GenerateReport
- GetJobStatus
- GetPortfolioSummary

---

## Endpoints sugeridos

### Ingestão

- `POST /api/v1/imports/csv`
- `POST /api/v1/imports/json`

### Jobs

- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/jobs`

### Processamento

- `POST /api/v1/process`
- `GET /api/v1/results/{job_id}`

### Relatórios

- `GET /api/v1/reports/{job_id}`
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/portfolio/assets/{symbol}`

### Health

- `GET /health`
- `GET /ready`

---

## Modelo de dados inicial

### transactions

- id
- user_id
- source
- external_id
- asset
- transaction_type
- quantity
- unit_price
- total_value
- fee_amount
- fee_asset
- occurred_at
- raw_payload
- created_at

### processing_jobs

- id
- user_id
- source_type
- status
- input_file_path
- started_at
- finished_at
- error_message
- created_at

### processing_results

- id
- job_id
- asset
- realized_profit
- cost_basis
- remaining_quantity
- result_payload
- created_at

### validation_errors

- id
- job_id
- row_number
- field_name
- error_code
- message
- created_at

---

## Segurança mínima recomendada

- variáveis de ambiente
- CORS controlado
- autenticação simples para área privada
- rate limit básico
- validação forte de payload
- upload com restrição de tamanho
- logs sem expor dado sensível

---

## Testes necessários

### Unitários

- parser
- normalizador
- validador
- cálculo FIFO
- lucro / prejuízo

### Integração

- API + banco
- upload + processamento
- job + resultado

### E2E simples

- upload pelo frontend
- consulta do resultado

### Casos de borda

- venda sem compra anterior
- taxa em ativo diferente
- transação duplicada
- arquivo inválido
- quantidade zero
- formato inesperado

---

## Qualidade de engenharia

Este projeto deve mostrar:

- código limpo
- separação de responsabilidades
- testabilidade
- logs úteis
- documentação clara
- deploy reproduzível

Ferramentas:

- Ruff
- Black
- Mypy
- pre-commit
- pytest
- coverage

---

## Documentação que deve existir

### README principal

- visão geral
- stack
- arquitetura
- como rodar local
- como testar
- endpoints
- roadmap

### Documento de arquitetura

- decisões técnicas
- por que fila
- por que PostgreSQL
- por que FastAPI
- por que arquitetura limpa/hexagonal

### Documento de domínio

- como funciona FIFO
- como transações são normalizadas
- quais regras existem

### Documento de deploy

- Docker
- variáveis de ambiente
- cloud

---

## Roadmap completo

## Fase 0 — Planejamento

- definir escopo MVP
- definir modelo de domínio
- definir arquitetura base
- definir nome e branding do projeto
- criar repositório

## Fase 1 — Núcleo do domínio

- modelar entidades e value objects
- implementar normalização
- implementar validação
- implementar cálculo FIFO básico
- criar testes unitários do domínio

## Fase 2 — Persistência e aplicação

- configurar PostgreSQL
- criar migrations
- implementar repositórios
- criar casos de uso
- persistir transações, jobs e resultados

## Fase 3 — API backend

- configurar FastAPI
- criar rotas principais
- validar requests/responses com Pydantic
- documentar endpoints
- criar health checks

## Fase 4 — Processamento assíncrono

- adicionar Redis
- implementar fila
- criar workers
- processar importações grandes em background
- adicionar status de job

## Fase 5 — Frontend operacional

- criar app em Next.js
- tela de upload
- dashboard de jobs
- visualização de resultados
- UX mínima mas bonita e funcional

## Fase 6 — Integração real

- adicionar parser de CSV da Binance
- opcional: integrar Binance API
- tratar múltiplos formatos de entrada
- robustecer normalização

## Fase 7 — Produção e cloud

- Dockerizar tudo
- criar Docker Compose local
- configurar CI com GitHub Actions
- subir backend em Azure
- subir banco em cloud
- configurar storage
- proteger secrets

## Fase 8 — Observabilidade e robustez

- logs estruturados
- métricas simples
- retries
- tratamento de falhas
- alertas básicos

## Fase 9 — Evoluções premium

- custo médio
- múltiplos usuários
- multi-source
- autenticação mais forte
- snapshots de posição
- relatórios mais ricos

---

## Roadmap por prioridade real

### Prioridade máxima

- domínio forte
- FIFO
- testes
- FastAPI
- PostgreSQL

### Prioridade alta

- CSV Binance
- frontend simples
- Docker
- deploy

### Prioridade média

- Redis + fila
- jobs assíncronos
- storage
- observabilidade

### Prioridade posterior

- Binance API
- autenticação completa
- analytics avançado
- IA

---

## Como falar dele em entrevista

### Versão curta

Construí uma plataforma de processamento de transações financeiras com Python, focada em ingestão, validação, aplicação de regras complexas de negócio e exposição dos resultados via API, com arquitetura limpa, processamento assíncrono e deploy em cloud.

### Versão ainda mais forte

Desenvolvi uma plataforma de data processing voltada a transações financeiras, simulando um cenário real de data platform: ingestão multi-fonte, normalização, cálculo de cost basis com FIFO, processamento assíncrono, persistência, API backend e preparação para operação em cloud.

---

## O que realmente é feito no mercado

Sim, no mercado real é comum ver exatamente essa combinação:

- backend Python com FastAPI
- PostgreSQL
- Redis para fila/cache
- processamento assíncrono
- APIs REST
- frontend separado em Next.js
- Docker
- CI/CD
- deploy em cloud
- observabilidade

Ou seja: essa direção está correta e conversa com o que empresas reais fazem.

---

## Escolha final recomendada

### Arquitetura

- Clean Architecture com inspiração hexagonal

### Backend

- FastAPI
- PostgreSQL
- Redis
- fila assíncrona

### Frontend

- Next.js
- TypeScript

### Cloud

- Azure

### Integração real

- CSV Binance primeiro
- Binance API depois

### Publicação

- demo segura
- dados fake/demo
- secrets protegidos

---

## Conclusão

Esse projeto deve ser tratado como:

- projeto número 1 do portfólio
- ativo estratégico de carreira
- demonstração de maturidade técnica
- ponte entre teu histórico em automação/dados financeiros e vagas mais fortes de backend/data platform

A meta não é apenas terminar.  
A meta é construir algo que, ao ser apresentado, faça recrutador e gestor técnico pensarem:

> esse cara entende domínio, backend, dados, arquitetura e produto.

## Dúvidas práticas — GitHub aberto, demo, autenticação e portfólio

## Vale a pena deixar o GitHub aberto?

### Resposta curta

**Sim, na maioria dos casos vale muito a pena.**

Especialmente porque esse projeto foi pensado para ser teu principal ativo técnico.

Um GitHub aberto ajuda a mostrar:

- código real
- organização
- arquitetura
- documentação
- testes
- maturidade de engenharia

### Quando faz sentido deixar aberto

- quando não existem dados reais sensíveis
- quando todas as credenciais estão protegidas
- quando o projeto usa dados fake/demo
- quando o objetivo é portfólio e posicionamento profissional

### Quando faz sentido restringir parte dele

- se houver integrações reais com contas pessoais
- se houver algum componente experimental que exponha demais a infraestrutura
- se quiser deixar algum módulo privado temporariamente durante construção

### Estratégia recomendada

A melhor abordagem é:

- **repositório público**
- documentação forte
- dados de demonstração
- segredos fora do código
- demo controlada

Isso te dá o melhor dos dois mundos: visibilidade e segurança.

---

## Publicar tudo na web é perigoso?

### Resposta curta

**Não, desde que o projeto seja preparado para isso.**

Publicar um sistema não é perigoso por si só. O risco está em publicar sem proteção mínima.

### O que torna um projeto perigoso

- credenciais no repositório
- banco exposto sem restrição
- autenticação inexistente onde deveria existir
- uploads sem validação
- endpoints administrativos públicos
- logs com dados sensíveis

### O que torna um projeto seguro o suficiente para portfólio

- variáveis de ambiente
- chaves e segredos fora do Git
- dados fake
- limite de upload
- autenticação simples para área privada
- ambiente demo separado
- documentação clara do que é demo

---

## Esse projeto precisa de usuário e senha?

### Resposta curta

**Para o backend real publicado: sim, é melhor ter.**

Mas não precisa começar com isso no primeiro dia.

### Melhor caminho

#### MVP inicial

- sem login
- apenas uso local ou controlado
- foco no domínio e na API

#### Versão de demonstração publicada

- login simples
- usuário demo
- proteção básica da área operacional

### Por que isso ajuda

Porque passa imagem de produto mais sério e evita deixar qualquer pessoa disparando upload/processamento livremente.

### Melhor opção de autenticação para esse caso

- autenticação simples por usuário/senha
- JWT ou sessão simples
- papel básico de usuário demo / admin demo

Não precisa inventar sistema complexo de identidade no começo.

---

## E se eu não quiser deixar tudo navegável publicamente?

Perfeito. Essa é uma ótima estratégia também.

### Modelo híbrido recomendado

#### Público

- landing page do projeto
- descrição da arquitetura
- screenshots
- GIFs curtos
- vídeo demo
- documentação
- repositório público

#### Protegido

- ambiente real da aplicação
- login necessário
- uso limitado

### Vantagem

Você mostra o que interessa visualmente e tecnicamente, sem deixar a aplicação totalmente aberta.

---

## Como mostrar no portfólio sem expor demais

### Estrutura ideal da apresentação

#### 1. Página do projeto no portfólio

Mostrar:

- contexto
- problema
- solução
- stack
- arquitetura
- screenshots
- resultados esperados
- link do GitHub
- link da demo (se existir)

#### 2. Screenshots

Pode mostrar telas como:

- tela de upload
- dashboard de jobs
- tela de resultado por ativo
- tela de erros de validação
- detalhe de processamento

#### 3. GIF ou vídeo curto

Muito forte para portfólio. Exemplo:

- subir CSV
- job em processamento
- resultado final

#### 4. Observação de segurança

Pode escrever algo como:

> A demonstração pública utiliza dados fictícios e ambiente controlado. Credenciais, segredos e integrações sensíveis não são expostos.

Isso passa maturidade.

---

## Melhor estratégia de publicação para esse projeto

## Opção A — Mais segura e prática

### GitHub

- público

### Backend

- publicado, mas protegido por autenticação demo

### Frontend

- público

### Banco e storage

- cloud com secrets protegidos

### Resultado

Ótimo equilíbrio entre impacto e segurança.

---

## Opção B — Portfólio visual primeiro

### GitHub

- público

### Aplicação web

- não totalmente aberta

### Portfólio mostra

- screenshots
- vídeo demo
- documentação
- arquitetura

### Resultado

Menos risco operacional e ainda muito forte para recrutadores.

---

## Opção C — Projeto privado por tempo limitado

### Quando usar

- enquanto ainda estiver muito cru
- enquanto ainda estiver organizando estrutura

### Depois

- abrir quando estiver apresentável

### Observação

Essa opção é aceitável no início, mas para portfólio principal o ideal é abrir quando estiver limpo.

---

## O que eu recomendo para o teu caso

### Recomendação principal

1. desenvolver localmente primeiro
2. organizar repositório e README
3. abrir o GitHub quando a base estiver limpa
4. publicar frontend com visual bonito
5. publicar backend com autenticação demo
6. mostrar screenshots e vídeo no portfólio

### Tradução prática

- não precisa abrir tudo hoje
- mas o objetivo final deve ser **GitHub público + demo controlada**

---

## Precisa mesmo de frontend?

### Se o objetivo é impactar mais: sim

O mercado real tem muito backend sem frontend, mas no portfólio o frontend ajuda muito porque:

- facilita entendimento imediato
- chama atenção visualmente
- mostra produto completo
- melhora a percepção de maturidade

### Melhor papel do frontend

Não fazer um SaaS gigante. Fazer uma interface enxuta e útil:

- upload
- status do job
- tabela de resultados
- detalhes por ativo
- relatórios

---

## Qual é a arquitetura mais “de mercado” nesse caso?

### O que mais conversa com vagas reais hoje

- backend em FastAPI
- frontend em Next.js
- PostgreSQL
- Redis
- jobs assíncronos
- Docker
- deploy em cloud
- GitHub Actions

Essa combinação é forte, moderna e realista.

---

## Como isso pode ficar no portfólio

### Exemplo de bloco visual

**Crypto Data Processing Platform**

Plataforma de processamento de transações financeiras construída com Python e FastAPI, focada em ingestão de dados, normalização, cálculo de cost basis com FIFO, processamento assíncrono e exposição via API. Projeto pensado com arquitetura limpa, persistência em PostgreSQL, fila com Redis e deploy em cloud.

### Links

- GitHub
- Live Demo
- Architecture Notes

---

## Regra final para tomada de decisão

### Se a pergunta for:

"Deixo aberto ou não?"

A melhor resposta é:

**Sim, mas com responsabilidade.**

### Se a pergunta for:

"Precisa login?"

A melhor resposta é:

**Sim para a demo publicada; não necessariamente para o primeiro MVP local.**

### Se a pergunta for:

"Precisa frontend?"

A melhor resposta é:

**Sim, porque aumenta muito o impacto do portfólio, desde que o backend continue sendo o núcleo do projeto.**

### Se a pergunta for:

"Como mostrar sem me expor demais?"

A melhor resposta é:

**GitHub público, dados fake, demo controlada, screenshots, vídeo e ambiente protegido.**
