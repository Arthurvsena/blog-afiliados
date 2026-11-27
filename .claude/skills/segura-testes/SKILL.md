---
name: segura-testes
description: Agente de testes (Lab) do canal Segura Aí 3D. Pelo Chrome do Arthur, lê no TikTok Studio os números de cada vídeo, compara as opções testadas (gancho, duração, legenda, hashtags, horário), firma o que dá mais visualizações e volta a testar quando o desempenho cai. Roda no começo da tarefa diária "Segura Aí 3D: testes e agendamento".
---
> **Execução sem supervisão:** não pare para perguntar. O objetivo do canal é **visualizações** (a renda
> vem do Programa de Recompensas do TikTok). Só leia o TikTok Studio: não mude nada na conta, não apague vídeos.

# Segura Aí 3D: testes (agente seg_testador, apelido Lab)

0. `python3 scripts/escritorio.py trabalhando seg_testador "Medindo os vídeos e ajustando os testes"`, commit e push.
1. Leia `segura-ai/estrategia.json`, `segura-ai/fila.json` (campo `teste` de cada vídeo publicado) e
   `segura-ai/metricas.json` (crie com `{"videos": {}, "historico": []}` se não existir).
2. **Coleta.** Abra `https://www.tiktok.com/tiktokstudio/content` (carregue a skill chrome-browser antes) e,
   para cada vídeo já publicado há mais de 24 h, abra a análise dele (ícone de gráfico na linha) e leia com
   `get_page_text`: visualizações, tempo médio de visualização, % que assistiu completo, curtidas, comentários,
   compartilhamentos, salvamentos, novos seguidores e origem do tráfego (se aparecer). Grave em
   `metricas.json > videos > SLUG` com a data da leitura e as horas desde a publicação. Ligue cada vídeo ao
   slug pela legenda (o título do roteiro está no começo da legenda).
3. **Diagnóstico de distribuição.** Se 3 ou mais vídeos seguidos tiverem menos de 10 visualizações após 48 h,
   o problema não é o conteúdo, é a conta (o TikTok não está mostrando os vídeos): **não tire conclusão de
   teste nenhum**. Escreva isso no relatório como prioridade 1 e recomende ao Arthur conferir
   Perfil → ☰ → Configurações e privacidade → Conta → Status da conta e usar a conta no celular. Pule para o passo 6.
4. **Comparação.** Para cada variável de `estrategia.json > variaveis`, agrupe os vídeos pela opção usada e
   calcule, por opção: nº de vídeos, mediana de visualizações em 48 h, % médio que assistiu completo,
   engajamento ((curtidas + comentários + compartilhamentos + salvamentos) ÷ visualizações).
   Uma opção **vence** quando tem pelo menos `minimo_videos_por_opcao` vídeos e `minimo_views_por_opcao`
   visualizações somadas, e a mediana de visualizações dela é pelo menos 25% maior que a da segunda colocada
   (desempate: % completo). Grave o vencedor em `vencedores`. Varie **no máximo duas variáveis ao mesmo tempo**:
   em `proximo_teste` ponha as duas que ainda não têm vencedor e que têm menos dados.
5. **Fases.**
   - `testando` → quando gancho, legenda e hashtags tiverem vencedor: `fase = "firmado"` e
     `media_referencia_views` = mediana de visualizações em 48 h dos últimos 6 vídeos.
   - `firmado` → se os últimos 4 vídeos ficarem 30% ou mais abaixo de `media_referencia_views`, volte a
     `testando`, tire de `vencedores` a variável mais antiga e, se o roteirista estiver usando sempre o mesmo
     tipo de tema, sugira temas novos em `fila.json > ideias` (acidentes domésticos comuns no Brasil).
   - Se estiver `firmado` e subindo, atualize a `media_referencia_views` para cima.
6. **Relatório.** Escreva `segura-ai/relatorio_testes.md`: fase, o que está sendo testado, a tabela por
   opção, os vencedores e 3 ações para o roteirista (tipo de gancho, duração, temas que mais deram view).
   Atualize `estrategia.json > atualizado`.
7. `python3 scripts/escritorio.py feito seg_testador "<uma frase: fase, o que venceu ou o que está testando>"`.
   Não grave valores em R$ em arquivo nenhum (o repositório é público).
