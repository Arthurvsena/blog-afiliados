# Blog de afiliados "Tech Barato BR": regras do projeto

Este repositório é um blog estático de reviews e comparativos de eletrônicos
custo-benefício, monetizado pelo programa de afiliados do Mercado Livre.
Os agentes em `.claude/agents/` mantêm o blog todos os dias.

## Estrutura
- `config.yaml`: nome do site, subnichos, quantos posts por dia.
- `data/produtos.csv`: catálogo de produtos com link de afiliado. Links só
  entram pela skill `cadastrar-produtos` (que gera no Gerador de Links do
  Mercado Livre pelo Chrome do dono) ou pelo próprio dono. Nenhum agente
  inventa ou altera um `link_afiliado`.
- `data/pautas.json`: fila de pautas (ideias de posts) criada pelo pesquisador.
- `data/sugestoes_produtos.md`: produtos que o curador recomenda o dono cadastrar.
- `data/relatorio_seo.md`: relatório semanal do estrategista de SEO.
- `content/posts/*.md`: os posts (Markdown com frontmatter YAML).
- `design/marca.yaml`: identidade visual (cores, fontes, logo, regras), mantida
  pelo agente `designer`. O site lê as cores e fontes daqui.
- `scripts/verificar.py`: checagem de qualidade. Rode antes de terminar.
- `site/build.py`: gera o site em `_site/` (o GitHub Actions faz isso sozinho).

## Formato de um post
```markdown
---
titulo: "Os 5 melhores fones Bluetooth até R$ 200 em 2026"
slug: melhores-fones-bluetooth-ate-200
descricao: "Até 155 caracteres, com a palavra-chave e um motivo para clicar."
palavra_chave: "melhor fone bluetooth até 200 reais"
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

Componentes visuais (o designer aplica; cada bloco fecha com ::: sozinho):
:::pros            :::contras          :::veredito
- ponto            - ponto             Uma frase forte.
:::                :::                 :::
:::dica            :::atencao   (título opcional na mesma linha: ":::dica Antes de comprar")
```

## Regras inegociáveis (valem para todos os agentes)
1. **Nunca invente fatos.** Especificações, preços, notas e números de
   avaliações vêm de `data/produtos.csv` ou de páginas que você abriu com
   WebFetch/WebSearch nesta execução. Se não tiver certeza, não escreva.
   Não afirme ter testado um produto pessoalmente.
2. **Preço não vai no texto.** Preços mudam. Diga "veja o preço atual" e deixe
   o card mostrar a faixa de preço do CSV.
3. **Links de compra só via `{{produto:ID}}`**, com IDs de produtos com
   `ativo=sim` no CSV. Nada de colar links do Mercado Livre no texto.
4. Português do Brasil, tom de amigo que entende de tecnologia: direto, sem
   exageros ("o melhor do universo"), sem enrolação.
5. Escreva para pessoas primeiro: responda a dúvida real de quem pesquisou,
   com prós e contras honestos e para quem cada produto **não** serve.
6. Não copie textos de outros sites; pesquise e escreva com suas palavras.
7. Nunca edite `.github/`, `site/`, `scripts/` ou `config.yaml` durante a rotina.
   Só o `designer` edita `design/`.
8. Todo post novo ou atualizado passa pelo `designer` antes de ser publicado.
