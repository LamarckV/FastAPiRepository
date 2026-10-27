# Respostas DECISAO_TECNICA.md

### Porque escolhemos essa opção:

- Escolhemos a opção de adiar, é mais seguro para não acontecer de inserções sem antes da resposta do juiz, resumidamente, a tool feita grava dentro de uma transação aberta por turno e o commit só acontece depois da resposta do juiz.
- Antes o código passava direto e a tool rodava o comando no banco sem antes a resposta do juiz, agora ele lança no banco apenas depois da resposta do juiz dar o sinal para ele gravar a informação.
- como o banco gera um id na hora de executar sem precisar do commit, o llm consegue pegar o número da transação   
real pra responder ao usuário sem quebrar a resposta.

### Decisões que não tomamos e por que:

- nao escolhemos interceptar porque exigiria uma chamada extra do llm antes da tool rodar, deixando o processo mais lento e gastando token sem necessidade.
- nao escolhemos compensar porque o dado errado ficaria no banco por alguns segundos antes de ser apagado, e se desse uma falha de rede na hora de deletar o registro errado ficaria no banco.
- nao escolhemos tabela de staging/status pendente ficou de fora porque ia obrigar a mudar a estrutura do banco e reescrever as ferramentas de consulta de saldo pra filtrar o que tava pendente, quebrando as rotas que já funcionavam.

### Efeito nas métricas do SRE (Monitor):                
- Latência e p95 (SLO de 8s): Quase não muda e continua bem abaixo dos 8 segundos (em torno de 2 a 3s), porque não adicionamos nenhuma chamada de IA nova; a única diferença é que a conexão com o banco fica aberta por uns 2 segundos esperando o juiz responder.
- Taxa de erro (SLO de 5%): Continua perto de zero, pois quando o juiz recusa uma compra e roda o rollback, isso é um comportamento de segurança previsto e não uma falha do sistema, então o turno fecha com status ok.
- Custo e Tokens: O custo e a contagem de tokens continuam exatamente os mesmos da Etapa 7, já que não criamos novos agentes e nem aumentamos os prompts.

### Outras decisões (Google Calendar, Mongo, Falhas e Testes):
- Google Calendar e Mongo: o google calendar ficou de fora porque não tem integração no sistema, já o mongo continua como antes, salva no histórico depois do juiz, exatamente a frase que o usuário viu na tela.
- Falhas: Se o Juiz falhar ou o der erro na API, o processo bloqueia a escrita e dá rollback por segurança, se a API cair durante o processo, o banco descarta a transação automaticamente sem deixar nada escrito.
- Teste: fizemos testes com marcadores únicos de frases recusadas, como "comprei uma jaqueta em dólares" deixam 0 registros no banco, e frases em reais gravam 1 vez com sucesso.

### Arquivos criados e modificados:
- Criados:             
    - decisao_tecnica.md: documento com as decisões e explicações da solução.
- Modificados:                  
    - app/tools/db.py: criamos o controle da conexão do turno e as funções de commit e rollback.
    - app/tools/financeiro.py: tiramos o commit automático de add_transaction e update_transaction.
    - app/tools/agenda.py: tiramos o commit automático de add_event.
    - app/graph.py: ligamos o veredito do juiz ao commit (se aprovado) ou ao rollback (se recusado).