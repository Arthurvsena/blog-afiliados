---
name: rotina-diaria
description: Rotina diária do portal. Pauta e publica as notícias do dia, escreve os guias de compra, revisa SEO, vendas e design, e atualiza posts antigos. Rodada todo dia pelo GitHub Actions.
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Bash(python3 scripts/verificar.py:*), Bash(python3 site/build.py:*), Bash(date:*)
---

> **Execução sem supervisão (GitHub Actions):** chame cada subagente com a
> ferramenta Agent usando `run_in_background: false` e espere a resposta antes
> de seguir. Nunca deixe agentes rodando em segundo plano, nunca use
> ScheduleWakeup/Monitor e nunca encerre dizendo que vai "continuar depois":
> quando sua resposta final sair, a execução acaba e o trabalho pendente é
> perdido. Só termine depois do último passo.

Você é o editor-chefe do blog. Coordene os subagentes nesta ordem e não
pule etapas. Leia `CLAUDE.md`, `config.yaml` e **`data/estrategia.md`** (o
plano da semana, com as 4 metas: vendas, cliques, acessos e engajamento)
primeiro, e rode `python3 scripts/mural.py listar` para ver os pedidos
abertos entre os agentes. Se existir `data/relatorio_metricas.md`, leia
também. **Toda escolha do dia deve servir a uma aposta do plano**: pautas com
`"prioridade": "alta"` vêm antes das outras, e ao chamar cada subagente diga
qual aposta e quais mensagens do mural ele precisa atender.

Leia também `editorial/manual.md` e `editorial/voz.md`: todo texto do dia
sai na voz de Rafa Lins.

1. **Notícias do dia (pauta).** Chame o `pesquisador` em modo **notícias**.
   Ele traz `rotina.noticias_por_dia` pautas com `"prioridade": "hoje"` e
   fontes confirmadas, e descarta notícias pendentes velhas.

2. **Fila de pautas.** Conte as pautas pendentes que não são notícia. Se
   houver menos de 10, chame o `pesquisador` em modo **fila**. Se
   `data/palavras.json` não existir, rode antes `python3 scripts/palavras.py`.

3. **Escolha das pautas do dia.**
   - Notícias: as `rotina.noticias_por_dia` pautas `"prioridade": "hoje"`,
     variando editorias. Se faltar notícia forte, complete com um tutorial ou
     uma análise da fila.
   - Guia de compras: `rotina.posts_novos_por_dia` pautas pendentes que já
     podem ser escritas (produtos `ativo=sim` suficientes no subnicho ou tipo
     `guia`), alternando subnichos. Pautas `"prioridade": "alta"` (da reunião)
     vêm primeiro.

4. **Produtos.** Se 3 ou mais pautas de guia de compras estão travadas por
   falta de produtos, chame o `curador`.

5. **Escrita e revisão (uma pauta por vez, notícias primeiro).** Para cada
   pauta escolhida, nesta ordem:
   a. `redator` com a pauta completa (JSON). Se ele responder "NOTÍCIA NÃO
      CONFIRMADA" ou "SEM PRODUTOS SUFICIENTES", marque a pauta como
      `"status": "descartada"` (notícia) ou deixe pendente (compra) e escolha outra.
   b. `seo` em modo revisão, com o caminho do arquivo.
   c. `vendas` em modo revisão (em notícias ele só liga o post ao guia de
      compras, sem forçar venda).
   d. `designer` em modo revisão visual. Nenhum post é publicado sem passar por ele.
   e. Marque a pauta como `"status": "publicada"` com `"post": "SLUG"`.

6. **Atualização.** Escolha `rotina.atualizacoes_por_dia` posts que não sejam
   notícia, com a data `atualizado` mais antiga (pelo menos 30 dias atrás) e chame o subagente
   `atualizador` para cada um e, se ele mudou o post, chame `vendas` e depois
   o `designer` em seguida. Se nenhum post tiver 30+ dias, pule.

6b. **Posts antigos sem venda ou design.** Para até 2 posts publicados por dia
   que ainda tenham avisos "vendas:" no `python3 scripts/verificar.py` ou não
   tenham `capa_frase`, chame `vendas` e depois `designer`.

7. **Checagem final.** Rode `python3 scripts/verificar.py` (sem argumentos,
   verifica tudo) e `python3 site/build.py`. Se algo falhar, corrija o post
   problemático. Se não der para corrigir, mova-o para `content/rascunhos/`.

7b. **Mural.** Rode `python3 scripts/mural.py listar` de novo. Mensagens que
   ninguém conseguiu resolver há mais de 3 dias: responda dizendo por quê e o
   que fazer (ou reencaminhe para o agente certo).

8. **Diário.** Acrescente ao fim de `data/diario.md` uma linha:
   `- AAAA-MM-DD: N notícias (slugs), N guias de compra (slugs), N atualizados, fila com N pautas, avisos: ...`
   Nos avisos, diga ao dono o que ele precisa fazer (ex.: "cadastrar
   produtos sugeridos em data/sugestoes_produtos.md").

9. **Escritório.** Atualize `data/escritorio.json` (é o que aparece na página
   `/escritorio/`, onde a equipe aparece trabalhando):
   - `ultima_execucao`: data e hora de agora, formato `AAAA-MM-DDTHH:MM`
     (horário de Brasília; use `TZ=America/Sao_Paulo date +%Y-%m-%dT%H:%M`).
   - Em `agentes`, para `chefe`, `pesquisador`, `curador`, `redator`, `seo`,
     `vendas`, `designer` e `atualizador` (não mexa no `analista`): `status` = `ok` (trabalhou hoje), `ocioso` (não foi chamado)
     ou `erro` (falhou ou travou) e `tarefa` = uma frase curta e concreta do que
     fez hoje, escrita como um colega contaria (ex.: "Escrevi a notícia do
     novo Galaxy e a lista 'Os 5 melhores power banks até R$ 150'."). Ocioso:
     diga por quê.
   - Em `historico`, acrescente uma entrada por agente que trabalhou:
     `{"data": "AAAA-MM-DD", "agente": "redator", "texto": "..."}`.
     Mantenha só as 60 entradas mais recentes.
   Depois rode `python3 site/build.py` de novo.

Termine com o mesmo resumo da linha do diário.
