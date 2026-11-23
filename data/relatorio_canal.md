# Relatório do canal Nexus Tech IA: semana de 16 a 22/11/2026 (Produtor)

Fontes: `data/metricas.json` (semana 2026-11-16, `youtube`), `data/youtube.json` (28 dias até 22/11), `data/leitura_canal.json`, `data/visitas.json`, `data/videos.json`, `data/videos/vozes.json` e a pasta `data/videos/roteiros/`. Retenção e CTR por vídeo não foram coletados nesta semana. As views por vídeo são o total desde a publicação, não só da semana. Amostra pequena: os números mostram direção, não prova.

## 1. Resumo
| Número | 16 a 22/11 | 2 a 8/11 | Variação |
|---|---|---|---|
| Views | 168 | 2.483 | -93% |
| Horas assistidas | 1,1 | 8,7 | -87% |
| Inscritos novos | 0 | 1 | -1 |
| Impressões / CTR | não coletado | 1.549 / 1,4% | n/a |
| Visitas ao blog vindas do YouTube | 0 | 0 | igual |

A semana de 9 a 15/11 não tem número do YouTube em `metricas.json`. Na janela de 28 dias (`youtube.json`) o canal tem 4.395 views, 51,9% assistido, CTR de capa de 2,0% e +2 inscritos. De 16/11 para 23/11 a janela de 28 dias só subiu 145 views (4.250 para 4.395), o que bate com a semana fraca.

**Por que a semana caiu: quase não publicamos.** A grade pede 9 vídeos por semana (`config.yaml > video.grade`). Em `data/videos.json` só há 2 vídeos novos na semana: CNH digital (16/11) e Histórias Tech #3, Tamagotchi (22/11). Os roteiros de 17 a 21/11 foram escritos e 7 deles não aparecem nem em `videos.json` nem na lista do YouTube Studio (`youtube.json`):
- 17/11: tutorial "Como desbloquear o celular quando esquece a senha" e 60s "PS Store do PS3 e do Vita vai fechar"
- 18/11: 60s "PS5 atualização 14.23"
- 19/11: 60s "GTA 6 golpes: 3 armadilhas no lançamento" e Lá Fora "Memória RAM: preço em alta por causa da IA"
- 20/11: 60s "GTA 6 autosave falha"
- 21/11: Histórias Tech "Blockbuster x Netflix"

Antes de tirar qualquer conclusão de tema ou voz, é preciso saber onde a publicação (parte B da skill `canal-diario`, no Chrome do dono) parou. Sem vídeo no ar, não há views para medir.

## 2. Vídeos da semana e os que trouxeram gente ao blog
**Ao blog: nenhum.** `data/visitas.json` não tem nenhuma visita com origem YouTube em todo o período medido, e a semana inteira (44 visitas) também teve 0. Não há "3 vídeos que mais trouxeram gente ao blog" para listar. É a terceira semana seguida com zero, e o motivo é concreto: CNH digital, Vivo Satélite, Histórias Tech #2 e #3 estão em `videos.json` com `post` vazio, ou seja, sem matéria do blog ligada ao vídeo.

Views (total desde a publicação, coleta de `metricas.json`, com o % assistido de `youtube.json`):
| Vídeo | Quadro | Views | % assistido | CTR da capa |
|---|---|---|---|---|
| Vivo Satélite: 10 milhões já usaram (13/11) | 60s | 43 | 106,6% | 1,3% (309 impressões) |
| CNH digital na blitz: print não vale (16/11) | 60s | 35 | 41,0% | 1,9% (156 impressões) |
| Histórias Tech #2: Xbox (15/11) | historias | 4 | 69,0% | 0% (45 impressões) |
| Histórias Tech #3: Tamagotchi (22/11) | historias | sem dado | sem dado | sem dado |

- **Vivo Satélite** é o melhor sinal da semana: 0:32 de vídeo e as pessoas assistem mais de uma vez (106,6%). Abre com um número grande ("10 milhões").
- **CNH digital** abre com uma regra e perde mais da metade do público (41,0%), o pior 60s da janela.
- **Xbox** segura (69,0%), mas ninguém clicou na capa: o problema é título e capa, não o vídeo.

## 3. Short x longo (28 dias, `youtube.json`)
| Formato | Vídeos | Views | Horas | Inscritos | % assistido médio | Impressões |
|---|---|---|---|---|---|---|
| Short | 14 | 4.181 | 14,9 | 2 | 59,3% | 1.732 |
| Longo | 5 | 214 | 2,3 | 1 | 23,1% | 3.265 |

- **O Short é o que funciona**: 95% das views e 87% das horas.
- **O longo recebe impressões e perde a pessoa no começo**: 3.265 impressões (mais que os Shorts), mas 23,1% assistido. Smartband x smartwatch teve 1.854 impressões e 2,2% de CTR, ou seja, a capa chama e o começo não segura.
- **Lá Fora, Aqui é o pior quadro**: Chromagraph (10 views, 24,6%) e Xiaomi 18 Pro Max (7 views, 14,5%). Média de 8 views.
- **Tutorial é o único longo com sinal bom**: "Como ter vários WhatsApp no iOS" teve 4,6% de CTR em 522 impressões e trouxe 1 inscrito com só 71 views.

## 4. Vozes Fenrir x Orus (decisão da Luisa em `data/videos/vozes.json`)
Vídeos por voz: Fenrir 8, Orus 6, menos de 10 cada. Nos Shorts, Orus teve 62,5% assistido (3 vídeos) contra 53,2% do Fenrir (6 vídeos), 17% a mais para o Orus. Nos longos, Orus 27,1% (2) contra Fenrir 19,6% (2). Na semana de 9/11 a vantagem era do Fenrir. **Sem 10 vídeos por voz e sem 2 semanas seguidas na mesma direção, fica 50/50.**

Para a medida valer na próxima segunda: Vivo Satélite e Histórias Tech #2 estão com `voz` vazia em `videos.json`, e os Shorts "GTA 6 212 GB" e "Black Friday: 3 sinais de oferta falsa" seguem sem registro. São 4 vídeos que a Luisa não consegue contar por voz.

## 5. Aprendizados
1. Número grande na primeira frase segura o 60s (Vivo Satélite 106,6%, PS5 100 milhões 85,7%). Abrir com regra ou dúvida de data derruba (CNH 41,0%, GTA 6 datas 44,6%). É a variável da semana definida pela Luisa.
2. Histórias Tech retém (Xbox 69,0%), mas depende da capa e do título: Xbox teve 0% de CTR, Orkut teve 1,3% e 348 views.
3. Views sem link para o blog não viram acesso: 4.395 views em 28 dias e 0 visitas no site.
4. Sem publicação diária o canal some: a semana com 2 uploads fez 168 views.

## 6. Três ações para a semana de 23 a 29/11 (Black Friday em 27/11)
1. **Publicar a grade inteira e registrar tudo** (meta: acessos). Descobrir com o dono por que os vídeos de 17 a 21/11 não foram ao ar (parte B da `canal-diario`) e voltar a 1 vídeo por quadro do dia. Do que ficou parado, ainda valem o tutorial de desbloquear o celular (busca "como..." perene), o Blockbuster x Netflix (história perene) e os golpes do GTA 6, que puxam para a semana da Black Friday. O "PS5 14.23, véspera do GTA 6" venceu e sai da fila. Todo vídeo publicado entra em `videos.json` com `voz` e `post` preenchidos, e quem publicar completa a voz do Vivo Satélite e do Xbox e cadastra os dois Shorts antigos sem registro. Ainda aparece no canal um segundo upload do Smartband (1 view), que deve ficar privado.
2. **Todo Short leva ao blog e pede para seguir** (meta: acessos e engajamento). A escolha da pauta passa a exigir um post relacionado no blog. Sem post, a pauta só entra se for muito forte. O post vai no comentário fixado e na descrição, e o fim tem uma chamada com motivo concreto ("amanhã tem o próximo"), como a Luisa pediu (mural #104). Nesta semana, os 60s de Black Friday (golpe, preço falso, como conferir oferta) apontam para o guia da Black Friday do blog. Objetivo: a primeira visita com origem YouTube em `visitas.json`.
3. **Uma variável só, e o Lá Fora pausado** (meta: engajamento). Todos os 60s com 30 a 40 s e um número na primeira frase, comparados com a média de 62,5%. Na quinta (26/11), no lugar do Lá Fora, Aqui, entra um tutorial "como fazer" com termo do `data/vidiq.json`. O roteiro do RAMageddon fica guardado e não sai como Lá Fora nesta semana. Nos longos, a resposta aparece nos primeiros 15 segundos. No Histórias Tech #4, título com ano ou número e capa revisada antes de publicar (o Xbox teve 0% de CTR).
