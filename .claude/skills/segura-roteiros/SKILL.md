---
name: segura-roteiros
description: Roteirista do canal Segura Aí 3D (TikTok de segurança do dia a dia em animação 3D, separado da Nexus). Escreve um lote de roteiros no método tentativa-e-erro com placar, a partir das ideias de segura-ai/fila.json, confere cada um com a prévia das cenas e põe na fila de produção. Roda no GitHub Actions (workflow segura-roteiros.yml).
---
> **Execução sem supervisão:** não pare para perguntar; termine o lote inteiro.
> **Escreva cada roteiro direto com a ferramenta Write** em `segura-ai/roteiros/SLUG.json` e edite
> `fila.json` com Edit. Não crie scripts geradores nem rode Python seu: só os dois comandos abaixo são
> liberados, e exatamente assim, sem `cd` nem `&&` na frente.
> Este canal NÃO segue a voz de Rafa Lins nem as regras de posts do CLAUDE.md da Nexus:
> só as regras desta skill e de `segura-ai/CATALOGO.md`.

# Segura Aí 3D: lote de roteiros

1. Leia `segura-ai/CATALOGO.md` inteiro, `segura-ai/config.yaml` e `segura-ai/fila.json`.
   Leia o roteiro de exemplo `segura-ai/roteiros/trocar-lampada.json` (é o padrão de qualidade).
2. Pegue as primeiras ideias de `fila.json > ideias` até completar `producao.roteiros_por_lote`.
   Pule ideias cujo slug já exista em `segura-ai/roteiros/`. Se acabarem, crie ideias novas de
   acidentes domésticos comuns no Brasil (eletricidade, fogo, gás, quedas, crianças, ferramentas),
   sempre com uma solução que caiba nos objetos do catálogo.
   Leia também `segura-ai/estrategia.json` e `segura-ai/relatorio_testes.md` (se existir): eles dizem o que o
   público está preferindo. Para `gancho` e `duracao`: se houver vencedor, use sempre o vencedor; se não,
   distribua as opções em rodízio pelo lote (cada roteiro usa uma). Grave no roteiro
   `"teste": {"gancho": "OPÇÃO", "duracao": "OPÇÃO"}`. Escreva também `"pergunta"`: uma pergunta curta
   para a legenda (ex.: "Você já levou choque trocando o chuveiro?"). Dê preferência aos temas que o
   relatório de testes aponta como os que mais deram visualização.
3. Para cada ideia:
   a. **Pesquise a dica certa** (WebSearch/WebFetch) numa fonte confiável: NR do Ministério do
      Trabalho, Corpo de Bombeiros, Defesa Civil, ABNT, manual de fabricante. Nada inventado.
      Ponha as fontes em `fontes`. Se a solução exige profissional, o jeito certo é chamar o profissional.
   b. Escreva o roteiro no formato do catálogo: gancho que fala com quem assiste, 2 ou 3 tentativas
      erradas com placar e rebobinar, o jeito certo em passos numerados, final com recompensa e a
      chamada (segue + comenta UMA palavra). palavras conforme a `duracao` do teste (sempre entre 160 e 290), 10 a 16 cenas, frases curtas,
      humor de amigo, desastres cômicos sem sangue. Título de até 95 caracteres.
   c. Use só ambientes, objetos, ações, câmeras e efeitos do catálogo.
   d. Gere a prévia: `python3 segura-ai/montar.py segura-ai/roteiros/SLUG.json --folha --saida /tmp/folhas`
      e abra `/tmp/folhas/SLUG-folha.jpg` com Read. Corrija o que estiver errado (personagem fora da
      tela, objeto escondido, câmera que não mostra o que a fala diz, etiqueta em cima do rosto) e
      gere de novo. No máximo 3 tentativas por roteiro.
   e. Acrescente `{"slug": "SLUG", "status": "pronto"}` no fim de `fila.json > roteiros` e tire a ideia usada de `ideias`.
4. Rode `python3 segura-ai/diario.py --checar`: tem que terminar em OK.
5. Atualize o escritório: `python3 scripts/escritorio.py feito seg_roteirista "<uma frase com quantos roteiros e quais>"`.
6. Termine com uma linha por roteiro: slug, palavras e o gancho.
