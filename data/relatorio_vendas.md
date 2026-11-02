# Relatório de vendas: semana de 2026-11-02

## Onde estamos
- Semana: 2 cliques no ML, 0 pedidos, 0 impressões no Google, 6 visitas reais no domínio novo (dado: `data/relatorio_metricas.md`). Amostra pequena demais para concluir sobre conversão.
- O gargalo de venda hoje é **descoberta**, não texto: sem tráfego, nenhuma chamada de compra é vista. Mesmo assim, há buracos de cobertura que custam cliques assim que o tráfego chegar.
- Catálogo: 27 produtos ativos, 13 posts de guia/notícia com chamadas de compra: 8 guias/listas/review (todos com 4+ chamadas) e 2 notícias/análises com 1 chamada.

## Onde perdemos cliques (cobertura)
1. **Produtos sem nenhuma chamada em post nenhum**: Logitech G203, Redragon Cobra M711 (mouses), Samsung EP-TA800 25 W, Baseus GaN5 30 W, Ugreen Nexode 45 W. São 5 de 27 fora de qualquer página.
2. **Notícias sem oferta ligada**: a maioria das notícias não tem chamada. Algumas têm produto natural no catálogo: Echo Dot / Alexa Plus (lâmpadas inteligentes), Switch 2 / Zelda (mouses e teclados gamer, só se fizer sentido editorial), Starlink/celular (power bank). Leveza: no máximo 1 link por notícia, sem forçar.
3. **Teclados e smartbands**: há post, mas nenhum guia de critério ("como escolher") para puxar tráfego de pesquisa e levar à lista.
4. **Sem pedido não dá para saber qual produto converte**: o painel do ML não mostra cliques por produto. Anotar com o dono se dá para ativar sub-ID/etiqueta por post.
5. **Produtos com cliques e zero pedidos por 2 semanas**: ainda não aplicável (1ª semana medida). Nada a passar ao curador.

## O que mudou nesta revisão
- Nenhum post alterado hoje. O `verificar.py` não aponta avisos "vendas:".

## O que testar na semana
- Link de oferta (1) em 2 notícias com produto ligado (Echo Dot/Alexa Plus para lâmpada inteligente; notícia de conectividade para power bank), medindo se cliques sobem sem aumentar a saída da página.
- Chamar a tabela "Qual comprar?" mais perto do topo nos 2 posts de maior entrada (home e guia de compras).

## 3 apostas de venda da semana
1. **Lista de carregadores rápidos (Black Friday)**: Ugreen Nexode 45 W, Baseus GaN5 30 W e Samsung 25 W entram numa lista "carregador USB-C rápido: qual comprar" (termo de compra a validar em `palavras.json`). Cobre 3 produtos órfãos antes de 27/11. Pedido ao redator via pauta.
2. **Lista de mouse gamer barato**: Logitech G203 e Redragon Cobra M711, com ponte para a lista de teclados. Cobre mais 2 órfãos e aumenta páginas por visita.
3. **Guia "Black Friday 2026 em eletrônicos: como não cair em preço falso"** com links para as listas já prontas (power bank, fones, lâmpadas, teclados), sem preço nem desconto no texto; publicar até ~15/11 para o Google indexar a tempo. Pedido ao seo/redator.

## Regras mantidas
Sem urgência falsa, sem preço no texto, sem promessa de desconto na Black Friday: o texto diz "veja o preço atual" e deixa o card mostrar a faixa.
