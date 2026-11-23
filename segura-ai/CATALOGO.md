# Segura Aí 3D: método e catálogo do motor 3D

Canal de TikTok de **segurança do dia a dia em animação 3D** (estilo low poly, personagem de blocos).
Separado da Nexus e da Bíblia Animada: não usa a voz de Rafa Lins nem as regras de posts da Nexus.

## O método (o que faz esse formato viralizar)
Baseado na análise de canais como Chico Constrói, Chart Maps e Curiosidades do Dia a Dia:

1. **Gancho no 1º segundo, falando com quem assiste**: uma situação que a pessoa reconhece
   ("Se você troca lâmpada em cima da cadeira..."). Nunca comece com "Olá" ou com o tema.
2. **Tentativa e erro com placar**: 2 ou 3 jeitos errados, cada um termina em desastre cômico,
   no placar `PERIGO × VOCÊ` e num rebobinar de fita. Depois o jeito certo.
3. **Mostrar o invisível**: dentro da parede (fios), a perna da cadeira que cede, o neon da chave teste.
4. **Bordão**: o placar, repetido do mesmo jeito em toda falha ("Lâmpada dois, você zero").
5. **Narração de amigo**: frases curtas, humor, sem pausa longa, voz de quem conta um caso.
6. **Etiquetas na tela**: palavra-chave em pílula (✓ verde certo, ✗ vermelho errado), legenda palavra por palavra (automática).
7. **Final com recompensa + pedido de comentário de UMA palavra** ("comenta: SOBREVIVI").
8. **Mais de 60 segundos** (o Programa de Recompensas do TikTok só paga vídeos de 1 minuto ou mais):
   160 a 290 palavras de narração, 10 a 16 cenas.

## Regras de conteúdo (inegociáveis)
- **Segurança é coisa séria: nada inventado.** Cada dica precisa estar numa fonte confiável (NR do
  Ministério do Trabalho, manual do fabricante, Corpo de Bombeiros, ABNT, Defesa Civil). Liste em `fontes`.
- Os desastres são **cômicos e sem sangue**: estrelinhas, cabelo arrepiado, placar. Nada de ferimento realista.
- Nunca ensine a fazer algo perigoso "do jeito certo" que exija profissional: quando for o caso,
  o jeito certo é **chamar o eletricista / o técnico / os bombeiros (193)**.
- Português do Brasil, linguagem de rua, sem palavrão.

## Formato do roteiro (`segura-ai/roteiros/SLUG.json`)
```json
{
 "slug": "trocar-lampada",
 "titulo": "Gancho do post, até 95 caracteres",
 "descricao": "Uma linha com o que a pessoa aprende",
 "placar_nome": "LÂMPADA",                 // o adversário do placar (curto, maiúsculo)
 "comenta": "SOBREVIVI",                   // a palavra que a pessoa comenta
 "hashtags": ["segurancadotrabalho", "..."],
 "estilo_voz": "narrador brasileiro jovem, animado e bem-humorado, ritmo rápido de TikTok",
 "fontes": ["NR-10, item 10.5.1"],
 "cenas": [ { ...cena... } ]
}
```

### Uma cena
```json
{"fala": "O que o narrador diz nesta cena (1 ou 2 frases).",
 "ambiente": "sala",
 "camera": "personagem",
 "tag": "TENTATIVA 1",
 "objetos": [{"tipo": "lampada"}, {"id": "cad", "tipo": "cadeira_plastico", "x": 0.3, "z": 0.2}],
 "personagem": {"em_cima": "cad", "acao": "esticar", "alvo": "lampada.lampada", "momento": "cadeira"},
 "etiquetas": [{"texto": "Feita pra sentar", "tipo": "ok", "em": "sentar", "alvo": "cad.assento"}],
 "seta": {"alvo": "cad.perna", "em": "peso", "sai": "abre"},
 "placar": {"a": 1, "b": 0, "em": "lampada"},
 "efeitos": ["noite"],
 "rebobinar": true}
```
- `em`, `sai` e `momento` são **gatilhos de palavra**: o começo de uma palavra da fala da cena
  (sem acento, ex.: `"nao"`, `"lampada"`), ou um número de 0 a 1 (fração da fala).
- Cada cena desenha tudo de novo: repita os objetos e a posição do personagem em cada uma.

### Ambientes
`sala` (piso de madeira, sofá, janela; o quadro de disjuntores fica na parede da esquerda),
`banheiro` (azulejo, pia, vaso, box), `cozinha` (bancada, armários, geladeira).
O chão vai de x -3 a 3 e de z -2.4 (parede do fundo) a 2. A lâmpada do teto fica em x 0, z 0.

### Objetos (`tipo`, `id` opcional, `x`, `z`, `giro` em radianos)
| tipo | opções | âncoras (para `alvo`) |
| --- | --- | --- |
| `cadeira_plastico` | | `assento`, `perna` (a que quebra), `topo` |
| `escada` | `aberta: false` (meia aberta, sem trava), `degrau` 1–4 | `topo`, `pe`, `degrau` |
| `lampada` | `acesa`, `acende_em` (palavra) | `lampada`, `bocal` |
| `interruptor` | `desligado` | `botao` (fica fixo na parede do fundo) |
| `quadro_disjuntores` | `desligar_em` (palavra) | `disjuntor`, `quadro` (fixo, parede esquerda) |
| `bilhete` | | `bilhete` (preso ao lado do quadro) |
| `tomada` | `x` | `tomada` (parede do fundo, baixa) |
| `benjamim` | `x`, `esquenta: true` (brilha vermelho) | `benjamim` |
| `chuveiro` | | `chuveiro`, `registro` (fixo, parede do fundo do banheiro) |
| `poca` | `raio` | `poca` (água no chão) |
| `fogao` | | `boca`, `botao` |
| `panela` | `em_cima: "fogao"`, `fogo`, `apaga_em`, `tampa_em`, `cabo_para_fora` | `panela`, `cabo` |
| `botijao` | | `botijao`, `registro` |
| `extintor` | | `extintor` |
| `caixa` | `altura` | `topo` |
| `fio_no_chao` | | `fio` |
Para apontar para um objeto use `"id.ancora"` (ex.: `"cad.perna"`). Âncoras especiais:
`fio_fase`, `fio_neutro` (com o efeito `raio_x`) e `personagem`.

### Personagem
`pos: [x, z]` (no chão) ou `em_cima: "id"` (+ `degrau` na escada); `olhar` (giro em radianos);
`capacete: true`; `segura: "chave_teste"` (+ `neon: true` acende o neon); `visivel: false`.
Ações (`acao`) e o `momento` em que acontecem:
- `parado`, `pensar`, `apontar` (para a câmera, use no final), `comemorar` (pulando).
- `andar` (de `de: [x,z]` até `pos`), `subir` (de `de: [x,z]` até o objeto de `em_cima`; `esticar: true` + `alvo` para já esticar o braço).
- `esticar` (braço até `alvo`, balançando), `mexer` (mão no `alvo`: interruptor, disjuntor, bocal...).
- `choque` (mão no `alvo`, pisca, raios, cabelo arrepiado; `duracao` em s).
- `cair` (de cima de `em_cima`; cadeira quebra a perna, escada escorrega; `cai_em: [x,z]`),
  `escorregar` (andando de `de` até `pos` e cai de costas), `deitado`.
Depois de `cair`/`escorregar` aparecem estrelinhas e a tela treme sozinhas.

### Câmeras
`geral` (sala inteira), `personagem` (corpo inteiro, segue o personagem — use nas quedas),
`rosto`, `perto:id.ancora`, `baixo:id.ancora`, `cima` (de cima, bom com o personagem deitado),
`parede` (os fios dentro da parede, use com `raio_x`). A câmera aproxima devagar dentro da cena e
corta seco entre cenas.

### Na tela
- `tag`: pílula laranja no topo da cena inteira (`"TENTATIVA 1"`, `"JEITO CERTO"`, `"NR-10"`).
- `etiquetas`: `texto` (curto!), `tipo` `ok` | `erro` | `info` | `aviso` | cor `#rrggbb`, `em`, `sai`, `alvo`, `y` (posição vertical, 280 a 700).
- `seta`: seta vermelha balançando sobre um `alvo`.
- `placar`: `a` (adversário) e `b` (você); `erro: false` tira o X vermelho.
- `rebobinar: true`: fita volta no fim da cena (use depois de cada falha).
- `efeitos`: `noite` (escurece depois da queda), `raio_x` (parede transparente com fase e neutro),
  `confete` (+ `confete_em`), `faisca:id.ancora`, `estrelas`.
- `chamada` (última cena): `{"nome": "SEGURA AÍ 3D", "comenta": "PALAVRA", "em": "comenta"}`.

## Estrutura típica (80 a 95 s)
1. Gancho com o placar já contra a pessoa (+ rebobinar).
2. Tentativa 1 (2 cenas: o erro com etiquetas; a falha com placar + rebobinar).
3. Tentativa 2 (idem). 4. Tentativa 3 (opcional).
5. Jeito certo em passos numerados (1., 2., 3.), uma cena por passo, + a fonte (ex.: NR-10).
6. Final: placar virado ou recompensa + confete.
7. Chamada: segue + comenta UMA palavra.
