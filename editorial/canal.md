# Linha editorial do canal Nexus Tech IA (YouTube)

> **Formato, quadros, grade da semana e checklist: `editorial/manual_youtube.md`** (vale mais que este arquivo onde os dois divergirem).

## O que o canal é
Um **canal dark de tecnologia**: sem rosto, com narração, motion e fotos
oficiais, que as pessoas seguem porque **sempre aprendem algo útil ou
surpreendente sobre tecnologia em poucos segundos**. O canal é um produto
editorial sério, não uma vitrine. **A venda é consequência**: vem da
confiança de quem assiste, nunca o contrário.

## O que publicamos (formatos)
| Formato | O que é | Exemplo |
|---|---|---|
| Notícia quente (Short) | o fato do dia que todo mundo está comentando, com o ângulo Brasil | "iPhone Duo chegou e custa R$ 21.999" |
| Explicador (Short ou longo) | o porquê por trás de algo em alta | "Por que o seu celular esquenta carregando?" |
| Curiosidade / bastidor (Short) | o detalhe que quase ninguém sabe | "O recurso escondido do Android que economiza bateria" |
| Alerta (Short) | golpe, falha de segurança, recall, mudança de regra | "Golpe do Pix agendado: como funciona" |
| Comparativo / "vale a pena?" (longo) | decisão de compra com prós e contras honestos | "Galaxy A ou Redmi Note: qual comprar em 2026?" |
| Guia de compras (longo) | os melhores de uma categoria, para quem cada um serve | "5 fones bons até R$ 200" |
| Tutorial rápido (Short) | resolve um problema em 3 passos | "Como liberar espaço no WhatsApp" |

Equilíbrio da semana: pelo menos **70% conteúdo editorial** (notícia,
explicador, curiosidade, alerta, tutorial) e no máximo 30% de vídeos de compra.

## De onde vêm as pautas
1. `data/tendencias.json` (agente `tendencias`): o que está em alta agora no
   YouTube, no Google, no X e nas notícias de tecnologia do Brasil.
2. Posts recentes do blog com nota `"viral"` alta.
3. Guias de compra com visitas (`data/visitas.json`).

## Padrão de qualidade (vale para todo vídeo)
- **Gancho em até 2 segundos**, com o dado mais forte ou a pergunta que o
  público tem. Nada de "olá, pessoal".
- **Uma ideia por cena**, cortes a cada 1,5 a 3 segundos (fotos + gráficos).
- **Fatos com fonte**: tudo vem do post do blog ou de 2 fontes confiáveis
  abertas na hora (a fonte oficial vale por duas). Rumor é dito como rumor.
- **Ângulo Brasil**: preço aqui, quando chega aqui, funciona aqui?
- **Payoff**: o vídeo entrega o que o gancho prometeu antes do final.
- **Fim com conversa**: uma pergunta que dá vontade de comentar e o pedido
  para se inscrever (o botão "Inscrever-se" aparece animado na tela).
- **Conta uma história**: gancho → contexto → virada → prova → payoff →
  chamada. Nunca uma lista de fatos com a mesma tela repetida.
- **Mostra a prova**: print da matéria com o trecho grifado (cena `manchete`),
  de veículos diferentes, sempre com o nome do site na tela e na descrição
  (direito de citação, Lei 9.610/98, art. 46, III: só título e trecho curto).
- **Imagem do assunto**: foto oficial do produto, arte e capturas oficiais do
  jogo. Sem foto certa, cena gráfica (número, barras, linha do tempo, lista,
  calendário, comparativo). Cada vídeo usa animações variadas.
- Sem clickbait que o vídeo não entrega, sem sensacionalismo, sem opinião
  política, sem expor pessoas.

## Onde entra a venda (sem forçar)
- Só quando o assunto **naturalmente** pede um produto: um vídeo sobre
  bateria do celular pode citar um power bank do catálogo; uma notícia sobre
  o iPhone não precisa de produto nenhum.
- No máximo **1 menção** por Short, sempre no fim ("o que eu usaria está no
  link da bio"), e só com produto `ativo=sim` do catálogo.
- Se o assunto em alta pede um produto que não temos, o `tendencias` avisa o
  `curador` no mural.
- O link do blog vai em todo vídeo (matéria relacionada ou a página inicial).
