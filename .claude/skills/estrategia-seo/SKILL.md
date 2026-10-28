---
name: estrategia-seo
description: Rotina semanal de estratégia. O estrategista de SEO analisa o blog inteiro, escreve data/relatorio_seo.md e o curador renova as sugestões de produtos.
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Bash(python3 scripts/verificar.py:*), Bash(date:*)
---
1. Chame o subagente `seo` pedindo o **relatório semanal** (modo 2).
2. Chame o subagente `curador` para renovar `data/sugestoes_produtos.md`,
   priorizando os subnichos e as datas sazonais que o relatório apontou.
3. Acrescente ao fim de `data/diario.md`:
   `- AAAA-MM-DD (semanal): relatório SEO atualizado; prioridades: ...`
4. Em `data/escritorio.json`, atualize `seo` e `curador` (status `ok` e uma
   frase sobre o que fizeram) e acrescente uma entrada no `historico` para
   cada um, mantendo as 60 mais recentes. Não mexa nos outros agentes.
Termine com as 5 prioridades da semana.
