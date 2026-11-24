# Relatório de vendas: semana de 2026-11-24

## Onde estamos (semana 16 a 22/11, fonte: `data/relatorio_metricas.md`)
- 44 visitas, 12 cliques no ML (27,3% de taxa de clique, contra 32,4% na semana de 2/11), 1 pedido (8,3% dos cliques). O pedido foi indireto (balança de cozinha fora do catálogo): prova que o clique vira compra, mas não diz qual oferta convenceu.
- 84% das visitas são diretas e o Google mandou só 4. Quem chega pelo Google quer comprar, e é esse público que falta.
- Segue sem dado de clique por post ou produto. Sem sub-ID por post, não dá para saber o que vende.

## Onde perdemos cliques e vendas
1. **Páginas com leitura e zero oferta**: análise do iPhone 11 (132 impressões, posição 8,0, 0 ofertas). **Corrigido hoje**: `:::dica` no fim com 2 cabos USB-C para Lightning MFi do catálogo (Anker 322 e Ugreen US171).
2. **Google sem clique, perto da 1ª página**: Echo Dot (117 impressões, posição 12,8), lâmpadas Alexa (87, posição 14,0, já com 16 chamadas), HyperOS 4 (92). Problema de título e posição, não de oferta (seo).
3. **Power bank 20000 mAh** (página mais lida da semana, 5 visitas): primeira tela já tem a escolha principal com `{{link}}` e a tabela tem botão em todas as linhas. Nada a mudar na oferta. O `melhores-power-banks` tem 188 impressões e 0 cliques, a maioria de busca em inglês; não adianta mexer na oferta.
4. **Engajamento 1,0 página por visita**: quem entra numa lista não abre outra. O fechamento das 3 listas de energia precisa de "veja também" (redator).
5. **Notícias de alto interesse sem oferta**: Echo Dot/Echo Time e PS4 ficam com 1 chamada cada. Manter leve, 1 a 2 por post.

## Funil da Black Friday (27/11)
- Entrada: guia `black-friday-2026-eletronicos-como-nao-cair-em-preco-falso` linka as 6 listas. Em 27/11, atualizar a data do guia, sem preço e sem prometer desconto.
- Caminho: guia da BF -> lista da categoria -> ficha ou botão. Falta `melhores-fones-tws-bluetooth` e `melhores-carregadores-turbo` abrirem com a escolha principal e linkarem de volta ao guia da BF.
- Sem urgência falsa, sem "últimas unidades", sem preço no texto.

## O que testar na semana (meta: 20 cliques, melhor semana até hoje: 16)
- Cliques do iPhone 11 após a oferta de cabo (sem sub-ID, só pela soma semanal).
- Guias da BF e listas de energia com "veja também" contra o 1,0 página por visita.
- Taxa de clique de 27% ou mais com mais visitas do Google.

## 3 apostas de venda da semana
1. **Funil BF** (vendas + atualizador): guia -> listas, com escolha principal na primeira tela e link de volta nas listas de TWS e carregador turbo.
2. **Oferta leve onde o Google já mostra o post**: iPhone 11 (feito), Echo Dot e PS4, no máximo 2 chamadas.
3. **Pauta com produto**: "carregador GaN ou comum para iPhone" (o catálogo tem Ugreen Nexode, Baseus GaN5 e Samsung 25 W) e "como saber se o desconto é real", sem preço.

## Produtos com cliques e zero pedidos por 2 semanas
Sem dado por produto; nada a repassar ao curador. Pedido ao dono: ativar sub-ID por post no gerador de links do ML.

## Aviso técnico
Em `scripts/verificar.py` linha 102, o `\s*` cruza linhas: um `:::` de fechamento seguido de texto na linha de baixo conta como bloco aberto. Mural #12, o dono corrige.
