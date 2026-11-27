---
name: segura-publicar
description: Agenda no TikTok (@seguraai3d), pelo Chrome do Arthur, TODOS os vídeos prontos do canal Segura Aí 3D, dois por dia (12:15 e 19:15), usando o agendador do próprio TikTok. Roda na tarefa agendada "Segura Aí 3D: agendar no TikTok".
---
> **Execução sem supervisão:** não pare para perguntar. Este canal é separado da Nexus e da
> Bíblia Animada: publique só na conta do Segura Aí.

# Segura Aí 3D: publicar um vídeo

Regras: nunca digite senha, não faça login, não resolva CAPTCHA nem quebra-cabeça, não aceite termos,
não mude configurações de conta e nunca exclua nada. Se o TikTok pedir login ou verificação, pare,
registre o motivo e avise o Arthur. Carregue a skill `chrome-browser` antes do primeiro passo no
navegador. Trabalhe em abas novas e feche-as no fim.

## 0. Avisar o escritório
Rode `python3 scripts/escritorio.py trabalhando seg_publicador "Publicando no TikTok"`, faça commit
("Escritório: publicador trabalhando") e push. Assim o Zap aparece andando no escritório enquanto você posta.

## 1. Quais vídeos e quando
Leia `segura-ai/config.yaml` e `segura-ai/fila.json`. Os vídeos são **todos** os de `roteiros` com
`status: "produzido"`, na ordem. Se não houver, responda "Nenhum vídeo do Segura Aí para agendar" e termine.
Abra `https://www.tiktok.com/tiktokstudio/content` e anote os horários já agendados. Dê a cada vídeo o
próximo horário livre de `publicacao.horarios` (12:15 e 19:15, hora de Brasília; se `segura-ai/estrategia.json`
tiver vencedor de `horario`, use ele em um dos dois horários; se `horario` estiver em teste, alterne as opções e
grave o horário usado em `fila.json > roteiros > teste.horario`), a partir de pelo menos
1 hora depois de agora; o TikTok aceita agendar até 10 dias à frente. Faça as seções 2 e 3 para cada vídeo, um por vez.
Baixe do Release (campo `release`) pela API REST para `_partes/SLUG` **dentro do repositório**:
```bash
mkdir -p _partes/SLUG && cd _partes/SLUG
gh api repos/Arthurvsena/blog-afiliados/releases/tags/RELEASE --jq '.assets[]|"\(.id) \(.name)"' | grep "SLUG" |
  while read id nome; do gh api -H "Accept: application/octet-stream" repos/Arthurvsena/blog-afiliados/releases/assets/$id > "$nome"; done
split -b 3M -d -a 2 SLUG.mp4 SLUG.mp4.parte-; ls -l
```
Arquivos: `SLUG.mp4` (1080×1920, **nunca comprima**), `SLUG.json` (título) e `SLUG-tiktok.txt` (legenda).

## 2. Envio do arquivo pelo Chrome
O `file_upload` aceita até 3,8 MB por chamada, então o vídeo vai em partes de 3 MB e é remontado na página:
1. Crie um campo por parte (N = número de partes):
   `for (let i=0;i<N;i++){const e=document.createElement('input');e.type='file';e.dataset.parte=i;e.setAttribute('aria-label','parte '+i);e.style.cssText='position:fixed;left:0;top:'+(i*28)+'px;z-index:999999';document.body.appendChild(e);} 'ok'`
2. `find` "file inputs labeled parte 0 to parte N" e use `file_upload` com o caminho absoluto de cada
   parte, **uma chamada por parte, nunca dentro de `browser_batch`**. Confira os tamanhos com
   `[...document.querySelectorAll('input[data-parte]')].map(e=>e.dataset.parte+':'+(e.files[0]?.size||0)).join(' ')`.
3. Remonte: `const ps=[...document.querySelectorAll('input[data-parte]')].sort((a,b)=>a.dataset.parte-b.dataset.parte).map(e=>e.files[0]); const arq=new File(ps,'SLUG.mp4',{type:'video/mp4'}); if(arq.size!==TAMANHO) throw new Error('tamanho errado '+arq.size);`
   e entregue ao `input[type=file]` da página (o que tem `accept` de vídeo) com `DataTransfer` + evento `change`.
   No fim, remova os campos `input[data-parte]`.

## 3. TikTok
1. Abra `https://www.tiktok.com/tiktokstudio/upload`. Confira no canto da tela (ou em
   `https://www.tiktok.com/tiktokstudio`) que a conta aberta é `canal.tiktok_usuario` (ou
   `canal.conta_antiga`). Se for outra conta, **não publique**: registre "conta errada" e avise.
2. Envie o arquivo remontado (seção 2) e espere o upload chegar a 100%.
3. Legenda: apague o texto que o TikTok preencher e digite o `SLUG-tiktok.txt` (`computer type`).
4. Configurações: **Programar** com a data e a hora escolhidas (se o TikTok perguntar se pode salvar o
   vídeo para publicação agendada, clique em Permitir); quem pode ver **Todos**; comentários permitidos;
   em "Exibir mais", ative **"Conteúdo gerado por IA"** (a narração é de IA) e confirme em Ativar; ligue a
   **verificação de conteúdo simples** do post e, se ela acusar restrição, registre o motivo. Clique em
   **Agendar** e confira que o vídeo aparece em Publicações com a data certa. Se aparecer aviso de música
   ou direitos, registre e não insista.

## 4. Registro
Em `segura-ai/publicados.json` (crie com `[]` se não existir) acrescente
`{"slug", "titulo", "data": "AAAA-MM-DD HH:MM (horário agendado)", "tiktok": "agendado ou motivo"}` e mude o
`status` em `fila.json` para `"publicado"` se deu certo. Se não conseguiu, não acrescente nada (nada de linhas
repetidas de "Chrome indisponível"). Rode `python3 scripts/escritorio.py feito seg_publicador "Publiquei: TÍTULO"` (ou `erro` com o motivo).
Apague `_partes/`. Faça commit em main ("Segura Aí: agendados SLUGS"), `git pull --rebase origin main` e push.

Responda ao Arthur com uma linha por vídeo: título e horário agendado (ou o motivo).
