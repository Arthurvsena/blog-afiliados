# Canal Histórias da Bíblia (separado da Nexus)

Shorts de histórias bíblicas no método do canal Pixel US (gancho no primeiro segundo,
virada, final emocional, 45–60 s), mas em **animação 2D desenhada por código**.

- `roteiros/*.json`: um roteiro por vídeo (cenas com `id` e `fala`). O `id` escolhe o desenho da cena.
- `animacao/cenas.html`: as cenas em 2D (silhuetas; José é o único colorido, com a túnica de listras).
- `montar.py`: narra cada cena com a voz do Gemini (a mesma função da Nexus), usa o tempo real de cada
  fala, desenha os quadros no Chromium a 30 fps e mixa a trilha própria (`scripts/trilha.py`, estilo cinema).
- Workflow **Histórias da Bíblia (vídeo)** (`.github/workflows/biblia-piloto.yml`): roda tudo no GitHub e
  publica os MP4 num Release `biblia-<slug>`. Por padrão monta uma versão com a voz Orus e outra com a Fenrir.

Prévia local sem voz: `python3 canal-biblia/montar.py canal-biblia/roteiros/jose-do-egito.json --sem-voz`
