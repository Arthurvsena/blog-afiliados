# Portal "Tech Barato BR": regras do projeto

Este repositório é um portal de tecnologia (notícias de celulares, games, IA e
tecnologia, análises e tutoriais) com um **guia de compras** de eletrônicos
custo-benefício. Ganha com anúncios do Google AdSense e com o programa de
afiliados do Mercado Livre. Os agentes em `.claude/agents/` mantêm o site
todos os dias.

**Todo texto é escrito na voz de Rafa Lins** (`editorial/voz.md`), seguindo o
manual de redação (`editorial/manual.md`).

## Estrutura
- `config.yaml`: nome do site, editorias (notícias), subnichos (guia de
  compras), quantos posts por dia, autor, anúncios e domínio.
- `editorial/voz.md` e `editorial/manual.md`: a voz do autor e o método de
  cada formato (notícia, análise, tutorial, guias de compra).
- `data/produtos.csv`: catálogo de produtos com link de afiliado. Links só
  entram pela skill `cadastrar-produtos` (que gera no Gerador de Links do
  Mercado Livre pelo Chrome do dono) ou pelo próprio dono. Nenhum agente
  inventa ou altera um `link_afiliado`.
- `data/palavras.json`: termos reais de busca (autocompletar do Google e do
  Mercado Livre, Search Console), atualizado toda segunda por
  `scripts/palavras.py`. Toda palavra-chave de post sai daqui.
- `data/pautas.json`: fila de pautas (ideias de posts) criada pelo pesquisador.
- `data/sugestoes_produtos.md`: produtos que o curador recomenda o dono cadastrar.
- `data/estrategia.md`: **plano da semana** com as 4 metas (vendas, cliques,
  acessos, engajamento), decidido na reunião de segunda. Todos leem antes de trabalhar.
- `data/mural.json`: mural da equipe. Agentes trocam pedidos com
  `python3 scripts/mural.py listar|postar|responder`.
- `data/relatorio_seo.md`: relatório semanal do estrategista de SEO.
- `data/metricas.json` e `data/relatorio_metricas.md`: números da semana e
  análise do `analista` (visitas, cliques no ML, pedidos, Google).
- `data/relatorio_vendas.md`: apostas de venda da semana (agente `vendas`).
- `content/posts/*.md`: os posts (Markdown com frontmatter YAML).
- `design/marca.yaml`: identidade visual (cores, fontes, logo, regras), mantida
  pelo agente `designer`. O site lê as cores e fontes daqui.
- `scripts/verificar.py`: checagem de qualidade. Rode antes de terminar.
- `site/build.py`: gera o site em `_site/` (o GitHub Actions faz isso sozinho).

## Formato de um post
Notícia, análise ou tutorial (com `editoria`):
```markdown
---
titulo: "Samsung confirma o Galaxy X no Brasil: preço e data"
slug: samsung-galaxy-x-brasil-preco
descricao: "Linha fina com o dado mais útil que não está no título."
palavra_chave: "galaxy x preço brasil"
editoria: celulares        # celulares | games | inteligencia-artificial | tecnologia | analises | tutoriais
tipo: noticia              # noticia | analise | tutorial
publicado: 2026-10-29 14:30
atualizado: 2026-10-29
fontes:
  - nome: "Samsung Newsroom Brasil"
    url: "https://..."
tags: ["Samsung", "Galaxy X", "lançamento"]
capa_frase: "Chegou ao Brasil"
---
```
Guia de compras (com `subnicho`):
```markdown
---
titulo: "Os 5 melhores fones Bluetooth até R$ 200 em 2026"
slug: melhores-fones-bluetooth-ate-200
descricao: "Até 155 caracteres, com a palavra-chave e um motivo para clicar."
palavra_chave: "melhor fone bluetooth até 200 reais"   # termo real do palavras.json
palavras_secundarias: ["fone bluetooth barato bom", "fone sem fio custo beneficio"]
subnicho: fones-caixas-bluetooth
tipo: lista          # lista | review | comparativo | guia
produtos: [id-1, id-2]
publicado: 2026-10-28
atualizado: 2026-10-28
capa_frase: "10.000 mAh que cabem no bolso"   # o designer escreve
faq:
  - pergunta: "..."
    resposta: "..."
---
Texto em Markdown. Para mostrar o card de um produto com botão de compra,
escreva numa linha sozinha: {{produto:ID}}
Link de oferta no meio do texto: {{link:ID}} ou {{link:ID|texto}}.
Botão pequeno (cabe em tabela): {{botao:ID}} ou {{botao:ID|Ver preço}}.

Componentes visuais (o designer aplica; cada bloco fecha com ::: sozinho):
:::pros            :::contras          :::veredito
- ponto            - ponto             Uma frase forte.
:::                :::                 :::
:::dica            :::atencao   (título opcional na mesma linha: ":::dica Antes de comprar")
```

## Regras inegociáveis (valem para todos os agentes)
0. **Notícia só com fonte.** Fato confirmado na fonte oficial ou em duas fontes
   confiáveis, listadas em `fontes`. Rumor é tratado como rumor. Nunca copie
   nem parafraseie de perto o texto de outro site.
1. **Nunca invente fatos.** Especificações, preços, notas e números de
   avaliações vêm de `data/produtos.csv` ou de páginas que você abriu com
   WebFetch/WebSearch nesta execução. Se não tiver certeza, não escreva.
   Não afirme ter testado um produto pessoalmente.
2. **Preço não vai no texto dos guias de compra.** Preços mudam. Diga "veja o
   preço atual" e deixe o card mostrar a faixa de preço do CSV. Em notícias de
   lançamento, o preço oficial entra com a data ("preço de lançamento").
3. **Links de compra só via `{{produto:ID}}`**, com IDs de produtos com
   `ativo=sim` no CSV. Nada de colar links do Mercado Livre no texto.
4. Português do Brasil, tom de amigo que entende de tecnologia: direto, sem
   exageros ("o melhor do universo"), sem enrolação.
5. Escreva para pessoas primeiro: responda a dúvida real de quem pesquisou,
   com prós e contras honestos e para quem cada produto **não** serve.
6. Não copie textos de outros sites; pesquise e escreva com suas palavras.
7. Nunca edite `.github/`, `site/`, `scripts/` ou `config.yaml` durante a rotina.
   Só o `designer` edita `design/`.
8. Todo post novo ou atualizado passa por `seo` → `vendas` → `designer`
   antes de ser publicado.
10. Ninguém trabalha isolado: leia o plano e o mural antes, responda o que
    resolveu e peça ajuda pelo mural quando outro agente puder destravar uma meta.
9. O repositório é público: nunca escreva valores em R$ de ganhos ou
   comissões em arquivo nenhum.
