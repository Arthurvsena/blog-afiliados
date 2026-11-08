---
name: biblia-publicar
description: Publica o próximo vídeo pronto do canal Bíblia Animada no YouTube e no TikTok pelo Chrome do Arthur e guarda o vídeo no Google Drive dele (para o Instagram). Cada execução publica UM vídeo. Roda na tarefa agendada "Bíblia Animada: publicar", duas vezes por dia.
---
> **Execução sem supervisão:** não pare para perguntar. Este canal é separado da Nexus: não use a
> voz de Rafa Lins nem publique nada no canal Nexus Tech IA.

# Bíblia Animada: publicar um vídeo

Regras: nunca digite senha, não faça login, não resolva CAPTCHA, não aceite termos, não mude
configurações de conta e nunca exclua nada. Se um site pedir login ou verificação, pule esse site,
registre o motivo e siga para os outros. Carregue a skill `chrome-browser` antes do primeiro passo
no navegador. Trabalhe em abas novas e feche-as no fim.

## 1. Qual vídeo
Leia `canal-biblia/config.yaml`, `canal-biblia/fila.json` e `canal-biblia/publicados.json`.
O vídeo é o **primeiro** de `fila.json > historias` com `status: "produzido"`. Se não houver,
responda "Nenhum vídeo da Bíblia Animada para publicar agora" e termine.
Ele está no Release `release` (campo da fila). Baixe pela API REST (o `gh release download` usa
GraphQL, que é bloqueado) para a pasta `_partes/SLUG` **dentro do repositório**:
```bash
mkdir -p _partes/SLUG && cd _partes/SLUG
gh api repos/Arthurvsena/blog-afiliados/releases/tags/RELEASE --jq '.assets[]|"\(.id) \(.name)"' | grep "SLUG" |
  while read id nome; do gh api -H "Accept: application/octet-stream" repos/Arthurvsena/blog-afiliados/releases/assets/$id > "$nome"; done
split -b 9M -d -a 2 SLUG.mp4 SLUG.mp4.parte-; ls -l
```
Arquivos: `SLUG.mp4` (1080×1920, alta qualidade: **nunca comprima**), `SLUG.json` (título),
`SLUG-youtube.txt`, `SLUG-tiktok.txt`, `SLUG-instagram.txt`.

## Envio de arquivo grande pelo Chrome (vale para os 3 sites)
O `file_upload` aceita até 10 MB por chamada, então o vídeo vai em partes de 9 MB e é remontado na página:
1. Crie um campo por parte (N = número de partes):
   `for (let i=0;i<N;i++){const e=document.createElement('input');e.type='file';e.dataset.parte=i;e.setAttribute('aria-label','parte '+i);e.style.cssText='position:fixed;left:0;top:'+(i*28)+'px;z-index:999999';document.body.appendChild(e);} 'ok'`
2. `find` "file inputs labeled parte 0 to parte N" e use `file_upload` com o caminho absoluto de cada
   parte, **uma chamada por parte, nunca dentro de `browser_batch`**. Confira os tamanhos com
   `[...document.querySelectorAll('input[data-parte]')].map(e=>e.dataset.parte+':'+(e.files[0]?.size||0)).join(' ')`.
3. Remonte: `const ps=[...document.querySelectorAll('input[data-parte]')].sort((a,b)=>a.dataset.parte-b.dataset.parte).map(e=>e.files[0]); const arq=new File(ps,'SLUG.mp4',{type:'video/mp4'}); if(arq.size!==TAMANHO) throw new Error('tamanho errado '+arq.size);`
   e entregue ao campo de arquivo do site (`DataTransfer` + evento `change`), como em cada passo abaixo.
   No fim, remova os campos `input[data-parte]`.

## 2. YouTube (canal Bíblia Animada)
1. Abra `https://studio.youtube.com`. Confira no menu à esquerda que o canal aberto é **Bíblia Animada**
   (e o ID, se `canal.youtube_canal_id` estiver preenchido). Se for outro canal (Nexus Tech IA, Art Play),
   troque pelo avatar > **Mudar de conta** > **Bíblia Animada**. Se o canal não existir, pule o YouTube
   e registre "canal Bíblia Animada não encontrado".
2. **Criar** > **Enviar vídeos**. Entregue o arquivo remontado ao `input[type=file]` da janela
   (`DataTransfer`, evento `change`). Confira com screenshot que a tela de Detalhes abriu.
3. Detalhes: título = `titulo` do `SLUG.json`; descrição = `SLUG-youtube.txt`; público:
   **"Não, não é conteúdo para crianças"** (o canal é para o público geral); em "Mostrar mais":
   **Conteúdo alterado: Não** (animação 2D, nada realista); playlist "Histórias da Bíblia" se existir.
4. Avance até **Visibilidade** > **Público** > **Publicar**. Copie o link do vídeo.

## 3. TikTok
1. Abra `https://www.tiktok.com/tiktokstudio/upload`. Se pedir login, pule o TikTok e registre.
   Se `canal.tiktok_usuario` estiver preenchido, confira que a conta aberta é ela.
2. Entregue o arquivo remontado ao `input[type=file]` da página (o que tem `accept` de vídeo).
3. Legenda: apague o texto que o TikTok preencher e digite o `SLUG-tiktok.txt` (`computer type`).
4. Em configurações: quem pode ver **Todos**; comentários permitidos; ative **"Conteúdo gerado por IA"**
   (a narração é feita por IA). Clique em **Publicar** e espere a confirmação. Se aparecer aviso de
   música ou direitos, registre e não insista.

## 4. Google Drive (para o Instagram)
Pasta: `publicacao.drive_pasta` dentro do "Meu Drive", subpasta do mês (`AAAA-MM`). Arquivos: o
`SLUG.mp4` e o `SLUG-instagram.txt` (a legenda pronta).
- **Se houver ferramentas `mcp__remote-devices__*` e uma pasta conectada do Google Drive para
  computador** (ex.: `G:\Meu Drive\Bíblia Animada`): copie os dois arquivos para
  `/mnt/user-data/outputs/` e use `device_commit_files` para gravá-los em
  `<pasta>/AAAA-MM/`. O Drive sincroniza sozinho.
- **Senão, pelo Chrome**: abra `https://drive.google.com/drive/my-drive`, entre na pasta
  `Bíblia Animada` (se não existir, crie: **Novo** > **Pasta**) e na subpasta do mês (crie se faltar).
  Remonte o arquivo (seção acima) e solte na lista de arquivos:
  `const dt=new DataTransfer(); dt.items.add(arq); const alvo=document.querySelector('[role=main]')||document.body; for (const t of ['dragenter','dragover','drop']) alvo.dispatchEvent(new DragEvent(t,{bubbles:true,cancelable:true,dataTransfer:dt}));`
  Confira com screenshot que o envio começou e terminou. Faça o mesmo com o `SLUG-instagram.txt`.
  Se não funcionar em 2 tentativas, registre "Drive: envio falhou" e siga.

## 5. Registro
Em `canal-biblia/publicados.json` acrescente:
`{"slug", "titulo", "data": "AAAA-MM-DD HH:MM", "youtube": "link ou motivo", "tiktok": "ok ou motivo", "drive": "ok ou motivo"}`
e mude o `status` da história em `fila.json` para `"publicado"` se pelo menos o YouTube ou o TikTok
deu certo (o que falhou fica escrito no registro). Se **os dois** falharam (conta não criada, login,
verificação), não mude o status: o vídeo continua esperando e a próxima execução tenta de novo. Apague `_partes/`. Faça commit em main
("Bíblia Animada: publicado SLUG"), `git pull --rebase origin main` e push.

Responda ao Arthur em 3 linhas: título, link do YouTube, e o que deu certo ou errado no TikTok e no Drive.
