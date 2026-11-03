---
name: canal-diario
description: Rotina diária do departamento de vídeo. PARTE A (GitHub Actions, workflow videos.yml) escolhe os posts, escreve os roteiros, narra com a voz do Google (Chirp 3 HD pt-BR) e monta 2 Shorts e 1 vídeo longo com motion no Remotion, publicando os arquivos num Release do GitHub. PARTE B (tarefa agendada no computador do dono) baixa os vídeos do Release e publica no canal Nexus Tech do YouTube pelo Chrome.
---
> **Execução sem supervisão:** chame subagentes com `run_in_background: false`
> e espere cada resposta. Nunca use ScheduleWakeup/Monitor e só termine depois
> do último passo da parte que você está executando.

# Canal Nexus Tech: vídeos do dia

Antes de tudo: leia `CLAUDE.md`, `data/estrategia.md`, `data/relatorio_diario.md`
(se existir) e `python3 scripts/mural.py listar`.

# PARTE A: produção (GitHub Actions)

As ferramentas já vêm instaladas pelo workflow (ffmpeg, Remotion em `video/`,
vozes). A voz é a de `config.yaml > video.voz` (Google Chirp 3 HD, com a
chave no segredo `GOOGLE_TTS_KEY`); sem a chave, o script usa sozinho a voz
grátis Kokoro.

## A1. Pauta
Chame o `produtor` em **modo pauta do dia**. Ele devolve até 2 Shorts e 1 longo.

## A2. Roteiros
Para cada vídeo: `roteirista` (com o tipo e o post) e depois `produtor` em
**modo revisão** com o caminho do roteiro.

## A3. Montagem (um vídeo por vez)
1. `python3 scripts/video_motion.py data/videos/roteiros/SLUG.json --saida _videos --manter`
   Leva de 3 a 6 min por Short e de 10 a 25 min por vídeo longo. O resultado
   diz o arquivo, o tamanho (< 10 MB), a duração, a voz usada, a capa (longos)
   e o `.txt` com a descrição pronta.
2. **Confira as fotos**: abra (Read) as imagens baixadas em
   `video/public/run/SLUG/c*.jpg`. Só valem fotos oficiais do próprio produto
   ou da notícia. Se alguma não mostrar exatamente o que a fala diz (foto de
   app, de exemplo de câmera, pessoas, logo de outra marca), troque a cena por
   uma cena gráfica (`numero`, `info`, `data`, `comparativo`) e monte de novo.
3. Olhe 3 quadros do vídeo final (`ffmpeg -ss T -i ARQ -frames:v 1 /tmp/q.png`
   e Read) para conferir legenda e imagem.
4. Se o Remotion falhar duas vezes, use a reserva sem motion:
   `python3 scripts/video.py data/videos/roteiros/SLUG.json --saida _videos`.
5. Grave em `_videos/SLUG.json` um resumo para a publicação:
   `{"slug", "tipo", "post", "titulo", "hashtags", "voz", "segundos"}` (copie do
   roteiro e do resultado do script).

## A4. Escritório e mural
Em `data/escritorio.json`, atualize `produtor` e `roteirista` (status `ok`,
`ocioso` ou `erro` e uma frase em 1ª pessoa) e acrescente no `historico`.
Responda no mural o que foi resolvido. O workflow publica `_videos/` num
Release `videos-AAAA-MM-DD` e faz o commit dos roteiros.

# PARTE B: publicação (tarefa agendada no computador do dono)

## B1. Baixe os vídeos do dia
`gh release download videos-AAAA-MM-DD --repo Arthurvsena/blog-afiliados --dir /mnt/user-data/outputs/videos`
(data de hoje no horário de Brasília). Se não existir Release de hoje, avise o
dono que a produção não rodou e termine. Pule vídeos cujo `slug` já esteja em
`data/videos.json` com status `publicado`.

## B2. Publique no YouTube (Chrome do dono)
Carregue a skill `chrome-browser`. Trabalhe em aba nova e feche no fim.
Regras: não faça login, não digite senha, não resolva CAPTCHA, não aceite
termos, não mude configurações do canal. Se o YouTube Studio pedir login,
verificação de telefone ou não mostrar o canal **Nexus Tech IA**, pare a
publicação, registre os vídeos como não publicados e avise o dono no fim.

Para cada vídeo:
1. Abra `https://studio.youtube.com/channel/UCFFNejQflJHQNj6AAX026LQ` (canal
   **Nexus Tech IA**, @TechNexusIA, da conta nexus.latech2026@gmail.com). Se
   abrir outro canal (ex.: Art Play), troque pelo avatar > **Mudar de conta** >
   **Nexus Tech IA**. Confira o nome no menu à esquerda antes de enviar.
   Clique em **Criar** > **Enviar vídeos**.
2. Ache o `input[type=file]` com `find`/`read_page` e use
   `mcp__claude-in-chrome__file_upload` com o caminho do `.mp4` (não clique no
   botão de escolher arquivo: isso abre uma janela que você não controla).
3. **Detalhes**: título = `titulo`; descrição = conteúdo do `.txt`; miniatura =
   a `-capa.jpg` (só vídeos longos e só se o botão de miniatura estiver
   liberado); categoria, idioma e tags padrão já vêm configurados no canal; público: **"Não, não é conteúdo para crianças"**. Em "Mostrar
   mais": **Conteúdo alterado: Não** (narração sintética não é conteúdo
   realista alterado); tags = `hashtags`.
4. Avance até **Visibilidade**, escolha **Público** e clique em **Publicar**.
   Copie o link do vídeo que aparece no fim.
5. Nos vídeos longos, abra o vídeo e fixe um comentário com o link do post
   (o mesmo da descrição). Se não puder ser fixado, siga.

## B3. Registro
Acrescente cada vídeo em `data/videos.json` (crie se não existir):
```json
{"videos": [{"data": "AAAA-MM-DD", "tipo": "short", "slug": "...", "post": "slug-do-post",
             "titulo": "...", "url": "https://youtu.be/...", "voz": "google:Charon",
             "segundos": 0, "status": "publicado|pronto (não publicado: motivo)"}]}
```
Faça commit em main ("Canal AAAA-MM-DD"), `git pull --rebase origin main` e
push (sem os arquivos de vídeo). Responda ao dono com os vídeos publicados
(título e link) e qualquer problema.
