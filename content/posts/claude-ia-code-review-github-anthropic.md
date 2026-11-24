---
titulo: "Claude IA revisa código no GitHub: o que é o Code Review"
slug: claude-ia-code-review-github-anthropic
descricao: "O Code Review do Claude comenta pull requests no GitHub, mas não aprova nem bloqueia sozinho. Veja planos, custo por uso e o que ele não faz."
palavra_chave: "claude ia"
palavras_secundarias: ["claude ia como usar", "claude ia o que faz", "claude ia como funciona"]
editoria: inteligencia-artificial
tipo: noticia
publicado: 2026-11-24 15:00
atualizado: 2026-11-24
fontes:
  - nome: "Claude Code docs: Code Review"
    url: "https://code.claude.com/docs/en/code-review"
  - nome: "Claude Code docs: custos e uso do Code Review"
    url: "https://code.claude.com/docs/en/code-review-costs.md"
  - nome: "InfoQ"
    url: "https://infoq.com/news/2026/11/claude-code-review"
tags: ["Claude", "Anthropic", "Claude Code", "GitHub", "revisão de código"]
capa_frase: "IA que revisa seu código"
compartilhar: "O Claude agora revisa pull requests no GitHub com vários agentes. Só comenta: não aprova nem bloqueia sozinho. Planos Team e Enterprise."
imagem:
  arquivo: claude-ia-code-review-github-anthropic.jpg
  credito: 'Logo: Claude (Wikimedia Commons)'
  licenca: Public domain
  fonte: https://commons.wikimedia.org/wiki/File:Claude_AI_logo.svg
---
O Claude IA tem um serviço de revisão de código para o GitHub, o Code Review. Segundo a documentação oficial da Anthropic, ele analisa cada pull request com vários agentes e deixa comentários nas linhas com problema. Está disponível só para organizações nos planos Team e Enterprise, e quem programa sozinho no plano comum fica de fora.

:::atencao Só comenta
Por si só, a revisão não aprova nem bloqueia o pull request. Ela comenta e pronto.
:::

## Como o Claude IA revisa o código no Code Review

Pull request é a proposta de mudança no código que alguém pede para a equipe revisar antes de entrar no projeto. É essa etapa que o Claude assume como primeiro leitor.

De acordo com a documentação, a revisão roda na infraestrutura da Anthropic em quatro etapas:

- vários agentes leem o diff (o trecho alterado) e o código ao redor, em paralelo;
- uma etapa de verificação confere os achados contra o código e descarta falsos positivos;
- os problemas restantes são deduplicados e ordenados por gravidade;
- o resultado é publicado no pull request.

No GitHub, aparecem comentários inline, um resumo e um check run chamado "Claude Code Review". Na prática, é um colega que lê tudo antes do humano e já aponta onde olhar.

Por padrão, o foco é correção: bugs que quebrariam a produção, e não preferência de formatação. Dá para ajustar o que ele sinaliza com arquivos `REVIEW.md` e `CLAUDE.md` no repositório.

## Quem pode usar e quanto custa

A documentação lista Team e Enterprise, com repositórios no GitHub (incluindo GitHub Enterprise Server). Um Owner da organização precisa ativar o serviço e instalar o app do Claude no GitHub.

Não há preço fixo por revisão. A cobrança é por uso de tokens, via créditos de uso, separada do que o plano já inclui. O valor muda com o nível escolhido (Quick, Standard ou Deep), o tamanho da mudança e quantas vezes a revisão roda. Dá para definir um limite mensal de gasto.

Vale lembrar o que a documentação deixa de fora: organizações com Zero Data Retention ou configuração HIPAA não têm acesso. A documentação não informa preço em reais nem disponibilidade específica para o Brasil.

## O que ele não faz

A própria Anthropic avisa que a ferramenta pode deixar passar bugs e falhas de segurança, e que uma revisão sem achados não prova que o código está limpo ou seguro. Ela também lê o código sem compilar nem executar.

:::dica Sem Team ou Enterprise
O comando `/code-review` roda na sua sessão do Claude Code em qualquer plano.
:::

## O contexto: a Anthropic revisa com IA o próprio código

O InfoQ publicou em 15 de novembro um resumo de como o time do Claude Code revisa o próprio código, com base em texto da Anthropic. Segundo a reportagem, os pull requests mesclados no repositório mais que dobraram entre junho e setembro. A fatia aprovada após uma rodada de revisão e correção subiu de 65% para 78%.

A abordagem combina testes automáticos, revisão por IA e aprovação humana proporcional ao risco. Mudanças em workflows de CI sempre passam por uma pessoa. Esses números são da própria Anthropic, sobre o uso interno, e não medem o produto na sua empresa.

## O que fica

Vale um piloto pequeno, com limite de gasto definido, se sua empresa já paga Team ou Enterprise. Para quem programa por conta própria, o `/code-review` local é o caminho. Se o texto sobre o Claude em geral for o que você procura, veja [como usar o Claude IA](/posts/claude-ia-como-usar-como-funciona/), que explica o que o Claude faz e como funciona. Para o lado empresarial, leia também sobre o [IPO da Anthropic](/posts/anthropic-ipo-nasdaq-ant-s-1-claude/).

:::veredito
Boa segunda leitura, não substituto do revisor humano: ela só opina, e a decisão continua com a equipe.
:::
