# Manual do YouTube: canal Nexus Tech IA

> Todo agente que mexe no canal (`tendencias`, `produtor`, `roteirista`, `analista`)
> lê este manual antes de trabalhar. Ele junta o relatório de estratégia de
> 04/11/2026 com o que já funciona no nosso processo. Vale junto com
> `editorial/canal.md` (linha editorial) e `CLAUDE.md` (regras do projeto).

## 0. Regras de ouro
1. **Nunca reaproveitar vídeo de outro canal.** Nada de baixar, cortar, traduzir
   ou dublar vídeo de terceiros. O YouTube tira a monetização do canal inteiro
   por "conteúdo reutilizado", mesmo com permissão.
2. **Copiar o padrão, nunca o conteúdo.** Dos canais de fora vem estrutura,
   ritmo e tipo de gancho. Roteiro, imagens e narração são sempre nossos.
3. **Nenhum vídeo igual ao anterior.** Variar gancho, abertura, ângulo e cenas.
   Vídeo-modelo com só o produto trocado é "conteúdo inautêntico" e é punido.
4. **Todo número com fonte** registrada no roteiro (`fontes` e `fonte` da cena).
   Datas e números de história conferidos em 2 fontes.
5. **Conteúdo primeiro, venda como consequência.** Produto só quando ajuda.
6. **Sem imagem gerada por IA.** Para conceito sem foto, use gráfico nosso.

### Imagens permitidas
- Imagens oficiais de divulgação (press kit, página do produto, do jogo, da
  empresa), sempre com crédito ("Divulgação/Nintendo"). Ache com
  `python3 scripts/midia.py imagens URL_OFICIAL --baixar /tmp/cand`.
- Print de matéria com o trecho grifado (cena `manchete`, direito de citação,
  Lei 9.610/98, art. 46, III), com o nome do veículo na tela.
- Fotos com licença livre (Wikimedia Commons com CC0/CC BY/CC BY-SA).
- Gráficos, listas, linhas do tempo e números animados feitos por nós.
- Logo de empresa **só para identificar de quem se fala**, nunca como enfeite.

### Trechos de VÍDEO (obrigatórios: só foto e animação fazem a pessoa pular)
Todo vídeo tem trechos em movimento: **pelo menos 1 por Short e 4 por longo**.
Fontes permitidas, nesta ordem:
1. **Vídeo oficial** de quem é dono do assunto: trailer e gameplay oficial do
   jogo (página da Steam, site do jogo/publisher), vídeo de divulgação do
   fabricante (página do produto, press kit). Ache com
   `python3 scripts/midia.py videos URL_OFICIAL` e use
   `"video:URL|Vídeo: Rockstar Games|SEGUNDO_INICIAL"` (o script corta 12 s,
   sem som, com o crédito na tela). Trecho curto, ilustrando o que a narração
   comenta: é citação (Lei 9.610/98, art. 46, III), não reaproveitamento.
2. **Gravação de tela nossa**: `"tela:URL"` abre a página e grava 12 s rolando
   (página oficial do produto, do jogo, do serviço, o site do tutorial).
3. **Banco grátis** (Pexels): `"estoque:termos em inglês"` para cenas genéricas
   (pessoa usando celular, cidade, loja). Só funciona com o segredo `PEXELS_API_KEY`.
**Nunca**: vídeo de outro canal/criador do YouTube, TV, filme ou série, e
nunca baixar nada do YouTube. Isso gera reivindicação de direitos, "conteúdo
reutilizado" e perda da monetização do canal inteiro. Vídeo grátis para
assistir não é grátis para usar.

### Proibido
Trecho de vídeo de terceiros, emissoras ou filmes; música comercial (a trilha é
gerada pelo nosso script, `scripts/trilha.py`); imagem de IA; personagem de
terceiros como decoração fora de um assunto sobre ele.

## 1. Identidade (reconhecível em 2 segundos)
| Elemento | Padrão Nexus (já no processo de vídeo) |
|---|---|
| Cores | Fundo escuro + violeta (#7C5CFF), iguais ao site |
| Fonte | Inter Tight grossa em títulos e legendas |
| Destaque | Palavra falada em violeta na legenda |
| Selo | Nome do quadro no canto superior direito ("Nexus em 60s", "Histórias Tech #3") |
| Vinheta | 2,5 s, só no "Lá Fora, Aqui", sempre DEPOIS do gancho (automática) |
| Fonte da informação | Barra discreta "Fonte: X, 05/11" (campo `fonte` da cena) |
| Trilha | Gerada pelo script por quadro, uma diferente por vídeo, ~22 dB abaixo da voz |
| Voz | Fenrir ou Orus (teste A/B da Luisa em `data/videos/vozes.json`); ritmo por quadro |
| Inscrição | Botão animado "Inscrever-se" no fim de todo vídeo (automático) |

## 2. Pesquisa: "Termômetro Gringo" (agente `tendencias`)
Além do Brasil (Google Trends BR, YouTube BR, portais), olhar todo dia:
- **EUA/Global:** The Verge, TechCrunch, Engadget, Ars Technica, GSMArena,
  Hacker News, Reddit (r/technology, r/gadgets, r/Android, r/apple).
- **China/Ásia:** GSMArena, Gizmochina, Android Authority (Xiaomi, Huawei, Honor, Oppo, Vivo).
- **Europa:** TechRadar, Xataka, Frandroid.

Uma pauta de fora entra se cumprir **3 de 4**: (1) apareceu em 2+ fontes de
fora nos últimos 7 dias; (2) importa para o brasileiro (dá para comprar, vai
chegar ou afeta o dia a dia); (3) está pouco coberta em português (busque no
YouTube BR); (4) puxa uma página do blog (post, guia ou ficha de produto).
Notícia quente do Brasil continua valendo para o "Nexus em 60s".

**Biblioteca de Padrões (1ª segunda-feira do mês, `tendencias`):** os vídeos
mais vistos do mês de Two Minute Papers, Fireship, ColdFusion, Kurzgesagt e
Mrwhosetheboss/MKBHD. Registrar só o padrão (título, duração, tipo de gancho,
blocos, estilo da miniatura) em `data/videos/padroes.md`. Nunca o roteiro.

### vidIQ: provar a demanda antes de gravar
Domingo e quarta à noite uma tarefa usa o vidIQ (conectado à conta do Arthur;
plano grátis = 150 créditos por mês, 5 por consulta, ~30 consultas) e grava
`data/vidiq.json`: termos com volume de busca, concorrência e nota, e vídeos de
tecnologia em português que estão explodindo. Longos (tutorial e Lá Fora) só
saem de termo com demanda medida; Shorts preferem assuntos que já provaram
público. Os agentes do GitHub não acessam o vidIQ: só leem esse arquivo.

## 3. Grade da semana (`config.yaml > video.grade`)
| Dia | Vídeos |
|---|---|
| Segunda a sexta | 1 "Nexus em 60s" (12:00) |
| Terça | + 1 "Nexus Ensina" (tutorial, 19:00) |
| Quinta | + 1 "Lá Fora, Aqui" (19:00) |
| Sábado e domingo | 1 "Histórias Tech" (12:00) |
São 9 vídeos por semana: os Shorts trazem gente nova, os longos dão o motivo para se inscrever.

## 4. "Nexus em 60s": Short de notícia (`"quadro": "60s"`)
Inspiração: Fireship. 9:16, 30 a 60 s (75 a 165 palavras), voz ~175 ppm.
| Tempo | Bloco |
|---|---|
| 0–2 s | **Gancho**: imagem forte + a frase mais forte na tela. Nada de "olá". |
| 2–40 s | **A notícia**: uma só. O que é, o detalhe mais surpreendente, por que importa no Brasil. Prova com `manchete` ou `numero`. |
| 40–55 s | **Comentário Nexus**: uma frase de humor seco, nunca forçado. |
| final | **Loop**: a última frase emenda na primeira. Link da bio só se houver post. |
Regras: troca visual a cada 1,5 a 3 s; legenda palavra por palavra (automática);
nada de "se inscreve" falado (o botão aparece sozinho no fim).

## 5. "Histórias Tech": Short de mini-documentário (`"quadro": "historias"`, `"numero": N`)
Inspiração: ColdFusion. 9:16, 60 a 90 s (140 a 225 palavras), voz ~145 ppm, série numerada.
| Tempo | Ato |
|---|---|
| 0–3 s | **O momento dramático**: começa no ponto mais forte. |
| 3–30 s | **Ato 1, o auge**: ano grande na tela (`data` ou `linha`). |
| 30–65 s | **Ato 2, a virada**: o erro, a decisão ou o concorrente. Prova (`barras`, `numero`, `citacao`). |
| 65–90 s | **Ato 3, a lição**: o que aconteceu e o que ensina. Fecha com pergunta. |
Regras: troca visual a cada 3 a 5 s; legenda em frases inteiras e trilha
cinematográfica (automáticas); fotos de arquivo com licença livre ou de imprensa
oficial; **toda data e todo número em 2 fontes**. Temas que não envelhecem
(Nokia, BlackBerry, Kodak, Orkut, Atari, Nintendo vs. Sega...). O número do
episódio é o maior `numero` em `data/videos.json` + 1.

## 6. "Lá Fora, Aqui": vídeo longo (`"quadro": "lafora"`, `"tipo": "longo"`)
Inspiração: Two Minute Papers. 16:9, 5 a 8 min (700 a 1.300 palavras), voz ~155 ppm.
| Tempo | Bloco (`capitulo` na 1ª cena de cada um) |
|---|---|
| 0:00–0:15 | **Gancho**: a novidade + a pergunta do brasileiro ("chega aqui? por quanto?"). Vinheta entra depois, sozinha. |
| 0:15–0:45 | **Por que bombou**: onde e com que números, com fonte na tela. |
| 0:45–3:00 | **Como funciona**: o resultado primeiro, depois o porquê; 1 ou 2 comparações do dia a dia. |
| 3:00–4:30 | **E no Brasil?**: chega ou não; preço lá fora convertido com a cotação e a data; regra de importação vigente com fonte e data. Sempre "estimativa", nunca "vai custar R$ X". |
| 4:30–6:00 | **Alternativas que já dá pra comprar**: até 3, do catálogo (`produto`), com prós e contras e para quem não serve. |
| 6:00–fim | **Veredito Nexus + CTA**: opinião clara baseada nas fontes (nunca "eu testei"), pergunta para os comentários, pedido para se inscrever e "link na descrição". |
Regras: troca visual a cada 4 a 6 s, nenhuma tela parada por mais de 8 s; todo
número importante escrito na tela; comparações em `barras`/`comparativo`;
capítulos na descrição (o script calcula os tempos reais). Miniatura: um
elemento principal grande, fundo escuro com brilho violeta, no máximo 3 a 4
palavras que não repetem o título.

## 6b. "Nexus Ensina": tutorial longo (`"quadro": "tutorial"`, `"tipo": "longo"`)
Por quê: tutorial é o que as pessoas **procuram** no YouTube e não envelhece;
é o vídeo que faz alguém se inscrever ("esse canal resolve meu problema").
16:9, 4 a 8 min (600 a 1.300 palavras), voz calma ~150 ppm, toda terça.
**Tema:** uma dúvida real com busca (autocompletar do YouTube/Google com
"como..."): configurar, resolver, economizar, se proteger. Ex.: "como liberar
espaço no celular", "como saber se o celular é original pelo IMEI", "como
transferir o WhatsApp para outro celular", "como ver se um site é golpe antes
de comprar". Prefira o que dá para MOSTRAR com gravação de tela (sites e
serviços web) e com páginas oficiais de ajuda (Apple, Samsung, Google,
Microsoft, Anatel, gov.br), sempre conferindo os passos na página oficial.
| Bloco | O que acontece |
|---|---|
| 0:00–0:20 | **O resultado primeiro**: o que a pessoa vai conseguir no fim e em quanto tempo. |
| 0:20–0:50 | **O que você precisa** (aparelho, versão, conta) e para quem **não** serve. |
| passos | Cenas `passo` (selo "PASSO N" + a ação curta em `tela`), uma ação por passo, com gravação de tela (`tela:`) ou imagem oficial da página de ajuda. Diga onde tocar e o que deve aparecer. |
| erros | **Se não funcionou**: os 2 ou 3 problemas mais comuns e a saída. |
| fim | Resumo em `lista`, pergunta ("que tutorial você quer no próximo?"), pedido para se inscrever e "link na descrição". |
Títulos: "Como [fazer X] no [aparelho/app] (passo a passo 2026)". Capa: o
resultado ("CELULAR LIVRE", "DESCOBRI O GOLPE").

## 7. Embalagem: títulos, descrições e capas
**Título:** até 60 caracteres (mais ` #shorts` nos Shorts), palavra-chave (campo
`palavra_chave`, o termo que o brasileiro busca) no começo, um dado concreto e
uma curiosidade que o vídeo responde. O roteirista escreve 3 opções e escolhe.
**Descrição** (gerada pelo script): 1ª frase com a palavra-chave e a resposta;
link do blog; frase do quadro com link de inscrição; produtos (se houver);
capítulos (longo); fontes e créditos; 3 a 5 hashtags, a mais buscada primeiro.
**Capas (longo):** o script gera 2 versões, A (texto à esquerda, foto com
brilho violeta) e B (foto inteira, texto grande com destaque amarelo), com o
`capa_texto` e o `capa_texto_b`: até 4 palavras que completam o título. Elas
vão para o "Testar e comparar" do YouTube Studio, que escolhe a vencedora.
**Shorts:** a "capa" é o primeiro segundo: gancho forte com texto grande.
Fórmulas:
Fórmulas: "[Produto] chegou: vale a pena no Brasil?", "Por que [empresa] [fez X]",
"O [produto] que viralizou na China (e quanto custaria aqui)",
"Como a [empresa] [subiu/caiu]". Nunca prometer o que o vídeo não entrega.

## 8. Métricas (Luisa, `analista`)
Comparar cada vídeo com a média dos últimos 10 **do mesmo quadro**.
| Quadro | O que olhar | Alerta |
|---|---|---|
| Nexus em 60s | % que continuou assistindo, views em 24 h, inscritos | muita gente arrastando: os 2 primeiros segundos falharam |
| Histórias Tech | retenção até o fim, comentários | queda no meio: Ato 2 lento |
| Lá Fora, Aqui | retenção aos 30 s, retenção média, CTR, cliques no blog | queda nos primeiros 15 s: gancho falhou |
Toda segunda: 2 melhores e 2 piores por quadro, o que mudou entre eles, **uma
variável por vez** na semana seguinte e o aprendizado na seção 10.
Miniaturas: a Luisa só lê o resultado do "Testar e comparar" do YouTube Studio.

## 9. Checklist antes de publicar (o `produtor` confere)
- [ ] `python3 scripts/video_motion.py ROTEIRO --checar` deu OK
- [ ] Roteiro original; todo número com fonte; nada de vídeo de terceiros
- [ ] Imagens oficiais ou livres, com crédito; nenhuma imagem de IA
- [ ] Gancho e abertura diferentes dos últimos 5 vídeos do mesmo quadro
- [ ] Short termina em loop; longo pede inscrição e manda para a descrição
- [ ] Link do post/guia do blog na descrição quando houver

## 10. Aprendizados (a Luisa preenche toda segunda)
> Começa vazio. Ex.: "Ganchos com pergunta de preço retêm mais que ganchos com especificação."
