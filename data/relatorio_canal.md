# Relatório do canal Nexus Tech IA: semana de 2 a 8/11/2026 (Produtor)

Fonte: `data/metricas.json` (youtube), `data/visitas.json`, `data/videos.json`, `data/videos/vozes.json`. É a primeira semana medida, então não há comparação com semana anterior. Amostra pequena: os números mostram direção, não prova.

## 1. Resumo
| Número | Semana |
|---|---|
| Views | 2.483 |
| Horas assistidas | 8,7 |
| Inscritos novos | 1 |
| Impressões / CTR | 1.549 / 1,4% |
| Visitas ao blog vindas do YouTube | 0 (origens do blog: 19 diretas, 15 Google) |

Leitura: o canal já entrega views, mas **não converte em inscrito nem em visita ao blog**. 1 inscrito em 2.483 views e zero visitas vindas do YouTube. Esse é o ponto fraco a atacar, pois nossa meta é acessos.

## 2. Vídeos que mais funcionaram
| Vídeo | Views | Retenção | CTR |
|---|---|---|---|
| Sony recompra PS5 usado (não chega ao Brasil) | 1.130 | 63,4% | 5,5% |
| Ocarina of Time no Switch 2 | 474 | 48,1% | 0,0% |
| iPhone Duo, 234 mil dobras | 374 | 58,5% | 1,2% |
| Histórias Tech #1 (Orkut) | 332 | 49,3% | 1,6% |

- Sozinho, o Short da Sony traz 45% das views da semana. O padrão: **fato concreto + ângulo Brasil ("não chega aqui")**, com CTR 5,5%.
- Os Shorts de lançamento/preço sem tensão (Ocarina) tiveram retenção mais baixa (48,1%).
- Os piores: Chromagraph (longo "Lá Fora, Aqui"), 7 views e 24,6% de retenção; GTA 6 datas, 53 views e 44,6%.
- Atenção: o GTA 6 "212 GB" (92 views, CTR 10,5%, retenção 40,8%) e o "Black Friday: 3 sinais de oferta falsa" (15 views, CTR 7,4%) têm CTR alto, ou seja, o tema/título atrai, mas a retenção é fraca. Os dois não estão em `data/videos.json` (ver ação 4).

## 3. Short x longo
- Shorts: quase todas as views (2.4 mil+). Retenção de 41% a 63%.
- Longos: muito fracos. Smartband x smartwatch: 6 views (retenção boa, 72,3%, mas sem público); Chromagraph: 7 views (24,6%). Dois uploads do smartband com o mesmo título dividiram a audiência (5 + 1 views); o duplicado deve ser removido ou ficar privado.
- Hipótese: longo novo sem inscritos depende de busca; só vale com termo do vidIQ com demanda medida e título com a palavra-chave. Chromagraph (pauta de nicho) não tinha demanda provada.

## 4. Vozes Fenrir x Orus (decisão da Luisa em `data/videos/vozes.json`)
Menos de 10 vídeos por voz (Fenrir 6, Orus 3). Nos Shorts, Fenrir 54,8% de retenção (4 vídeos) contra Orus 44,6% (1 vídeo). Amostra pequena demais: **mantém 50/50**. Não tirar conclusão ainda; a diferença pode ser do tema, não da voz (o melhor vídeo, Sony, foi com Fenrir, mas o pior, Chromagraph, também).

## 5. Aprendizados (para a seção 10 do manual)
1. Gancho de "fato concreto + não chega ao Brasil" é o que gera clique (CTR 5,5%) e retenção (63%).
2. CTR alto com retenção baixa (GTA 6 212 GB, Black Friday) = título promete mais que o começo do vídeo entrega; o gancho precisa trazer a promessa logo.
3. Longos sem demanda de busca provada não andam.

## 6. Recomendações para a próxima semana (uma variável por vez)
**Para `tendencias`**
- Priorizar para o "Nexus em 60s" pautas do tipo "[empresa] faz X, mas não no Brasil" / "chega aqui? por quanto?" (padrão do vídeo da Sony). Marcar essas pautas com nota mais alta.
- Para os longos de terça (tutorial) e quinta (Lá Fora): só pauta com termo do `data/vidiq.json` com volume alto e concorrência baixa. Sem termo medido, não entra.
- Black Friday e GTA 6 (pré-download) mostraram CTR alto: manter pautas dessa semana de Black Friday (golpe/oferta falsa, como conferir preço), que também puxam o guia de compras do blog.

**Para `roteirista`**
- Abrir o Short com o dado concreto na primeira frase e a promessa do título já nos primeiros 2 segundos (corrige o caso GTA 6 e Black Friday).
- Teste de variável única: no "Nexus em 60s", comparar gancho "fato + não chega ao Brasil" contra gancho de lançamento/preço, mantendo o resto igual.
- Todo vídeo: levar a pessoa ao blog. O YouTube trouxe 0 visitas; a chamada do Short deve citar o post relacionado quando houver (link da bio) e a descrição do longo deve ter o link para o guia/post.
- Evitar repetir o formato do Ocarina (lançamento + preço sem tensão). Histórias Tech #2: tema com virada forte e dado em 2 fontes (o #1 do Orkut teve 49,3%; o Ato 2 deve ser mais curto).

## 7. Ações para o Produtor/equipe
1. Remover ou deixar privado o upload duplicado do smartband.
2. Cadastrar em `data/videos.json` os Shorts "GTA 6 212 GB" e "Black Friday: 3 sinais de oferta falsa" (voz desconhecida; a Luisa não consegue medir voz sem isso).
3. Não programar mais longo "Lá Fora" sem termo vidIQ validado; no lugar, repetir um tutorial de terça com busca clara.
4. Pedir ao `viral` textos de divulgação do Short da Sony (o melhor da semana) para as redes, apontando para o post relacionado.
