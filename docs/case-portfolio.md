# Portal Savannah: da aplicação local à VPS

## Resumo para o portfólio

Desenvolvi, com apoio de IA, um portal para organizar tarefas, compromissos, metas e comunicados de uma equipe. Usei Django e PostgreSQL, com Docker, Gunicorn e Caddy na estrutura de implantação. O projeto saiu do ambiente local e foi publicado em uma VPS da Hostinger.

Meu foco foi construir uma aplicação completa: interface, autenticação, regras de acesso, banco de dados e publicação. Na preparação do portfólio, o projeto ganhou uma demonstração separada com dados fictícios e somente leitura.

## O problema

Tarefas, prazos, agenda e informações internas precisam estar acessíveis em um mesmo lugar. O portal reúne esses elementos e permite identificar quem é responsável por cada entrega e qual é seu andamento.

Não foi feita uma medição de ganho de produtividade. O resultado apresentado é a aplicação funcional e o processo de desenvolvimento, não uma promessa de impacto comercial.

## A solução

O painel mostra tarefas abertas e atrasadas, próximos compromissos, metas e comunicados. As listas permitem consultar responsáveis e prazos. O calendário organiza os compromissos e as metas calculam o progresso a partir dos valores registrados.

A aplicação usa páginas renderizadas pelo Django. Essa escolha mantém interface, formulários e regras de negócio no mesmo projeto, sem exigir uma API e um frontend separado para este escopo.

## Decisões técnicas

- **Django:** autenticação, formulários, ORM, administração e proteção CSRF integrados.
- **PostgreSQL na configuração normal:** persistência relacional para pessoas e registros relacionados.
- **Permissões no servidor:** esconder um botão não é suficiente; acesso direto às rotas também é verificado.
- **Docker, Gunicorn e Caddy:** estrutura definida para executar a aplicação e encaminhar acesso HTTPS.
- **Demonstração independente:** SQLite próprio, dados fictícios e nenhuma credencial da equipe. A entrada não usa uma senha compartilhada.
- **Somente leitura na demo:** protege a apresentação contra alterações, exclusões e troca de senha por visitantes.

## Verificação

A preparação executou 25 testes da aplicação e 13 da demonstração. Eles cobrem autenticação, autorização, CSRF, validação de formulários, calendário, filtros e bloqueio de mudanças na demo. Os 25 testes da aplicação passaram em SQLite e PostgreSQL 17 em contêineres isolados. A demo foi revisada no navegador em desktop e celular; essa validação não substitui teste de carga ou de restauração.

Também foram corrigidos três problemas pequenos: envio de formulário vazio sem mostrar erros, eventos dos dias adjacentes que apareciam na grade mas não eram buscados e consultas repetidas de participantes.

## Meu papel e uso de IA

Usei IA como apoio para construir e evoluir o projeto. A proposta é entender as decisões e conseguir explicar o caminho de uma operação: da tela ao formulário, da regra de permissão ao banco e da alteração local à publicação.

O projeto é um laboratório prático de desenvolvimento web e implantação. Evito apresentar como domínio independente aquilo que ainda preciso aprofundar.

## Próximos passos

Publicar a demonstração em endereço próprio e apresentar o repositório revisado, após confirmar destino e permissões de publicação. A versão do backend e dos templates já foi comparada com a VPS. A recuperação de backups segue como etapa operacional própria. Depois, evoluir observabilidade, histórico de alterações e experiência de administração conforme a necessidade real.

## Texto curto para um card

**Portal Savannah**  
Portal de equipe com tarefas, agenda, metas e comunicados. Desenvolvido em Django com apoio de IA, com estrutura de implantação em PostgreSQL, Docker, Gunicorn e Caddy. Demonstração isolada com dados fictícios e testes de autenticação, permissões e segurança das operações.

**Links:** inserir apenas depois de confirmar o endereço publicado da demo e o repositório. Não usar o acesso interno da equipe como demonstração pública.
