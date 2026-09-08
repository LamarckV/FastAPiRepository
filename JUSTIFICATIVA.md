# Respostas JUSTIFICAVA.md

### Questão 1:
- Criados:
    - app/vectorstore.py
    - app/perfil.py
    - app/routes/perfil.py
    - app/ingest_faq.py
    - frontend/perfil.html, perfil.css, perfil.js
- Modificados:
    - app/schemas.py
    - app/config.py
    - app/tools/financeiro.py
    - app/tools/faq.py
    - app/memoryMongo.py
    - app/routes/chat.py e app/graph.py
    - app/main.py

### Questão 2
- O perfil entra pela rota POST /perfil quando o usuário salva dentro da página
- É gravado dados numéricos (user_id, renda_mensal, objetivo, tolerancia_risco) que vão para a collection perfil no mongo e textos livres que viram um vetor e vai para o Qdrant na collection preferencias_perfil, junto da tag user_id

### Questão 3
- O texto das preferencias passa pelo llm que transforma em um vetor de 768 posições, quando o usuário faz um pergunta, é vetorizado e os vetores são calculados pelo Qdrant que calcula pelos vetores mais próximos no espaço
- Por que se buscasse a palavra exata, em uma restrição tipo "n quero nada arriscado",  não seria encontrado se o usuario perguntasse sobre cripto, pq a palavra cripto não esta escrita, a busca de vetor busca por relação de  significado

### Questão 4
- Criei uma só tool, pq fica mais simples e rápido para o llm, como uma só ele puxa direto só a renda/objetiv/risco e as preferencias, se fossem duas tools ele poderia acabar consultando os numeros e esquecendo do texto de preferencias ou o contrário, além de ficar mais lento, fica menos ocnfiável.

### Questão 5
- Por conta da busca por filtro no mongo pelo id do usuario, no Qdrant ele verifica usando um filtro por payload e na API o id do usuario vem de um contexto fixo da sessão, q impede o modelo de chutar ou criar um id pro usuario

### Questão 6
- Consulta os bancos diretamente por conta da velocidade ser maior, fazer um disparo pela api causaria lentidão no sistema desnecessaria e tem risco de travar uma sessão em outra já aberta

### Questão 7
- Por que o perfil não ta em contato direto como o usuario e nem faz tomadas de decisão, ele é só um banco de leitura pra ajuda o llm de finanças a dar conselhos melhores, fazer um agente só pra perfil deixaria o sistema muito lente sem precisar

### Questão 8
- Por que o perfil exige validação extrita, se deixar o chat principal fazer mudanças no perfil por mensagens, o usuário poderia acabar mudando informações de proposito ou até sem perceber ou o llm poderia interpretar algo errado e acabar gravando dados errado ou substituindo dados falsos