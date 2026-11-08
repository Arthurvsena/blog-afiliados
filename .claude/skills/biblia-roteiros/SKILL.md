---
name: biblia-roteiros
description: Roteirista do canal Bíblia Animada (separado da Nexus). Escreve um lote de roteiros de Shorts de histórias bíblicas em animação 2D, no método do canal Pixel US, a partir das ideias de canal-biblia/fila.json, confere cada um com a prévia das cenas e põe na fila de produção. Roda no GitHub Actions (workflow biblia-roteiros.yml).
---
> **Execução sem supervisão:** não pare para perguntar; termine o lote inteiro.
> Este canal NÃO segue a voz de Rafa Lins nem as regras de posts do CLAUDE.md da Nexus:
> só as regras desta skill e de `canal-biblia/CATALOGO.md`.

# Bíblia Animada: lote de roteiros

1. Leia `canal-biblia/CATALOGO.md` inteiro, `canal-biblia/config.yaml` e `canal-biblia/fila.json`.
   Leia também 2 roteiros prontos como exemplo (`canal-biblia/roteiros/davi-e-golias.json` e
   `canal-biblia/roteiros/daniel-na-cova-dos-leoes.json`).
2. Pegue as primeiras ideias de `fila.json > ideias` até completar `producao.roteiros_por_lote`
   (config). Pule ideias cujo slug já exista em `canal-biblia/roteiros/`. Se as ideias acabarem,
   acrescente histórias bíblicas conhecidas que ainda não foram feitas (alterne Antigo e Novo Testamento).
3. Para cada história:
   a. Confira o texto bíblico (passagem da ideia). Se tiver dúvida de um detalhe, pesquise (WebSearch)
      numa fonte da Bíblia (ex.: bibliaonline.com.br). Nada inventado: nem falas, nem números.
   b. Escreva o roteiro no formato do catálogo: cena 1 é o gancho; 6 a 8 cenas; 70 a 130 palavras;
      virada no meio; última cena é o versículo (curto e fiel, com a referência). Título de até 95
      caracteres que faz a pessoa querer saber o final (sem mentir). `heroi.cores`: 4 ou 5 cores que
      combinem entre si e sejam diferentes das últimas histórias.
   c. Use só cenários, elementos, poses e efeitos que estão no catálogo.
   d. Gere a prévia: `python3 canal-biblia/montar.py canal-biblia/roteiros/SLUG.json --sem-voz --folha --saida /tmp/folhas`
      e abra `/tmp/folhas/SLUG-folha.jpg` com Read. Corrija o que estiver errado (herói fora da tela,
      elemento escondido atrás de outro, cena que não mostra o que a fala diz) e gere de novo.
      No máximo 3 tentativas por história.
   e. Acrescente `{"slug": "SLUG", "status": "pronto"}` no fim de `fila.json > historias` e tire a ideia usada de `ideias`.
4. Rode `python3 canal-biblia/diario.py --checar`: tem que terminar em OK.
5. Termine com uma linha por roteiro: slug, número de palavras e o gancho.
