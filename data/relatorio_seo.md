# Relatório de SEO: 2026-11-02

Situação: 29 posts, sitemap com cerca de 38 URLs, Search Console com 0 cliques e 0 impressões (último dado: 31/10), 6 visitas reais em nexustechai.com.br na semana. O site ainda está sendo descoberto. Sem dados de busca, a prioridade é cobrir termos reais com posts de compra (onde já há produtos) e ligar os posts entre si.

Fonte de referência: diretrizes do Google Search Central (conteúdo útil e feito para pessoas, E-E-A-T, políticas contra spam). Não pesquisei mudanças recentes nesta rodada.

## Oportunidades de palavras (`data/palavras.json`, sem `coberto_por`)
O arquivo agora tem termos de todas as editorias, não só dos subnichos. Os mais fortes ainda sem post:

| # | Termo | Força | Fontes | Post sugerido |
|---|---|---|---|---|
| 1 | fone tws bluetooth | 4,41 | Google + ML | lista (5 fones já cadastrados) |
| 2 | fone bluetooth jbl / fone tws jbl | 4,41 / 4,11 | Google + ML | seção na lista acima (só 1 JBL no catálogo) |
| 3 | mouse gamer barato | 4,19 | Google + ML | lista (pauta existe; faltam 2 mouses) |
| 4 | fone tws só funciona um lado | 2,67 | Google (dúvida) | tutorial sem produto, com link para a lista |
| 5 | melhor smartband custo benefício / smartband bom e barato | n/d | Google | lista (4 produtos prontos) |
| 6 | headset gamer barato / melhor headset gamer | n/d | Google + ML | lista (nenhum produto cadastrado) |
| 7 | smartwatch barato (+ gps, nfc, corrida) | 2,3 | Google + ML | lista (pauta existe) |
| 8 | caixa de som bluetooth (+ até 100 reais, jbl) | 2,58 | Google | lista (nenhum produto cadastrado) |
| 9 | melhor carregador turbo | 2,22 | Google + ML | lista (3 carregadores cadastrados) |
| 10 | fone tws como usar / como ligar | 1,83 | Google (dúvida) | tutorial curto, alimenta a lista de fones |

Alerta: a pauta `melhores-fones-tws-ate-150` usa "melhor fone tws até 150 reais", que NÃO existe no arquivo. Termos reais mais próximos: "melhor fone de ouvido sem fio ate 100 reais" e "melhor fone tws até 300 reais". Trocar a palavra-chave ao escrever, ou fazer a lista "fone tws bluetooth" e usar a faixa de preço só como H2.

Pautas novas adicionadas em `data/pautas.json`: `melhores-fones-tws-bluetooth`, `fone-tws-so-funciona-um-lado`, `melhores-headsets-gamer-baratos`.

## Quase na 1ª página (posição 8 a 20)
Nenhuma ainda: o Search Console não mostra consultas nem impressões. Revisar na próxima segunda. Enquanto isso, o único sinal é 1 visita vinda do Google (post do Switch 2 / Zelda).

## Buscas com visita sem post próprio
Sem consultas registradas. Pendência: o post do Switch 2 e Zelda trouxe a única visita do Google; a continuação (Ocarina of Time) já foi publicada.

## Clusters
| Subnicho | Existe | Falta |
|---|---|---|
| Power banks e carregadores | guia como-escolher, melhores-power-banks, melhores-power-banks-20000mah, review Ugreen PB311 | melhores-carregadores-turbo (pendente, 3 produtos), comparativo 10.000 x 20.000 mAh, review Anker/Baseus |
| Fones e caixas | como-escolher-fone-bluetooth, fones-bluetooth-baratos-bons, fone-bluetooth-ou-com-fio | lista "fone tws bluetooth" (maior força livre), dúvida "só funciona um lado", caixas de som (sem produto) |
| Smartwatches e smartbands | guia smartband-ou-smartwatch | lista smartbands (4 produtos prontos), lista smartwatch barato, review Galaxy Fit3 ou Smart Band 10 |
| Acessórios gamer | melhores-teclados-mecanicos-ate-200 | mouse gamer barato (faltam 2 produtos), switch blue ou red (pendente), headset gamer barato |
| Casa inteligente | lampada-inteligente-vale-a-pena, melhores-lampadas-inteligentes-alexa, notícias Alexa+ e Echo Dot | tomada inteligente vale a pena, câmera wifi custo benefício (precisam de produtos) |
| Notícias e análises | 14 notícias, 3 análises, 3 tutoriais de WhatsApp | tutoriais WhatsApp: clonado (pendente) e Android para iPhone (pendente) formam cluster de segurança com o de duas etapas |

Links internos a reforçar (cada guia deve apontar para suas listas e vice-versa):
- como-escolher-fone-bluetooth e fone-bluetooth-ou-com-fio para a lista "fone tws bluetooth" assim que ela existir.
- smartband-ou-smartwatch-qual-escolher só tem 1 link: adicionar a lista de smartbands quando publicada.
- Notícia Echo Dot e Alexa+ para melhores-lampadas-inteligentes-alexa (já ligam entre si; conferir o link de volta).
- Notícia Switch 2 e Zelda, análise do Switch 2 e notícia do Ocarina of Time: formar triângulo (3 posts).
- iphone-duo-vale-a-pena-dobravel tem só 1 link: ligar à notícia de preço e à de MacBook/Apple.
- Notícias com 1 link apenas (Gemini, GPT-6.1, Vivo, PS Plus, Xbox, Motorola, SAC): adicionar 1 a 2 links para notícias da mesma editoria.

## Canibalização
1. `iphone-duo-preco-brasil-entrega-2027` (principal "iphone duo preço brasil") x `iphone-duo-vale-a-pena-dobravel` (usa "iphone duo preço brasil" como secundária). Tirar o termo de preço da análise e deixar a notícia com ele.
2. `alexa-plus-brasil-acesso-gratis-prorrogado-fevereiro-2027` (principal "alexa+ brasil grátis prime") x pauta `analise-alexa-plus-brasil-vale-a-pena-assinar` (a repete como secundária). A análise deve usar "alexa+ vale a pena" e "alexa plus brasil".
3. `melhores-power-banks` x `melhores-power-banks-20000mah`: manter os dois, mas o primeiro vira porta de entrada (todas as capacidades) e o segundo só 20.000 mAh. Evitar repetir os mesmos produtos na mesma ordem.
4. `fones-bluetooth-baratos-bons` x futura lista "fone tws bluetooth": a primeira foca preço baixo; a nova, formato TWS e marcas. Não repetir "barato" no título da nova.

## Sazonalidade (próximas 8 semanas)
Datas dos próprios posts e do calendário geral; confirmar as de varejo antes de publicar.
- 3/11: PS Plus de novembro começa; REDMAGIC 12 Pro (lançamento global).
- 5/11: Motorola Signature 27 e Ocarina of Time no Switch 2. Atualizar os dois posts no dia.
- 11/11: Echo Dot e Echo Time (lançamento Brasil); também "11.11", data de promoção no varejo. Reforçar listas de fones, power banks e lâmpadas.
- 12 e 13/11: fim do cadastro Vivo para a Motorola e início da pré-venda.
- 19/11: GTA 6 (segundo as fontes do post do Xbox). Atualizar o post do FSR 4.1.
- 27/11: Black Friday (última sexta de novembro). Antes disso, as listas de fones, power banks, smartbands e lâmpadas precisam estar publicadas e com chamadas de compra. Publicar até 15/11 para dar tempo de indexar.
- Dezembro: Natal. Listas "presente até R$ 200" (fones, smartbands, teclados).
- Janeiro: previsão de entrega do iPhone Duo; atualizar a notícia.

## Ações do dono
1. Cadastrar produtos pela skill: 4+ headsets gamer, 2+ mouses gamer, 3+ caixas de som bluetooth (destravam 3 listas com forte busca).
2. Conferir no Search Console se o sitemap está "Sucesso" e pedir indexação das 5 URLs principais (home, 2 guias de compra, 2 listas). Confirmar que a propriedade é a de prefixo https://nexustechai.com.br/.
3. Parar de abrir o host antigo (arthurvsena.github.io): 35 das 50 visualizações da semana vieram dele e distorcem a análise.
4. Divulgar as listas (fones, power banks) em grupos de WhatsApp e redes usando os textos de `data/redes.md`.
5. Conectar o AdSense à conta usada no Chrome (o analista não achou dados).

## Top 5 prioridades da próxima semana
1. Publicar a lista "fone tws bluetooth" (maior força livre; 5 produtos prontos), já com H2 por faixa de preço e marca.
2. Publicar a lista de smartbands (4 produtos cadastrados) e ligar ao guia smartband-ou-smartwatch.
3. Publicar "melhores carregadores turbo" com os 3 carregadores do catálogo (ou pedir o 4º ao curador), antes da Black Friday.
4. Corrigir a canibalização do iPhone Duo e da Alexa+ antes de escrever a análise da Alexa+, e trocar a palavra-chave da pauta "fones até 150" por um termo que existe no arquivo.
5. Rodada de links internos: notícias com 1 link ganham 1 a 2, e guias ganham as listas novas.
