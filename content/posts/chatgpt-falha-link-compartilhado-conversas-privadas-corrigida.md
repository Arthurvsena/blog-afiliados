---
titulo: "ChatGPT: falha de segurança em link foi corrigida"
slug: chatgpt-falha-link-compartilhado-conversas-privadas-corrigida
descricao: "Falha de segurança no link compartilhado do ChatGPT foi fechada em 26/10 e não há indício de uso contra usuários comuns. Não precisa trocar a senha."
palavra_chave: "chatgpt falha segurança link"
palavras_secundarias: ["chatgpt conversas privadas falha"]
editoria: inteligencia-artificial
tipo: noticia
publicado: 2026-11-06 14:30
atualizado: 2026-11-06
fontes:
  - nome: "Parameter (relatório técnico)"
    url: "https://www.parameter.ai/labs/we-found-a-gap-at-openai"
  - nome: "Canaltech"
    url: "https://canaltech.com.br/inteligencia-artificial/golpe-de-um-clique-falha-no-chatgpt-expunha-conversas-privadas-em-4-segundos/"
  - nome: "The Hacker News"
    url: "https://thehackernews.com/2026/10/a-shared-chatgpt-link-could-run.html"
tags: ["ChatGPT", "OpenAI", "segurança", "Parameter", "MathLive"]
capa_frase: "Um clique, já corrigido"
compartilhar: "Falha no ChatGPT deixava um link expor suas conversas em 4,5 s. A OpenAI já corrigiu e não precisa trocar a senha."
imagem:
  arquivo: chatgpt-falha-link-compartilhado-conversas-privadas-corrigida.jpg
  credito: 'Logo: ChatGPT (Wikimedia Commons)'
  licenca: Public domain
  fonte: https://commons.wikimedia.org/wiki/File:ChatGPT-Logo.svg
---

Uma falha de segurança no ChatGPT web permitia que um link de conversa compartilhada executasse código malicioso na sessão de quem o abrisse, com acesso ao histórico e aos arquivos da conta. A OpenAI corrigiu o problema até 26 de outubro, segundo os pesquisadores da Parameter, e, de acordo com eles, não há indício de uso contra pessoas comuns. Quem usa o ChatGPT no Brasil não precisa trocar a senha nem mexer em nada.

## Como a falha do ChatGPT funcionava

O ataque dependia de um link de conversa compartilhada com um gráfico interativo. Segundo o Canaltech, o golpista mandaria esse link por e-mail, rede social ou mensagem. Se a vítima estivesse logada e abrisse o endereço, o código rodaria como se fosse do próprio chatgpt.com.

Na prática, é como entregar a chave de casa a quem toca a campainha só porque ele veio com um crachá parecido com o seu.

Com esse acesso, o script poderia ler o histórico, abrir mensagens antigas, ver documentos anexados e alterar configurações em segundo plano. Segundo o Canaltech, tudo levava cerca de 4,5 segundos, sem baixar nada nem autorizar aplicativo.

## O que deu errado por trás

De acordo com o relatório da Parameter, citado pelo The Hacker News, três decisões de projeto se combinaram. A biblioteca de código aberto MathLive, usada para fórmulas e teclados matemáticos, aceitava uma mensagem de configuração sem checar quem a enviou. Essa mensagem podia carregar HTML bruto. E esse HTML criava um quadro sem isolamento que herdava a identidade do ChatGPT.

O YouTube entrou só no final. Segundo o The Hacker News, um recurso do YouTube permitido pelas regras de segurança da página serviu de contorno para o ataque. Ele não foi a causa.

## Linha do tempo e correção

Pelas duas fontes, a sequência foi esta:

- **18/10:** a OpenAI recebeu o alerta pelo programa de recompensas por bugs. A gravidade subiu de P2 para P1, o nível mais alto.
- **22 a 26/10:** a correção foi aplicada nos servidores, segundo o Canaltech. O The Hacker News dá o dia 26 como o fim do trabalho.
- **28/10:** a Parameter publicou o relatório técnico, depois do conserto.

A MathLive também lançou uma atualização que passa a verificar a origem das mensagens. Os pesquisadores receberam US$ 5 mil da OpenAI.

## O que ainda não se sabe

A OpenAI não aparece com declaração própria nas matérias que li. Então a versão da correção e do alcance vem dos pesquisadores. Vale lembrar que a Parameter vende serviços de segurança, e o relatório é uma publicação da própria empresa.

Também fica a ressalva de que "sem indício de uso" não é o mesmo que "ninguém usou". Os testes, segundo a Parameter, foram feitos só entre contas controladas por ela.

## O que fazer

Como a correção está no lado da OpenAI, não é preciso atualizar app nem redefinir senha. Mesmo assim, a falha é bom lembrete de higiene:

- Desconfie de link de conversa compartilhada vindo de desconhecido, como faria com qualquer link estranho.
- Ative a verificação em duas etapas na conta. O passo a passo do WhatsApp, em [verificação em duas etapas no WhatsApp](/posts/whatsapp-confirmacao-duas-etapas-como-ativar/), segue a mesma lógica.
- Evite anexar documento sensível em conversa de IA se não precisa dele.

Para entender o tamanho do serviço, veja que o [ChatGPT teria 20% das buscas do Google](/posts/chatgpt-20-por-cento-buscas-google-openai-diz/), segundo a OpenAI. Falha em plataforma desse porte merece atenção, mesmo corrigida.

Sobre privacidade de links, a Apple também mexeu nos [links públicos do iCloud](/posts/apple-icloud-links-publicos-verificacao-ios-27-3/). E, em IA, veja o [GPT-6.1 Terra, que usa o PC](/posts/openai-gpt-6-1-terra-preco-recursos/).

:::dica Sem ação necessária
A correção está no lado da OpenAI: não é preciso atualizar app nem redefinir senha.
:::

## Vale se preocupar?

Na minha leitura, não. A brecha era séria no papel, mas foi fechada em oito dias, sem registro de vítimas. O que fica é o hábito: link de conversa também é link, e quem não conhece o remetente não deveria clicar.
