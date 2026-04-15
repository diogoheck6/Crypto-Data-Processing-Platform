A partir do markdown do meu projeto e dos documentos já existentes no repositório, quero que você me ajude a transformar a visão do projeto em um sistema de execução dentro do próprio repositório.

Quero trabalhar com você no VS Code de forma iterativa, sempre sabendo:

- o que já foi feito
- o que falta
- qual é o próximo passo
- qual tarefa executar agora
- quais arquivos serão criados ou alterados
- como validar se a etapa foi concluída corretamente

Com base nisso, gere e mantenha os seguintes arquivos em markdown dentro de `docs/`:

1. `docs/MVP_SCOPE.md`
   - escopo enxuto do MVP
   - o que entra agora
   - o que fica para depois
   - definição clara do que não será feito nesta fase

2. `docs/ROADMAP.md`
   - roadmap macro do projeto por fases
   - ordem lógica de construção
   - dependências entre fases
   - objetivo de cada fase

3. `docs/CHECKLIST.md`
   - checklist operacional completo
   - dividido por fases
   - com tarefas pequenas e executáveis
   - caixas de seleção markdown
   - em ordem prática de execução

4. `docs/BACKLOG.md`
   - backlog em formato de épicos e tarefas
   - priorização
   - critérios de aceite
   - tarefas quebradas em blocos pequenos

5. `docs/STATUS.md`
   - documento para manter o estado atual do projeto
   - deve ter:
     - fase atual
     - feito
     - em andamento
     - próximo passo
     - bloqueios
     - decisões recentes

6. `docs/NEXT_STEP.md`
   - documento curto e objetivo
   - usado para orientar cada sessão de trabalho
   - deve conter:
     - contexto atual
     - o que já existe
     - tarefa da sessão
     - arquivos envolvidos
     - definição de pronto da tarefa
     - observações importantes

7. `docs/ARCHITECTURE.md`
   - visão arquitetural do projeto
   - arquitetura limpa com inspiração hexagonal
   - separação entre domínio, aplicação e infraestrutura
   - responsabilidades de cada camada
   - decisões técnicas

Importante:

- escreva tudo em português
- não seja genérico
- organize de forma prática
- pense como um projeto real de engenharia
- priorize domínio, backend e testes antes do frontend
- considere que o projeto usará:
  - Python
  - FastAPI
  - PostgreSQL
  - Redis
  - fila assíncrona
  - Docker
  - Next.js no frontend
  - Azure no futuro
- considere que a arquitetura limpa e a inspiração hexagonal já fazem parte da direção do projeto
- não comece pelo frontend
- o checklist deve ser detalhado o suficiente para eu executar passo a passo junto com a IA

Regras obrigatórias de execução:

1. Sempre leia primeiro:
   - `docs/STATUS.md`
   - `docs/NEXT_STEP.md`
   - `docs/ROADMAP.md`
   - `docs/CHECKLIST.md`
   - `docs/ARCHITECTURE.md`

2. Nunca assuma que algo já foi feito se isso não estiver registrado em `STATUS.md` ou marcado no `CHECKLIST.md`.

3. Trabalhe em uma tarefa por vez.

4. Sempre diga:
   - em que fase estamos
   - qual é a tarefa atual
   - por que ela vem agora
   - quais arquivos serão criados ou alterados
   - o que significa concluir essa tarefa

5. Ao final de cada tarefa, sempre proponha a atualização de:
   - `docs/STATUS.md`
   - `docs/NEXT_STEP.md`
   - `docs/CHECKLIST.md`

6. Não pule etapas.
   Não tente construir tudo de uma vez.
   Não avance para a próxima tarefa sem fechar a atual.

7. Sempre respeite a separação entre:
   - domínio
   - aplicação
   - infraestrutura
   - interface

8. Sempre que possível, trate testes como parte obrigatória da entrega.

Diretriz específica sobre testes:

- testes não são opcionais
- toda regra de negócio importante deve ter teste
- toda etapa relevante deve considerar validação
- inclua testes no roadmap, checklist, backlog e definição de pronto
- para cada funcionalidade importante, indique:
  - o que deve ser testado
  - se o teste é unitário, integração ou e2e
  - qual é o mínimo aceitável para considerar a etapa concluída

Explique também, quando fizer sentido, por que os testes são importantes naquela etapa, especialmente para:

- regras financeiras
- cálculos
- validação de dados
- fluxos de processamento
- API
- persistência

Fluxo de trabalho esperado em cada sessão:

1. Ler o estado atual nos arquivos
2. Identificar a tarefa da sessão
3. Explicar o objetivo da tarefa
4. Quebrar em passos pequenos
5. Guiar a execução passo a passo
6. Definir como validar se ficou pronto
7. Propor atualização da documentação
8. Sugerir o próximo passo, sem executá-lo ainda

Objetivo final:
Construir um projeto real de engenharia de software, com qualidade suficiente para servir como projeto principal de portfólio, demonstrando domínio de backend, dados, arquitetura, testes, processamento assíncrono e preparação para cloud.

Agora comece lendo os arquivos de documentação do projeto e me diga:

- em que fase estamos
- qual deve ser a tarefa atual
- e quais arquivos/documentos precisam ser criados ou atualizados primeiro
