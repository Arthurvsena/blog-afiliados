# Tech Barato BR: blog de afiliados automático

Blog de eletrônicos custo-benefício que se atualiza sozinho todo dia.
Uma equipe de 6 agentes do Claude pesquisa, escolhe produtos, gera os links de
afiliado pelo seu Chrome, escreve, otimiza para o Google e atualiza os posts.

**Custo: R$ 0.** O site fica no GitHub Pages (grátis), a automação roda no
GitHub Actions (grátis em repositório público) e a IA usa a **sua assinatura
do Claude** (Pro ou Max), sem cobrança de API.

---

## A equipe

| Agente | O que faz | Quando |
|---|---|---|
| 🧑‍💼 Editor-chefe | Coordena a rotina e chama os outros na ordem | Todo dia, 08:47 |
| 🔎 Pesquisador | Descobre o que as pessoas buscam e enche a fila de pautas | Quando a fila tem menos de 10 |
| 📦 Curador | Pesquisa produtos e, pelo seu Chrome, gera os links de afiliado e cadastra | Toda segunda e quinta, 09:13 (no seu computador) |
| ✍️ Redator | Escreve listas, reviews, comparativos e guias | Todo dia |
| 📈 Estrategista SEO | Revisa cada post e escreve o relatório semanal | Todo dia + toda segunda |
| 🔄 Atualizador | Renova posts com mais de 30 dias | Todo dia |

Veja a equipe trabalhando em **`SEU-SITE/escritorio/`**: um escritório em
pixel art que mostra o que cada agente fez no dia (de noite eles dormem 😴).

---

## Instalação (uns 30 minutos, uma vez só)

### 1. Crie o repositório no GitHub
1. Crie uma conta grátis em <https://github.com>.
2. Clique em **New repository**, dê o nome `blog-afiliados` e marque
   **Public** (precisa ser público para Pages e Actions saírem de graça).
3. Envie todos os arquivos desta pasta. O jeito mais fácil é o
   **GitHub Desktop** (<https://desktop.github.com>): clone o repositório
   vazio, copie os arquivos para dentro dele, faça "Commit" e "Push".
   ⚠️ As pastas `.github` e `.claude` começam com ponto e às vezes ficam
   ocultas. Confira se elas subiram.

### 2. Ajuste o endereço do site
Já configurado para `https://arthurvsena.github.io/blog-afiliados`. Se quiser,
troque o nome do blog em `config.yaml`.

### 3. Libere o GitHub Pages e as permissões
No repositório, abra **Settings**:
- **Pages** → em *Source*, escolha **GitHub Actions**.
- **Actions → General** → em *Workflow permissions*, marque
  **Read and write permissions** e salve.

### 4. Conecte sua assinatura do Claude
1. No seu computador, instale o Claude Code. Veja as instruções em
   <https://code.claude.com/docs/en/setup>.
2. Abra o terminal e rode: `claude setup-token`
3. Faça login com a sua conta e **copie o token** que aparecer.
4. No GitHub: **Settings → Secrets and variables → Actions → New repository
   secret**. Nome: `CLAUDE_CODE_OAUTH_TOKEN`. Valor: o token. Salve.
   (Nunca cole o token em arquivo nenhum do repositório.)

### 5. Links de afiliado: automático pelo seu Chrome
Uma tarefa agendada no app do Claude (segunda e quinta, 09:13) roda **no seu
computador**: abre o Mercado Livre no seu Chrome, escolhe produtos bem avaliados,
gera os links no Gerador de Links e cadastra tudo em `data/produtos.csv`
(skill `.claude/skills/cadastrar-produtos`). Para funcionar, no horário:
- o computador está ligado, com o Chrome aberto e a extensão do Claude ativa;
- você está logado no Mercado Livre nesse Chrome.
Se o Mercado Livre pedir login de novo ou CAPTCHA, a tarefa para e avisa no
escritório (o curador aparece com "PRECISA DE AJUDA"). Faça login e mande
"rodar cadastro de produtos" no chat.

Se quiser cadastrar um produto na mão, acrescente uma linha em
`data/produtos.csv` com o link do Gerador de Links (formato `https://meli.la/...`).

### 6. Rode pela primeira vez
**Actions → Rotina diária do blog → Run workflow.** Leva de 10 a 30 minutos.
Quando terminar, o site estará em `https://arthurvsena.github.io/blog-afiliados/`.
A partir daí ele roda sozinho todo dia às 08:47.

### 7. Rode a estratégia de SEO
**Actions → Estratégia semanal de SEO → Run workflow** para gerar o primeiro
`data/relatorio_seo.md`. Depois disso, roda toda segunda às 07:31.

### 8. Avise o Google que seu site existe
1. Entre em <https://search.google.com/search-console> e adicione a
   propriedade **Prefixo do URL** com o endereço do seu site.
2. Escolha verificar pela **tag HTML**, copie só o código do `content="..."`
   e cole em `google_verificacao` no `config.yaml`. Espere o site
   republicar (uns 2 minutos) e clique em Verificar.
3. Em **Sitemaps**, envie `sitemap.xml`.

---

## Sua rotina (10 minutos por semana)
- **Segunda:** leia `data/relatorio_seo.md` e deixe o computador ligado com o
  Chrome aberto às 09:13 (cadastro de produtos).
- **Quando quiser:** veja o escritório e o `data/diario.md`.
- **Uma vez por semana:** abra 1 ou 2 posts novos e leia. Se algo estiver
  errado, corrija pelo lápis do GitHub. Sua revisão é o que separa um blog
  útil de um blog de spam aos olhos do Google.

## Avisos importantes
- **Limite da assinatura:** cada rotina consome parte do limite de uso do seu
  plano do Claude, o mesmo que você usa no chat. Comece com 1 post por dia
  (`config.yaml`). Se a rotina falhar por limite, ela tenta de novo no dia
  seguinte.
- **Google e conteúdo de IA:** o Google pune sites que publicam muito conteúdo
  feito em massa só para ranquear. Por isso os agentes têm regras rígidas
  (só fatos verificados, nada de inventar testes, prós e contras honestos) e o
  `scripts/verificar.py` barra posts fracos. Mesmo assim, qualidade e sua
  revisão importam mais que quantidade.
- **Paciência:** blogs novos levam de 3 a 6 meses para ganhar tráfego do
  Google. Não desanime no primeiro mês.
- **Domínio próprio (opcional, único custo):** quando o blog crescer, um
  domínio `.com.br` custa cerca de R$ 40/ano e passa mais confiança.

## Problemas comuns
| Sintoma | Solução |
|---|---|
| Rotina falha com erro de autenticação | Gere outro token com `claude setup-token` e atualize o secret |
| Site sem estilo/CSS | Confira o `url_base` no `config.yaml` |
| Só saem guias, nenhuma lista | O cadastro pelo Chrome não rodou: veja o escritório e peça "rodar cadastro de produtos" |
| Erro "action version not found" | Troque `@v6`/`@v4` pela versão mais recente indicada na página da action |

## Estrutura
```
config.yaml              ← suas configurações
data/produtos.csv        ← seus links de afiliado
data/sugestoes_produtos.md, relatorio_seo.md, diario.md, pautas.json, escritorio.json
content/posts/           ← os posts
.claude/agents/          ← a equipe (instruções de cada agente)
.claude/skills/          ← rotina diária e estratégia semanal
.github/workflows/       ← agendamentos
site/                    ← gerador do site, visual e escritório
scripts/verificar.py     ← checagem de qualidade
```
Teste local: `pip install -r requirements.txt && python3 site/build.py`
(o site sai na pasta `_site/`).
