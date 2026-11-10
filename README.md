# Portal Savannah

Fiz o Portal Savannah para ajudar pequenos negócios e equipes pequenas ou médias a organizar a rotina e ter mais controle interno. Ele reúne tarefas, prazos, compromissos, metas e comunicados. Dá para acompanhar quem é responsável por cada tarefa, o que está em andamento e o que ficou atrasado.

A proposta é usar essa base em projetos da Savannah, adaptando o portal à identidade e às necessidades de cada empresa que contratar o serviço.

Desenvolvi o projeto com apoio de IA, usando Django e PostgreSQL. A implantação usa Docker, Gunicorn e Caddy, e a aplicação original já foi publicada em uma VPS.

Aqui estão o código e uma demo separada, com dados fictícios, para quem quiser conhecer o projeto. O repositório está público e os testes passaram no GitHub Actions.

## O que o portal faz

- Mostra as tarefas abertas e atrasadas do usuário no painel.
- Organiza tarefas por responsável, prazo, prioridade e situação.
- Registra compromissos com participantes, local e link de reunião.
- Exibe os compromissos em um calendário mensal.
- Acompanha metas numéricas e calcula o percentual atingido.
- Reúne os comunicados da equipe.
- Controla login, logout e permissões de alteração no servidor.

A interface usa templates do Django, HTML, CSS e JavaScript, sem um frontend separado.

## Personalização para cada empresa

A personalização é feita por projeto. Pode incluir logo, cores, textos e ajustes de interface para seguir a identidade de cada empresa que contratar a Savannah. O visual disponível neste repositório é o da própria Savannah.

Hoje, esses ajustes são feitos no código, principalmente nos templates e no CSS, junto com a configuração da implantação. Ainda não há um painel para personalizar a marca automaticamente. Mudanças em funcionalidades também precisam ser avaliadas e desenvolvidas conforme o escopo de cada projeto.

Para atender empresas diferentes com esta versão, é preciso preparar instalações, bancos, contas e segredos separados. O código atual não tem isolamento entre empresas dentro da mesma instalação, conhecido como multi-tenancy.

O foco são equipes pequenas e médias. A capacidade para cada uso ainda precisa ser validada com testes de carga.

## Aplicação e demonstração

A aplicação normal usa PostgreSQL e permite criar, editar e excluir registros conforme as permissões de cada usuário.

Todos os usuários ativos podem consultar os registros da equipe. As permissões de alteração dependem do tipo de registro, de quem o criou e de quem é o responsável. Comunicados só podem ser criados ou alterados por superusuários. Não há separação de dados entre empresas ou departamentos.

A demonstração usa `config.demo_settings`, com:

- Um banco SQLite próprio, em `demo-data/`.
- Três pessoas fictícias, sem senha utilizável e sem privilégios administrativos.
- Entrada pelo botão **Explorar demonstração**, sem senha compartilhada.
- Bloqueio de criação, edição, exclusão, administração e troca de senha no servidor.

Deixei a demo somente para leitura para que os visitantes possam explorar sem apagar ou alterar os exemplos. As operações de criação, edição e exclusão continuam no código da aplicação e nos testes.

A configuração da demo ignora as variáveis `POSTGRES_*` e usa seu próprio banco. Não reutilize segredos, contas, backups ou volumes da aplicação real.

## Rodar a demo localmente

Os comandos abaixo são para macOS ou Linux e devem ser executados na raiz do projeto.

Se ainda não tiver uma cópia do repositório:

```sh
git clone https://github.com/mauro-mota/portal-savannah.git
cd portal-savannah
```

Escolha Python ou Docker. Uma das opções já basta para rodar a demo.

### Com Python

Requer Python 3.12. Confira a versão de `python3` antes de criar o ambiente:

```sh
python3 --version
```

Com Python 3.12 disponível:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.lock.txt

export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DJANGO_SETTINGS_MODULE=config.demo_settings
export PRODUCTION=0
export ALLOWED_HOSTS=localhost,127.0.0.1

mkdir -p demo-data
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py collectstatic --noinput

gunicorn config.wsgi:application \
  --bind 127.0.0.1:8010 \
  --workers 1 \
  --worker-class gthread \
  --threads 4
```

Abra http://127.0.0.1:8010 e clique em **Explorar demonstração**.

Para parar o servidor, pressione `Ctrl+C` no terminal.

O comando `seed_demo` cria cinco tarefas, dois compromissos, uma meta e dois comunicados. Pode ser executado novamente: atualiza os mesmos exemplos, com datas relativas ao dia da execução. Ele recusa execução fora do modo demo e bases com usuários ou registros fora do padrão esperado.

### Com Docker

Requer Docker com Compose e Python 3 para gerar a chave local.

```sh
export DEMO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose -f compose.demo.yaml up --build
```

Abra http://127.0.0.1:8010.

O Compose prepara o banco, os dados fictícios e os arquivos estáticos automaticamente. O projeto se chama `savannah-portfolio-demo`, usa volume próprio e publica a porta apenas em `127.0.0.1`.

Para parar, pressione `Ctrl+C`. Se precisar parar por outro terminal, com `DEMO_SECRET_KEY` definida:

```sh
docker compose -f compose.demo.yaml stop demo
```

Use `compose.demo.yaml` para a demonstração. O arquivo `compose.prod.yaml` pertence à configuração da aplicação real e exige revisão antes de qualquer implantação.

## Testes

Na validação de 10/11/2026, passaram:

- **25 testes da aplicação**, com SQLite e PostgreSQL 17.
- **13 testes da demonstração**, com SQLite, também executados dentro do contêiner.

O [workflow do GitHub Actions](https://github.com/mauro-mota/portal-savannah/actions/workflows/test.yml) executa as verificações a cada push e pull request. A [primeira execução, no commit `a7a2f5e`](https://github.com/mauro-mota/portal-savannah/actions/runs/42738859258), terminou com os dois jobs aprovados.

Os testes cobrem autenticação, permissões, proteção CSRF, formulários, filtros, calendário e bloqueio de alterações na demo. Também verificam a entrada sem senha, a recusa de contas privilegiadas e a geração repetível dos dados fictícios.

### Executar com SQLite

Com o ambiente Python ativado e as dependências instaladas:

```sh
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export PRODUCTION=0
mkdir -p demo-data

DJANGO_SETTINGS_MODULE=config.settings TEST_SQLITE=1 \
  python manage.py test core.tests core.tests_quality

DJANGO_SETTINGS_MODULE=config.demo_settings \
  python manage.py test core.tests_demo
```

### Executar com PostgreSQL em Docker

```sh
export TEST_DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"

docker compose -f compose.test.yaml up \
  --build \
  --abort-on-container-exit \
  --exit-code-from tests

docker compose -f compose.test.yaml down
```

Esse comando executa os testes da aplicação com PostgreSQL e os da demo com SQLite. O banco PostgreSQL é temporário, não publica portas e não usa volumes da produção.

## Estrutura do projeto

- `core/models.py`: usuários, tarefas, compromissos, metas e comunicados.
- `core/forms.py`: formulários.
- `core/views.py`: telas, operações e regras de autorização.
- `core/demo.py`: entrada de visitante e bloqueios da demonstração.
- `core/management/commands/seed_demo.py`: criação dos dados fictícios.
- `config/settings.py`: configuração da aplicação normal.
- `config/demo_settings.py`: configuração da demonstração.
- `templates/` e `static/`: interface.
- `core/tests.py`, `core/tests_quality.py` e `core/tests_demo.py`: testes automatizados.
- `.github/workflows/test.yml`: verificações do GitHub Actions.
- `docs/case-portfolio.md`: estudo de caso.
- `docs/validacao.md`: registro dos testes e verificações.
- `docs/publicacao.md`: cuidados para uma futura publicação da demo.
- `SECURITY.md`: orientações de segurança.

Os documentos em `docs/` registram a preparação inicial. Algumas referências à publicação do repositório e à execução do CI ainda precisam ser atualizadas. O [roteiro original de instalação](docs/instalacao-original.md) foi preservado como referência histórica. Seus comandos precisam ser revisados antes de qualquer uso na VPS atual.

## Segurança e limites

As permissões são verificadas no servidor, inclusive quando alguém tenta acessar uma rota diretamente. A aplicação também usa proteção CSRF, validação de senhas e bloqueio de tentativas de login com `django-axes`.

O projeto ainda precisa de uma auditoria completa de segurança e dependências.

Também não há:

- Autenticação multifator.
- Recuperação automática de senha por e-mail.
- Histórico detalhado de alterações.
- Anexos.
- Integração com calendários externos.
- Testes de carga.

A revisão da interface incluiu telas em larguras de desktop e celular, mas não uma auditoria completa de acessibilidade.

Na operação da aplicação real, ainda precisam ser validados a restauração de backups, os privilégios do PostgreSQL e a distribuição de segredos entre os serviços.

Não publique `.env`, bancos, dumps, backups, chaves ou logs com dados pessoais. O `.gitignore` não remove arquivos que já tenham sido incluídos em um commit.

Antes de colocar a demo na internet, revise domínio, proxy, HTTPS, cookies seguros, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`. Use uma chave exclusiva e mantenha banco e volumes separados. O passo a passo local deste README não configura uma implantação pública.

## Uso de IA

Usei IA como apoio para construir e revisar o portal. Também uso o projeto para aprender mais sobre o caminho completo: da tela aos formulários, das permissões ao banco de dados e do ambiente local à publicação.

Este repositório mostra o que foi construído e testado até aqui. Ainda não fiz uma medição de ganho de produtividade da equipe.

## Próximos passos

- Publicar a demonstração em um endereço próprio.
- Atualizar o estudo de caso e os documentos de preparação.
- Validar a restauração de backups da aplicação real.
- Aprofundar a revisão de segurança e a observabilidade.

## Licença e marca

O repositório ainda não tem uma licença de uso e redistribuição definida. A publicação do código não concede automaticamente permissão de uso da marca Savannah.
