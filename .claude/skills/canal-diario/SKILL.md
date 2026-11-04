---
name: canal-diario
description: Rotina diária do departamento de vídeo. PARTE A (GitHub Actions, workflow videos.yml) escolhe os posts, escreve os roteiros, narra com a voz Gemini (Fenrir/Orus) e monta 2 Shorts e 1 vídeo longo com motion no Remotion, publicando os arquivos num Release do GitHub. PARTE B (tarefa agendada no computador do dono) baixa os vídeos do Release e publica no canal Nexus Tech do YouTube pelo Chrome.
---
> **Execução sem supervisão:** chame subagentes com `run_in_background: false`
> e espere cada resposta. Nunca use ScheduleWakeup/Monitor e só termine depois
> do último passo da parte que você está executando.

# Canal Nexus Tech: vídeos do dia

Antes de tudo: leia `CLAUDE.md`, `data/estrategia.md`, `data/relatorio_diario.md`
(se existir) e `python3 scripts/mural.py listar`.

# PARTE A: produção (GitHub Actions)

As ferramentas já vêm instaladas pelo workflow (ffmpeg, Remotion em `video/`,
vozes). A voz é a Gemini (Fenrir ou Orus, revezando pelo teste A/B de
`data/videos/vozes.json`, chave no segredo `GEMINI_API_KEY`); sem a chave, o
script usa sozinho a voz grátis Kokoro.

## A1. Tendências e pauta
1. Chame o `tendencias`: ele pesquisa o que está em alta hoje e atualiza
   `data/tendencias.json`.
2. Chame o `produtor` em **modo pauta do dia**. Ele devolve 2 Shorts e 1 longo,
   seguindo `editorial/canal.md` (conteúdo primeiro, venda como consequência).

## A2. Roteiros
Para cada vídeo: `roteirista` (com o tipo e a pauta: a tendência inteira em JSON ou o post) e depois `produtor` em
**modo revisão** com o caminho do roteiro.

## A3. Montagem (um vídeo por vez)
0. `python3 scripts/video_motion.py data/videos/roteiros/SLUG.json --checar`
   tem que dar OK (senão devolva ao roteirista com o que faltou).
1. `python3 scripts/video_motion.py data/videos/roteiros/SLUG.json --saida _videos --manter`
   Leva de 3 a 6 min por Short e de 10 a 25 min por vídeo longo. O resultado
   diz o arquivo, o tamanho (alta qualidade, sem limite de 10 MB), a duração, a voz usada, a capa (longos)
   e o `.txt` com a descrição pronta.
2. **Confira as fotos**: abra (Read) as imagens baixadas em
   `video/public/run/SLUG/c*.jpg`. Só valem fotos oficiais do próprio produto
   ou da notícia. Se alguma não mostrar exatamente o que a fala diz (foto de
   app, de exemplo de câmera, pessoas, logo de outra marca), troque a cena por
   uma cena gráfica (`numero`, `info`, `data`, `comparativo`, `barras`, `lista`, `linha`) e monte de novo.
   Confira também os prints de matéria em `video/public/run/SLUG/m*.png`: o
   título e o trecho grifado têm que estar legíveis, sem anúncio na frente.
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
pela API REST do GitHub (o `gh release download` usa GraphQL, que é bloqueado aqui),
**dentro da pasta do repositório** (o envio pelo Chrome só aceita arquivos da
pasta de trabalho desta sessão):
```bash
cd ~/blog-afiliados 2>/dev/null || cd "$(git rev-parse --show-toplevel)"
mkdir -p _partes/AAAA-MM-DD && cd _partes/AAAA-MM-DD
gh api repos/Arthurvsena/blog-afiliados/releases/tags/videos-AAAA-MM-DD --jq '.assets[]|"\(.id) \(.name)"' |
  while read id nome; do gh api -H "Accept: application/octet-stream" repos/Arthurvsena/blog-afiliados/releases/assets/$id > "$nome"; done
for v in *.mp4; do split -b 9M -d -a 2 "$v" "$v.parte-"; ls -l "$v"*; done
```
(data de hoje no horário de Brasília; `_partes/` está no .gitignore). Se não
existir Release de hoje, avise o dono que a produção não rodou e termine.
Os vídeos vêm em **alta qualidade** (Shorts 1080×1920, longos 1920×1080, de 30
a 300 MB). **Nunca comprima** para caber em 10 MB: isso destrói a imagem e a
voz. O limite de 10 MB é por envio do Chrome, então o vídeo vai em partes de
9 MB e é remontado dentro da página (passo B2.2). Pule vídeos cujo `slug` já
esteja em `data/videos.json` com status `publicado` ou `programado`.

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
2. **Envio em partes** (não clique no botão de escolher arquivo: abre uma
   janela do Windows que você não controla). Com a janela "Enviar vídeos"
   aberta:
   a. Crie um campo de arquivo para cada parte (N = número de `VIDEO.mp4.parte-*`):
      `javascript_tool`: `for (let i=0;i<N;i++){const e=document.createElement('input');e.type='file';e.dataset.parte=i;e.style.cssText='position:fixed;left:0;top:'+(i*28)+'px;z-index:999999';document.body.appendChild(e);} 'ok'`
   b. `find` "campos de arquivo" para pegar as refs e, **um por chamada**, use
      `mcp__claude-in-chrome__file_upload` com o caminho absoluto de cada parte
      (parte-00 no 1º campo criado, parte-01 no 2º...). Os campos novos são os
      últimos da página; o do YouTube é o primeiro.
   c. Remonte e entregue ao YouTube (troque NOME e TAMANHO pelo nome do `.mp4` e
      o tamanho em bytes do `ls -l`):
      ```js
      const ps=[...document.querySelectorAll('input[data-parte]')].sort((a,b)=>a.dataset.parte-b.dataset.parte).map(e=>e.files[0]);
      const arq=new File(ps,'NOME.mp4',{type:'video/mp4'});
      if (arq.size!==TAMANHO) throw new Error('tamanho errado: '+arq.size);
      const alvo=[...document.querySelectorAll('input[type=file]')].find(e=>!e.dataset.parte);
      const dt=new DataTransfer(); dt.items.add(arq); alvo.files=dt.files;
      alvo.dispatchEvent(new Event('change',{bubbles:true}));
      document.querySelectorAll('input[data-parte]').forEach(e=>e.remove()); arq.size
      ```
      Confira com screenshot que a tela de Detalhes abriu com o nome do vídeo.
      Se não abrir, tente uma vez `alvo.dispatchEvent(new Event('input',{bubbles:true}))`;
      se ainda falhar, registre "pronto (não publicado: envio falhou)" e siga.
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
