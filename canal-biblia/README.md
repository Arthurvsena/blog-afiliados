# Bíblia Animada (canal separado da Nexus)

Shorts de histórias bíblicas no método do canal Pixel US (gancho no primeiro segundo, virada, final
emocional, 45–55 s), em **animação 2D desenhada por código**. O herói é o único personagem colorido.

## Como funciona, todo dia
1. **Produção (GitHub Actions)**: `biblia-diario.yml` pega os próximos roteiros da fila, narra com a voz
   do Gemini (uma chamada por vídeo), desenha as cenas, mixa a trilha própria e publica os MP4 e as
   legendas num Release `biblia-AAAA-MM-DD`. Quando a fila tem menos de 6 roteiros, chama sozinho o
   `biblia-roteiros.yml`, que escreve um lote novo (skill `biblia-roteiros`).
2. **Publicação (Chrome do Arthur)**: a tarefa agendada roda duas vezes por dia e publica um vídeo por vez
   no YouTube e no TikTok e guarda no Google Drive (skill `biblia-publicar`).

## Arquivos
- `config.yaml`: nome, frequência, voz, horários, pasta do Drive e o produto indicado (link de afiliado).
- `fila.json`: roteiros prontos (ordem de produção) e as ideias das próximas histórias.
- `roteiros/*.json`: um roteiro por vídeo. Formato e tudo que dá para desenhar: `CATALOGO.md`.
- `animacao/cenas.html` + `animacao/motor.js`: o desenho 2D (cenários, personagens, câmera, legendas).
- `montar.py`: monta um vídeo. `diario.py`: a produção do dia. `publicados.json`: o que já foi ao ar.

Prévia de um roteiro (sem gastar voz): `python3 canal-biblia/montar.py canal-biblia/roteiros/SLUG.json --sem-voz --folha`
