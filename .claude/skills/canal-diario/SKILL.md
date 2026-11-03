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

## A1. Tendências e pauta
1. Chame o `tendencias`: ele pesquisa o que está em alta hoje e atualiza
   `data/tendencias.json`.
2. Chame o `produtor` em **modo pauta do dia**. Ele devolve 2 Shorts e 1 longo,
   seguindo `editorial/canal.md` (conteúdo primeiro, venda como consequência).

## A2. Roteiros
Para cada vídeo: `roteirista` (com o tipo e a pauta: a tendência inteira em JSON ou o post) e depois `produtor` em
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
pela API REST do GitHub (o `gh release download` usa GraphQL, que é bloqueado aqui):
```bash
mkdir -p /mnt/user-data/outputs/videos && cd /mnt/user-data/outputs/videos
gh api repos/Arthurvsena/blog-afiliados/releases/tags/videos-AAAA-MM-DD --jq '.assets[]|"\(.id) \(.name)"' |
  while read id nome; do gh api -H "Accept: application/octet-stream" repos/Arthurvsena/blog-afiliados/releases/assets/$id > "$nome"; done
```
(data de hoje no horário de Brasília). Se não existir Release de hoje, avise o
dono que a produção não rodou e termine.
O envio pelo Chrome aceita no máximo 10 MB por arquivo: para cada `.mp4` com mais
de 9,5 MB, rode `pip install --break-system-packages -q pyyaml pillow` e
`python3 scripts/video_motion.py --comprimir CAMINHO.mp4` antes de enviar. Pule vídeos cujo `slug` já esteja em
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
4. Avance até **Visibilidade** e escolha **Programar** (não "Público"): cada
   vídeo sai num horário diferente (veja "Horários" abaixo). Preencha data e
   hora (fuso de Brasília) e clique em **Programar**. Copie o link do vídeo.
5. Nos vídeos longos, abra o vídeo e fixe um comentário com o link do post
   (o mesmo da descrição). Se não puder ser fixado, siga.

### Horários (um vídeo por horário, nunca todos juntos)
Horários-padrão do dia, de `config.yaml > video.horarios`: **12:00** o 1º Short,
**19:00** o vídeo longo, **21:00** o 2º Short (os horários de mais audiência
no Brasil para cada formato). Comece pelo Short de maior nota.
- Se um horário já passou (ou falta menos de 30 min), use o próximo horário
  livre de hoje começando 30 min depois de agora e com pelo menos **2 horas**
  entre um vídeo e outro.
- Se isso passar das 23:00, programe para amanhã no horário-padrão dele.
- Grave a data e hora programadas em `publica_em` no registro.

## B3. Registro
Acrescente cada vídeo em `data/videos.json` (crie se não existir):
```json
{"videos": [{"data": "AAAA-MM-DD", "tipo": "short", "slug": "...", "post": "slug-do-post",
             "titulo": "...", "url": "https://youtu.be/...", "voz": "google:Charon",
             "segundos": 0, "publica_em": "AAAA-MM-DD HH:MM", "status": "programado|publicado|pronto (não publicado: motivo)"}]}
```
Faça commit em main ("Canal AAAA-MM-DD"), `git pull --rebase origin main` e
push (sem os arquivos de vídeo). Responda ao dono com os vídeos publicados
(título e link) e qualquer problema.
