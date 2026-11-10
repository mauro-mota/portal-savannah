# Portal Savannah

Um portal de equipe em Django que reúne tarefas, compromissos, calendário, metas e comunicados. O projeto foi desenvolvido por Mauro com apoio de IA e publicado em uma VPS. Esta cópia prepara sua apresentação como projeto de portfólio.

**Estado desta entrega:** código e demonstração local preparados e testados. Nenhum repositório, site de portfólio ou ambiente público novo foi publicado. O backend e os templates foram comparados por hash com o contêiner da VPS. O CSS personalizado que era servido pelo Caddy foi preservado nesta cópia.

## O que você pode explorar

- Painel pessoal com tarefas abertas e atrasadas.
- Tarefas com responsável, prioridade, prazo, status e andamento.
- Compromissos com participantes e calendário mensal.
- Metas numéricas com percentual calculado.
- Comunicados internos.
- Login, logout por POST e regras de edição verificadas no servidor.

Todos os usuários ativos da aplicação normal veem os registros da equipe. A edição depende do criador, responsável e tipo do registro. Não há isolamento entre empresas ou departamentos.

## Dois ambientes diferentes

| Aplicação normal | Demonstração de portfólio |
| --- | --- |
| Django + PostgreSQL | Django + SQLite exclusivo |
| Pessoas e permissões administradas pelo responsável | Três pessoas fictícias, sem senha utilizável |
| Criação, edição e exclusão conforme permissões | Somente leitura, inclusive no servidor |
| Configuração `config.settings` | Configuração `config.demo_settings` |
| Implantação original deve ser revisada na VPS | Pode rodar localmente sem banco real |

A demonstração **não usa** variáveis POSTGRES, banco, volume, segredo ou conta da produção. O botão de entrada inicia uma sessão de visitante comum, nunca administrativa. Troca de senha, administração e mutações ficam bloqueadas.

A experiência somente leitura foi escolhida para não permitir que um visitante apague os exemplos, publique conteúdo impróprio ou bloqueie o acesso dos demais. O CRUD original continua disponível no código e nos testes.

## Executar a demonstração local

Requer Python 3.12. Em um terminal dentro desta pasta:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock.txt
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DJANGO_SETTINGS_MODULE=config.demo_settings
mkdir -p demo-data
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 127.0.0.1:8010 --workers 1 --worker-class gthread --threads 4
```

Abra http://127.0.0.1:8010 e selecione **Explorar demonstração**. Não há senha pública.

O comando `seed_demo` é repetível: atualiza os mesmos exemplos, com datas relativas ao dia da execução. Ele recusa execução fora do modo demo e recusa bases com usuários ou registros não reconhecidos. Não importa backups.

### Opção Docker local

```sh
export DEMO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose -f compose.demo.yaml up --build
```

O projeto Docker se chama `savannah-portfolio-demo`, usa volume próprio e publica apenas em `127.0.0.1:8010`. Não reutilize `compose.prod.yaml` para a demo. A demo foi executada e validada por Docker no Mac.

## Executar os testes

```sh
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
DJANGO_SETTINGS_MODULE=config.settings TEST_SQLITE=1 python manage.py test core.tests core.tests_quality
DJANGO_SETTINGS_MODULE=config.demo_settings python manage.py test core.tests_demo
```

Na preparação desta cópia, passaram **25 testes da aplicação e 13 da demo**. Os 13 testes originais também foram executados separadamente antes das alterações. Os testes usam bancos temporários e não acessam a VPS. Os 25 testes da aplicação também passaram com PostgreSQL 17.11 em Docker; os 13 da demo foram repetidos no contêiner.

Há um workflow de GitHub Actions em `.github/workflows/test.yml`. Ele está preparado no código, mas não executou no GitHub porque nada foi enviado a um repositório.

## Estrutura

- `core/models.py`: usuários e registros.
- `core/forms.py`: formulários e validação.
- `core/views.py`: leitura, CRUD e autorização.
- `core/demo.py`: entrada e proteção da demonstração.
- `core/management/commands/seed_demo.py`: exemplos fictícios.
- `config/settings.py`: aplicação normal.
- `config/demo_settings.py`: configuração isolada.
- `templates/` e `static/`: interface responsiva Savannah.
- `docs/case-portfolio.md`: texto-base do estudo de caso.
- `docs/validacao.md`: resultados e limites verificados.
- `docs/publicacao.md`: etapas restantes para publicação.
- `LEIA-ME.md`: roteiro histórico recebido nos pacotes; não representa uma validação desta VPS.

## Limites conhecidos

Não há MFA, recuperação automática por e-mail, histórico detalhado de alterações, anexos, integração de calendário ou teste de carga. A demo somente leitura não simula alterações persistentes.

Os testes automatizados foram executados com SQLite e PostgreSQL 17 em contêineres isolados. Recuperação de backups, carga e uma implantação pública da demo ainda exigem validação própria.

## Código e marca

Não foi adicionada uma licença de redistribuição nem alterada qualquer permissão de publicação. A titularidade e a autorização para exposição do código e da marca devem ser confirmadas antes de tornar um repositório público.

## Repetir a validação PostgreSQL

```sh
export TEST_DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests
docker compose -f compose.test.yaml down
```

O banco deste teste é temporário, não publica portas e não usa volumes da produção.

## Parar a demo local

```sh
docker stop savannah-portfolio-demo-demo-1
```

Isso para apenas a demonstração criada para o portfólio, sem tocar no servidor publicado.
