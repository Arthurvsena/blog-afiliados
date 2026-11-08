# Catálogo de cenas da Bíblia Animada

Cada vídeo é um roteiro JSON em `canal-biblia/roteiros/SLUG.json`. As cenas são desenhadas pelo
motor (`animacao/motor.js`) a partir deste catálogo: **não existe desenho fora daqui**. Se uma
história pedir algo que não está no catálogo, aproxime com o que existe (ex.: "rei" serve para
Nabucodonosor, Dario ou Herodes; "pessoa" com `pano` e `barba` serve para profetas).

## Formato do roteiro
```json
{
 "slug": "abraao-e-isaque",
 "titulo": "Gancho de até 95 caracteres, sem clickbait mentiroso",
 "referencia": "Gênesis 22",
 "heroi": {"nome": "Abraão", "cores": ["#hex", "#hex", "#hex", "#hex"]},
 "hashtags": ["abraao", "historiasdabiblia", "biblia", "fe", "shorts"],
 "estilo_voz": "contador de histórias bíblicas brasileiro, sotaque do Brasil, voz grave, calorosa e emocionante, ritmo de Shorts (cerca de 150 palavras por minuto), com pausas dramáticas nas viradas da história",
 "cenas": [
  {"fala": "...", "cenario": "deserto", "hora": "por_do_sol", "camera": "aproxima",
   "elementos": [{"tipo": "heroi", "x": 540, "pose": "orando"}],
   "efeitos": ["luz_divina"], "texto_tela": "3 dias"},
  {"fala": "Versículo curto, fiel ao texto.", "versiculo": true, "texto_tela": "Gênesis 22:14",
   "cenario": "ceu", "camera": "aproxima",
   "elementos": [{"tipo": "heroi", "plano": "fundo", "x": 540, "dy": 260, "escala": 1.4, "pose": "bracos_erguidos"}]}
 ]
}
```

## Método (o mesmo do canal Pixel US)
- **Cena 1 = gancho**: a frase mais chocante ou surpreendente da história, sem contexto. O espectador decide em 1 segundo.
- 6 a 8 cenas, **70 a 130 palavras no total** (45 a 55 s). Frases curtas. Uma ideia por cena.
- Uma **virada** no meio (o momento em que tudo parece perdido) e um final emocional.
- **Última cena = versículo** (`"versiculo": true`), curto (até ~20 palavras), com a referência em `texto_tela`.
- O herói da história é o **único personagem colorido** (túnica de listras com as `cores` do roteiro). Todos os outros são silhuetas.
- Fidelidade bíblica: nada de inventar falas ou fatos. Números (dias, pessoas, moedas) só se estiverem no texto bíblico.

## Cena
| campo | valores |
|---|---|
| `cenario` | `deserto`, `campo`, `cidade`, `palacio`, `templo`, `prisao`, `cova`, `mar`, `mar_aberto` (mar dividido; `abre_em` 0..1 ou -1 já aberto), `monte`, `jardim`, `ceu`, `interior`, `ventre` (dentro do peixe) |
| `hora` | `por_do_sol` (padrão), `dia`, `amanhecer`, `noite` |
| `tempestade` | `true`: céu escuro, chuva, raios e mar agitado |
| `camera` | `aproxima` (padrão), `afasta`, `zoom_forte`, `desce`, `sobe`, `direita`, `esquerda`, `fixa`. `foco: [x, y]` muda o centro do zoom |
| `tremor` | `true`: a câmera treme (terremoto, muralhas, gritos) |
| `efeitos` | `luz_divina` (feixe de luz do alto), `chuva`, `raios`, `brasas`, `fogo_do_ceu`, `arco_iris`, `sem_poeira` |
| `texto_tela` | texto curto no alto ("40 dias"). Se começar com número, ele conta de 1 até o número; `"contar": false` desliga |

Coordenadas: a tela tem 1080 × 1920. `x` vai de 0 (esquerda) a 1080 (direita); o meio é 540.

## Elementos
Campos comuns: `tipo`, `x`, `plano` (`fundo` pequeno e longe, `meio` padrão, `frente` grande e escuro),
`escala` (1 = normal), `dy` (desloca para baixo; negativo sobe), `olhar` (1 direita, -1 esquerda),
`cor` (hex, troca a cor da silhueta).

Animação: `aparece_em` (0..1 da cena), `entra` (`esquerda`, `direita`, `baixo`, `cima`, `fade`),
`anda_ate` (x final; `anda_de`/`anda_fim` em 0..1), `sobe` (pixels; negativo afunda), `some_em`,
`cai_em` (cai no chão), `treme`, `levanta_bracos_em`.

| tipo | observações |
|---|---|
| `heroi` | o colorido. `variante` opcional (`crianca`, `mulher`, `idoso`...), `veste: "branca"` |
| `pessoa` | `variante`: `homem`, `mulher`, `idoso` (barba e cajado), `crianca`, `pastor`, `soldado` (capacete, lança, escudo), `rei` (coroa), `farao`, `sacerdote`, `anjo` (asas e luz), `jesus` (túnica branca e luz). Extras: `barba`, `pano`, `cajado`, `coroa`, `colar` |
| `multidao` | `n` pessoas (padrão 9); aceita `variante` e `pose` |
| `gigante` | soldado com o dobro do tamanho |
| `pose` (heroi/pessoa/multidão) | `em_pe`, `andando`, `bracos_erguidos`, `apontando`, `orando`, `ajoelhado`, `ajoelhado_costas`, `sentado`, `caido`, `abraco`. `braco_d`/`braco_e` (radianos) para ajuste fino |
| animais | `camelo`, `ovelha` (`n`), `porco` (`n`), `leao`, `peixe_grande` (`boca_em`), `pomba` (`altura`), `cobra` |
| objetos | `barco`, `arca`, `fogo` (sarça, fornalha, altar), `tabuas` (dos mandamentos), `cruz`, `tumulo` (`aberto`, `aberto_em`), `muralha` (`cai_em`), `trono`, `mesa`, `cesto` (pães e peixes), `estrela` (`altura`), `palmeira`, `pedra` (funda: `lanca_em`, `alvo_x`, `alvo_y`), `luz` (`altura`) |

## Conferir antes de entregar
`python3 canal-biblia/montar.py canal-biblia/roteiros/SLUG.json --sem-voz --folha --saida /tmp/folhas`
gera `/tmp/folhas/SLUG-folha.jpg` com um quadro de cada cena. Abra (Read) e confira: o herói
aparece e é o único colorido, nada fica fora da tela, a legenda (embaixo) não cobre o principal,
e cada cena mostra o que a fala diz.
