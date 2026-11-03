---
name: canal-diario
description: Rotina diária do departamento de vídeo. Escolhe os posts do dia, gera roteiros, narra (ElevenLabs se houver crédito, senão voz grátis), monta 2 Shorts e 1 vídeo longo e publica no canal Nexus Tech do YouTube pelo Chrome do dono. Roda na tarefa agendada do fim da tarde, no computador do dono.
---
> **Execução sem supervisão:** chame subagentes com `run_in_background: false`
> e espere cada resposta. Nunca use ScheduleWakeup/Monitor e só termine depois
> do último passo.

# Canal Nexus Tech: vídeos do dia

Antes de tudo: leia `CLAUDE.md`, `data/estrategia.md`, `data/relatorio_diario.md`
(se existir) e `python3 scripts/mural.py listar`. Instale a voz grátis com
`pip install --break-system-packages -q piper-tts`, `python3 scripts/video.py --voz`
e `cd video && npm install --no-audit --no-fund` (Remotion, para o motion).

## 1. Pauta
Chame o `produtor` em **modo pauta do dia**. Ele devolve até 2 Shorts e 1 longo.

## 2. Roteiros
Para cada vídeo: `roteirista` (com o tipo e o post) e depois `produtor` em
**modo revisão** com o caminho do roteiro.

## 3. Narração (um vídeo por vez)
1. **Tente o ElevenLabs uma vez** por vídeo: chame
   `mcp__ElevenLabs__creative_generate_speech` com o texto de
   `python3 scripts/video_motion.py ROTEIRO --fala` (já com os números por extenso), `model_id: "eleven_multilingual_v2"`,
   `voice_id: "cCd5pjwRv69hyjEKrf0o"` (Renan Matheus, pt-BR),
   `generations_count: 1`. Acompanhe com `creative_get_flow_run_status` até
   terminar. Se gerar, baixe o áudio da URL do resultado para
   `/tmp/narracao-SLUG.mp3` (curl) e confira com `ffprobe`.
2. **Se qualquer coisa falhar** (sem crédito, ocupado, erro, download
   bloqueado), não tente de novo: use a voz grátis (sem `--audio`). Se o
   ElevenLabs disser que não há crédito, use a voz grátis em todos os vídeos
   restantes do dia.
3. Monte o vídeo com motion (Remotion):
   `python3 scripts/video_motion.py data/videos/roteiros/SLUG.json --saida /mnt/user-data/outputs/videos --manter [--audio /tmp/narracao-SLUG.mp3]`
   Leva de 4 a 6 min por Short e de 15 a 30 min por vídeo longo. Se o
   Remotion falhar duas vezes, use a reserva sem motion:
   `python3 scripts/video.py data/videos/roteiros/SLUG.json --saida /mnt/user-data/outputs/videos [--audio ...]`
   O resultado diz o arquivo, o tamanho (tem de ser < 10 MB), a duração, a
   voz usada, a capa (longos) e o `.txt` com a descrição pronta.
4. **Confira as fotos**: abra (Read) as imagens baixadas em
   `video/public/run/SLUG/c*.jpg`. Se alguma não tiver a ver com o assunto,
   mostrar logo de outra marca, pessoa reconhecível ou texto estranho, troque
   a referência no roteiro (outra `busca:` ou uma foto já usada em outra cena)
   e monte de novo. Depois olhe 3 quadros do vídeo final
   (`ffmpeg -ss T -i ARQ -frames:v 1 /tmp/q.png` e Read) para ver legenda e foto.
   Apague `video/public/run/SLUG` no fim.

## 4. Publicar no YouTube (Chrome do dono)
Carregue a skill `chrome-browser`. Trabalhe em aba nova e feche no fim.
Regras: não faça login, não digite senha, não resolva CAPTCHA, não aceite
termos, não mude configurações do canal. Se o YouTube Studio pedir login,
verificação de telefone ou não mostrar o canal **Nexus Tech**, pare a
publicação, guarde os vídeos e avise o dono no fim.

Para cada vídeo:
1. Abra `https://studio.youtube.com` e confira no canto superior que o canal
   é o **Nexus Tech**. Clique em **Criar** > **Enviar vídeos**.
2. Ache o `input[type=file]` com `find`/`read_page` e use
   `mcp__claude-in-chrome__file_upload` com o caminho do `.mp4` (não clique no
   botão de escolher arquivo: isso abre uma janela que você não controla).
3. **Detalhes**: título = `titulo` do roteiro; descrição = conteúdo do `.txt`
   (cole com `form_input` ou digitando); miniatura = a `capa` (só vídeos
   longos e só se o botão de miniatura estiver liberado); público: **"Não, não
   é conteúdo para crianças"**. Em "Mostrar mais": **Conteúdo alterado: Não**
   (narração sintética não é conteúdo realista alterado); tags = `hashtags`.
4. Avance até **Visibilidade**, escolha **Público** e clique em **Publicar**.
   Copie o link do vídeo que aparece no fim.
5. Nos vídeos longos, abra o vídeo e fixe um comentário com o link do post
   (o mesmo da descrição). Se o comentário não puder ser fixado, siga.

## 5. Registro
Acrescente cada vídeo em `data/videos.json` (crie se não existir):
```json
{"videos": [{"data": "AAAA-MM-DD", "tipo": "short", "slug": "...", "post": "slug-do-post",
             "titulo": "...", "url": "https://youtu.be/...", "voz": "elevenlabs|piper",
             "segundos": 0, "status": "publicado|pronto (não publicado: motivo)"}]}
```
Não faça commit dos arquivos de vídeo (só dos roteiros e do registro).

## 6. Escritório e mural
Em `data/escritorio.json`, atualize `produtor` e `roteirista` (status `ok`,
`ocioso` ou `erro` e uma frase em 1ª pessoa) e acrescente no `historico`.
Responda no mural o que foi resolvido.

## 7. Fim
Rode `python3 scripts/verificar.py` e `python3 site/build.py`, faça commit em
main ("Canal AAAA-MM-DD"), `git pull --rebase origin main` e push. Responda ao
dono com: os vídeos publicados (título e link), a voz usada em cada um e
qualquer problema (ex.: "o YouTube pediu verificação de telefone").
