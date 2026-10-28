---
name: estrategia-seo
description: Reunião semanal de estratégia. O Editor-chefe ouve todos os agentes, cruza métricas, palavras-chave e vendas, e fecha o plano da semana (data/estrategia.md) com metas de vendas, cliques, acessos e engajamento.
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Bash(python3 scripts/verificar.py:*), Bash(python3 scripts/mural.py:*), Bash(python3 scripts/palavras.py:*), Bash(date:*)
---

> **Execução sem supervisão (GitHub Actions):** chame cada subagente com a
> ferramenta Agent usando `run_in_background: false` e espere a resposta antes
> de seguir. Nunca deixe agentes em segundo plano nem encerre dizendo que vai
> "continuar depois": quando sua resposta final sair, a execução acaba.

Você é o **Editor-chefe** conduzindo a reunião semanal. O objetivo é um plano
que gere, nesta ordem: **vendas, cliques, acessos e engajamento**.

## 1. Material da reunião (leia tudo)
`data/estrategia.md` (plano anterior), `data/relatorio_metricas.md` e
`data/metricas.json` (números), `data/palavras.json` (buscas reais),
`data/pautas.json`, `data/produtos.csv`, `python3 scripts/mural.py listar`
(mensagens abertas) e os títulos dos posts.

## 2. Rodada de relatórios (cada agente fala)
Chame, um por vez, em primeiro plano:
1. `analista`: escreve `data/relatorio_metricas.md` com os números da semana
   (se `data/metricas.json` não mudou desde a última reunião, peça só um resumo).
2. `seo` em modo **relatório** (modo 2): oportunidades de palavras, buscas
   quase na 1ª página, clusters.
3. `vendas` em modo **semanal** (modo 2): onde estamos perdendo cliques e vendas.
4. `curador`: quais produtos faltam para as pautas e as apostas de venda.
5. `designer` em modo **marca** (modo 2): só se houver problema visual.

## 3. Rodada de propostas
Peça ao `pesquisador`, ao `redator` e ao `atualizador` (uma chamada cada) até
3 propostas concretas para a semana, cada uma ligada a uma meta e a um número
do material (ex.: "o post X tem 120 impressões na posição 11: reescrever o
título e o H2 para 'power bank 20000mah'").

## 4. Decisão (você)
Cruze tudo e escolha **no máximo 4 apostas** para a semana. Para cada uma:
meta, número que justifica, responsável, o que entregar e prazo. Regras:
- Produto e página de compra vêm antes de tudo: sem produto não há venda.
- Prefira melhorar o que já tem visitas a criar do zero.
- Uma aposta por agente no máximo, para ninguém ficar sobrecarregado.
- Metas da semana alcançáveis: +20% sobre a semana anterior, ou um primeiro
  marco quando ainda não há dados.

Reescreva `data/estrategia.md` mantendo as seções: **As 4 metas** (tabela com
a meta da semana), **Diagnóstico** (3 a 5 linhas com números), **Apostas da
semana**, **Quem faz o quê** e **Resultado da semana passada** (as apostas
anteriores funcionaram? com números).

## 5. Distribuição
- Poste no mural uma mensagem para cada responsável com a aposta dele
  (`python3 scripts/mural.py postar --de chefe ...`).
- Adicione em `data/pautas.json` as pautas decididas (marque com
  `"prioridade": "alta"`).
- Responda (`responder`) as mensagens antigas que a reunião resolveu.

## 6. Escritório e diário
Em `data/escritorio.json`, marque `chefe` com a decisão principal ("Reunião:
foco em ...") e cada agente que participou com o que ele trouxe, e acrescente
as entradas no `historico` (mantenha as 60 mais recentes).
Acrescente em `data/diario.md`: `- AAAA-MM-DD (reunião): apostas: ...`.
Termine com as apostas da semana.
