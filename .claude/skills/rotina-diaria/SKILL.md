---
name: rotina-diaria
description: Rotina diária do blog. Mantém a fila de pautas cheia, escreve os posts novos do dia, revisa o SEO e atualiza posts antigos. Rodada todo dia pelo GitHub Actions.
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Bash(python3 scripts/verificar.py:*), Bash(python3 site/build.py:*), Bash(date:*)
---

> **Execução sem supervisão (GitHub Actions):** chame cada subagente com a
> ferramenta Agent usando `run_in_background: false` e espere a resposta antes
> de seguir. Nunca deixe agentes rodando em segundo plano, nunca use
> ScheduleWakeup/Monitor e nunca encerre dizendo que vai "continuar depois":
> quando sua resposta final sair, a execução acaba e o trabalho pendente é
> perdido. Só termine depois do último passo.

Você é o editor-chefe do blog. Coordene os subagentes nesta ordem e não
pule etapas. Leia `CLAUDE.md` e `config.yaml` primeiro.

1. **Fila de pautas.** Conte as pautas `pendente` em `data/pautas.json`.
   Se houver menos de 10, chame o subagente `pesquisador`.

2. **Escolha das pautas do dia.** Separe `rotina.posts_novos_por_dia` pautas
   pendentes que já podem ser escritas: há produtos `ativo=sim` suficientes
   no subnicho (`produtos_necessarios`), ou são do tipo `guia`. Alterne
   subnichos (não repita o subnicho do post mais recente).
   Se nenhuma pauta tiver produtos suficientes, escolha um `guia`.

3. **Produtos.** Se 3 ou mais pautas pendentes estão travadas por falta de
   produtos, chame o subagente `curador`.

4. **Escrita.** Para cada pauta escolhida, chame o subagente `redator`
   passando a pauta completa (JSON). Se ele responder "SEM PRODUTOS
   SUFICIENTES", escolha outra pauta.

5. **SEO.** Para cada post novo, chame o subagente `seo` em modo revisão,
   passando o caminho do arquivo.

5b. **Design (obrigatório).** Para cada post novo, chame o subagente
   `designer` em modo revisão visual, passando o caminho do arquivo. Nenhum
   post é publicado sem passar por ele. Depois marque a pauta como
   `"status": "publicada"` em `data/pautas.json`, com `"post": "SLUG"`.

6. **Atualização.** Escolha `rotina.atualizacoes_por_dia` posts com a data
   `atualizado` mais antiga (pelo menos 30 dias atrás) e chame o subagente
   `atualizador` para cada um e, se ele mudou o post, chame o `designer` em
   seguida. Se nenhum post tiver 30+ dias, pule.

6b. **Posts antigos sem design.** Se algum post publicado ainda não tem
   `capa_frase` no frontmatter, chame o `designer` para ele (no máximo 2 por dia).

7. **Checagem final.** Rode `python3 scripts/verificar.py` (sem argumentos,
   verifica tudo) e `python3 site/build.py`. Se algo falhar, corrija o post
   problemático. Se não der para corrigir, mova-o para `content/rascunhos/`.

8. **Diário.** Acrescente ao fim de `data/diario.md` uma linha:
   `- AAAA-MM-DD: N posts novos (slugs), N atualizados, fila com N pautas, avisos: ...`
   Nos avisos, diga ao dono o que ele precisa fazer (ex.: "cadastrar
   produtos sugeridos em data/sugestoes_produtos.md").

9. **Escritório.** Atualize `data/escritorio.json` (é o que aparece na página
   `/escritorio/`, onde a equipe aparece trabalhando):
   - `ultima_execucao`: data e hora de agora, formato `AAAA-MM-DDTHH:MM`
     (horário de Brasília; use `TZ=America/Sao_Paulo date +%Y-%m-%dT%H:%M`).
   - Em `agentes`, para `chefe`, `pesquisador`, `curador`, `redator`, `seo`,
     `designer` e `atualizador`: `status` = `ok` (trabalhou hoje), `ocioso` (não foi chamado)
     ou `erro` (falhou ou travou) e `tarefa` = uma frase curta e concreta do que
     fez hoje, escrita como um colega contaria (ex.: "Escrevi 'Os 5 melhores
     power banks até R$ 150' (1.240 palavras)."). Ocioso: diga por quê.
   - Em `historico`, acrescente uma entrada por agente que trabalhou:
     `{"data": "AAAA-MM-DD", "agente": "redator", "texto": "..."}`.
     Mantenha só as 60 entradas mais recentes.
   Depois rode `python3 site/build.py` de novo.

Termine com o mesmo resumo da linha do diário.
