# Tech Barato BR: portal de tecnologia automático

Blog de eletrônicos custo-benefício que se atualiza sozinho todo dia.
Uma equipe de 9 agentes do Claude pesquisa, escolhe produtos, gera os links de
afiliado pelo seu Chrome, escreve, otimiza para o Google e atualiza os posts.

**Custo: R$ 0.** O site fica no GitHub Pages (grátis), a automação roda no
GitHub Actions (grátis em repositório público) e a IA usa a **sua assinatura
do Claude** (Pro ou Max), sem cobrança de API.

---

## O site
Portal de tecnologia com notícias diárias de **celulares, games, IA e
tecnologia**, análises, tutoriais e um **guia de compras** com links de oferta
do Mercado Livre. Todos os textos são assinados por **Rafa Lins**, a voz do
site (pseudônimo, explicado na página Sobre), seguindo `editorial/voz.md` e
`editorial/manual.md`. Receita: anúncios do Google AdSense + afiliados.

## Como a equipe trabalha junta
- **4 metas, nesta ordem:** vendas (pedidos), cliques (nos links), acessos
  (visitas) e engajamento (páginas por visita).
- **Reunião toda segunda (11:31):** o Editor-chefe ouve o Analista (números),
  o SEO (buscas), o Vendas (onde perdemos cliques), o Curador (produtos) e as
  propostas dos outros, e fecha no máximo 4 apostas em `data/estrategia.md`.
- **Mural (`data/mural.json`):** os agentes trocam pedidos entre si ("preciso de
  um produto X", "este post tem visitas e nenhum clique") e respondem o que
  resolvem. Toda rotina começa lendo o plano e o mural.
- Você acompanha o plano e os bilhetes no escritório.

## A equipe

| Agente | O que faz | Quando |
|---|---|---|
| 🧑‍💼 Editor-chefe | Coordena a rotina e chama os outros na ordem | Todo dia, 08:47 |
| 🔎 Pesquisador | Descobre o que as pessoas buscam e enche a fila de pautas | Quando a fila tem menos de 10 |
| 📦 Curador | Pesquisa produtos e, pelo seu Chrome, gera os links de afiliado e cadastra | Toda segunda e quinta, 09:13 (no seu computador) |
| ✍️ Redator | Escreve listas, reviews, comparativos e guias | Todo dia |
| 💰 Vendas | Garante chamadas de compra em todo post (links no texto, botões na tabela, "Qual comprar?") e ajusta os posts que recebem visitas mas não geram cliques | Todo post + toda segunda |
| 📊 Analista | Lê visitas, cliques no Mercado Livre, pedidos e Google, e entrega o relatório com ações para cada agente | Toda segunda, 09:13 (no seu computador) |
| 🎨 Designer | Dono da marca (`design/marca.yaml`, logo, cores) e revisor visual de todo post: tabelas, prós e contras, veredito e capa | Todo post + toda segunda |
| 📈 Estrategista SEO | Revisa cada post e escreve o relatório semanal | Todo dia + toda segunda |
| 🔄 Atualizador | Renova posts com mais de 30 dias | Todo dia |

Veja a equipe trabalhando no **escritório**: um escritório em pixel art que
mostra o que cada agente fez no dia (de noite eles dormem 😴). Ele é **privado**:
fica em `https://arthurvsena.github.io/blog-afiliados/escritorio/`, sem link no
site, e abre só com a sua senha (secret `ESCRITORIO_SENHA`, passo 10). Salve o
endereço nos favoritos.
O guia da marca fica em **`SEU-SITE/marca/`**.

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

### 9. Contador de visitas (Cloudflare Web Analytics, grátis e sem cookies)
1. Crie uma conta grátis em <https://dash.cloudflare.com/sign-up>.
2. Vá em **Analytics & Logs → Web Analytics → Add a site**, digite
   `arthurvsena.github.io` e escolha a opção de **JS snippet** (sem mudar DNS).
3. Copie só o valor de `"token"` do código que aparecer e cole em
   `cloudflare_token` no `config.yaml`.

### 10. Senha do escritório
No GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
Nome: `ESCRITORIO_SENHA`. Valor: uma senha só sua. A página do escritório é
publicada criptografada com ela; sem o secret, o escritório não é publicado.
No navegador, marque "Lembrar neste aparelho" para não digitar sempre.

**Limite do repositório público:** o código e os arquivos de `data/` ficam
visíveis no GitHub. Por isso nenhum agente grava valores em R$ de ganhos:
eles aparecem só na mensagem que o analista manda para você.

### 11. Domínio próprio (necessário para os anúncios do Google)
O Google AdSense não aprova sites em endereços do tipo `usuario.github.io`:
ele exige um domínio seu. Um `.com.br` custa cerca de R$ 40 por ano.
1. Registre o domínio (ex.: em <https://registro.br>).
2. No painel do domínio, crie os registros DNS do GitHub Pages: quatro
   registros `A` para `185.199.108.153`, `185.199.109.153`, `185.199.110.153`
   e `185.199.111.153`, e um `CNAME` de `www` para `arthurvsena.github.io`.
3. Preencha `dominio` no `config.yaml` (ex.: `techbaratobr.com.br`).
4. No GitHub: **Settings → Pages → Custom domain**, digite o domínio e marque
   **Enforce HTTPS** quando liberar.
5. Adicione o domínio novo no Search Console e no Cloudflare Web Analytics.

### 12. Google AdSense
1. Com o domínio no ar e pelo menos 20 a 30 posts publicados, cadastre-se em
   <https://adsense.google.com> com o endereço do domínio.
2. Copie o código do editor (`ca-pub-...`) para `anuncios.adsense_cliente` no
   `config.yaml`. O site passa a carregar o AdSense e publica o `ads.txt` sozinho.
3. Peça a revisão do site no AdSense e espere a aprovação (costuma levar de
   alguns dias a algumas semanas).
4. Depois de aprovado, ative os **anúncios automáticos** ou crie blocos em
   **Anúncios → Por bloco de anúncios** e cole os números em `anuncios.slots`
   (topo, artigo, lateral, lista).
5. Em **Privacidade e mensagens**, ative a mensagem de consentimento de cookies.

## Sua rotina (10 minutos por semana)
- **Segunda:** deixe o computador ligado com o Chrome aberto às 09:13 (métricas
  e cadastro de produtos). Depois leia `data/relatorio_metricas.md`.
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
