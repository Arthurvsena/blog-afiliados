import json, re
S = "2026-11-03-apple-memoria-2027-iphone-mais-caro"
c = []


def a(t, fala, **k):
    d = {"tipo": t, "fala": fala}
    d.update(k)
    c.append(d)


a("gancho", "A Apple avisou: o iPhone pode ficar mais caro em {2027|dois mil e vinte e sete}.", tela="Apple avisa: iPhone mais caro em 2027", capitulo="Gancho")
a("info", "A resposta curta: a culpa é da memória, e a conta pode chegar ao seu bolso. Os links estão na descrição.", icone="alerta")
a("data", "Foi nos resultados da Apple, divulgados em {02/11|dois de novembro}. Os dados vêm da Reuters, via Canaltech.", destaque="02/11", rotulo="resultados da Apple")
a("info", "Antes de tudo, um aviso sem rodeio: ninguém falou em preço de iPhone no Brasil. Vou separar o que é fato do que é palpite.", icone="check")
a("info", "Primeiro, o que a Apple disse. O CEO, John Ternus, chamou a alta nos preços da memória de inédita.", icone="chip", capitulo="O que a Apple disse")
a("info", "A Apple alertou que o preço dos chips de memória deve continuar subindo em {2027|dois mil e vinte e sete}.", icone="chip")
a("info", "Isso pressiona o custo de iPhones e iPads. Segundo Ternus, o custo da memória já subiu em relação ao trimestre anterior.", icone="dinheiro")
a("info", "E deve subir mais até o fim do ano. Não é um susto de um mês só.", icone="relogio")
a("info", "O diretor financeiro, Kevan Parekh, disse que a memória é a principal responsável pela queda prevista na margem.", icone="dinheiro")
a("comparativo", "A Apple espera margem bruta de {45% a 46%|quarenta e cinco a quarenta e seis por cento} no trimestre que fecha em dezembro. No trimestre anterior, foi {47,9%|quarenta e sete vírgula nove por cento}.",
  itens=[{"valor": "47,9%", "rotulo": "trimestre anterior"}, {"valor": "45% a 46%", "rotulo": "previsão até dezembro"}])
a("info", "Analistas esperavam cerca de {46,7%|quarenta e seis vírgula sete por cento}. A previsão veio abaixo, e as ações chegaram a cair {4%|quatro por cento} na teleconferência.", icone="alerta")
a("numero", "Mas a Apple não está no sufoco. A receita do trimestre até setembro foi de {US$ 114,48 bilhões|cento e quatorze bilhões e quatrocentos e oitenta milhões de dólares}.", destaque="US$ 114,48 bi", rotulo="receita do trimestre até setembro")
a("numero", "As vendas de iPhone somaram {US$ 57,58 bilhões|cinquenta e sete bilhões e quinhentos e oitenta milhões de dólares}, alta de {17,5%|dezessete vírgula cinco por cento} no ano.", destaque="+17,5%", rotulo="vendas de iPhone no ano")
a("info", "Então o problema não é demanda. É o custo da peça que fica dentro do aparelho.", icone="chip")
a("info", "E a Apple já mexeu no preço. Segundo a Reuters, via Canaltech, alguns modelos do iPhone 17 subiram {US$ 100|cem dólares}.", icone="dinheiro", capitulo="Já subiu lá fora")
a("numero", "Esse aumento é em dólar. Não dá para copiar esse número para o real.", destaque="US$ 100", rotulo="alta em alguns iPhone 17")
a("info", "A empresa também diz que estoques comprados antes seguraram parte do impacto. Só que esse efeito diminui com o tempo.", icone="caixa")
a("info", "Por que a memória está tão cara? A explicação vem da Samsung, em entrevista ao Tecnoblog.", icone="ia", capitulo="Por que a memória encareceu")
a("info", "Fabricantes estão reduzindo a produção de memória RAM comum para focar em chips {HBM|agá bê ême}, usados em data centers de inteligência artificial.", icone="ia")
a("info", "Na prática: os servidores de IA disputam a mesma fábrica que faria a memória do seu celular. Quando falta peça, o preço sobe.", icone="chip")
a("info", "E ampliar a produção não é rápido. Segundo a Samsung, instalar uma fábrica dedicada a esse chip pode levar anos.", icone="relogio")
a("info", "Agora, o Brasil. A Samsung disse ao Tecnoblog que o custo da memória RAM sobe desde setembro de {2025|dois mil e vinte e cinco}.", icone="chip", capitulo="E no Brasil")
a("numero", "Para o produto final, o vice-presidente da Samsung no Brasil previu alta de {10% a 20%|dez a vinte por cento}.", destaque="até 20%", rotulo="previsão da Samsung, celulares e notebooks")
a("info", "Vale lembrar: essa conta é da Samsung, vale para eletrônicos em geral e não é uma previsão para o iPhone.", icone="alerta")
a("info", "Segundo ele, os modelos básicos e intermediários seriam os mais afetados. Os topos de linha variariam pouco.", icone="tela")
a("info", "Dell e Lenovo também anunciaram aumento de preço em notebooks, em escala global. O movimento não é só de celular.", icone="caixa")
a("info", "Então o iPhone vai ficar mais caro aqui? Ninguém confirmou isso. A Apple falou de custo, e não de preço no Brasil.", icone="alerta", capitulo="O que ainda é incerto")
a("info", "O que dá para dizer: o custo da memória está subindo, e as fabricantes falam disso em público. O resto é palpite.", icone="check")
a("info", "Na minha leitura, o recado serve de alerta para quem pensa em trocar de celular: vale acompanhar os preços, em vez de esperar sem plano.", icone="carrinho", capitulo="O que fazer antes da Black Friday")
a("info", "Primeiro: se o seu aparelho atual ainda atende, não precisa correr por medo. Pressa é má conselheira de compra.", icone="relogio")
a("info", "Segundo: se a troca já estava nos planos, compare o preço em várias lojas e confira na ficha a memória e o armazenamento.", icone="carrinho")
a("info", "Terceiro: desconfie de desconto que aparece só na véspera. Veja o preço de antes e o de agora, com calma.", icone="alerta")
a("info", "Resumindo: a Apple avisou que a memória deve seguir cara em {2027|dois mil e vinte e sete}. Quanto isso muda no Brasil, ninguém sabe ainda.", icone="check", capitulo="Resumo")
a("info", "Veredito: sem pânico e sem pressa. Acompanhe os preços e compre só o que faz sentido para o seu uso.", icone="check")
a("info", "Preparei um guia de Black Friday no blog. Os links estão na descrição.", icone="carrinho")
a("cta", "Você compraria um celular agora ou esperaria? Conta aqui nos comentários.", tela="Comprar agora ou esperar?")

t = 0
caps = []
for x in c:
    if "capitulo" in x:
        caps.append("%d:%02d %s" % (t // 60, t % 60, x["capitulo"]))
    f = re.sub(r"\{[^|}]*\|([^}]*)\}", r"\1", x["fala"])
    t += len(f.split()) * 0.4 + 0.3
print(len(c), t)
v = {
    "tipo": "longo", "slug": S, "post": "",
    "titulo": "Apple avisa: iPhone pode ficar mais caro em 2027 (memória)",
    "resumo": "A Apple avisou nos resultados de 02/11 que a memória deve seguir mais cara em 2027, pressionando iPhones e iPads. Explico o que a Apple disse, por que a memória encareceu, o que a Samsung previu para eletrônicos no Brasil e o que ninguém confirmou. No blog tem o guia de Black Friday.",
    "hashtags": ["iPhone", "Apple", "BlackFriday", "memoriaRAM", "tecnologia"],
    "selo": "Celulares", "capa_texto": "iPhone mais caro em 2027?",
    "capitulos_desc": "\n".join(caps),
    "fontes": [
        {"nome": "Canaltech (cita Reuters)", "url": "https://canaltech.com.br/smartphone/iphone-pode-ficar-ainda-mais-caro-em-2027-por-causa-da-crise-alerta-apple/"},
        {"nome": "Tecnoblog", "url": "https://tecnoblog.net/noticias/eletronicos-devem-ficar-ate-20-mais-caros-no-brasil-preve-samsung/"}],
    "produtos": [], "cenas": c}
json.dump(v, open("/home/runner/work/blog-afiliados/blog-afiliados/data/videos/roteiros/apple-memoria-2027-iphone-mais-caro-black-friday.json", "w"), ensure_ascii=False, indent=2)
