# Roteiro original de instalação (histórico)

Este documento registra a preparação inicial do portal para uma VPS nova. Os comandos precisam ser revisados antes de qualquer uso na VPS atual.

Para conhecer o projeto e executar a demonstração local, comece pelo [README principal](../README.md).

Base de código própria em Django, PostgreSQL, Docker Compose e Caddy. Não é Nextcloud e não tem plataforma com cobrança por usuário. Este pacote é um ponto de partida didático e funcional, não um serviço de hospedagem já publicado.

Premissas: Mac com Apple Silicon para desenvolvimento; VPS nova e exclusiva com Ubuntu 24.04 e acesso root para publicação. O servidor deve aceitar conexão direta, sem CDN/proxy intermediário. Se usar Cloudflare no DNS, comece em modo Somente DNS.

## O que esta versão faz

- Login por nome de usuário e senha; logout por POST; troca de senha.
- Administração de pessoas; desativação de contas; redefinição manual de senha pelo administrador.
- Tarefas com responsável, prazo, prioridade, situação e campo de andamento.
- Compromissos com datas, participantes, local e link; calendário mensal.
- Metas numéricas, prazo, responsável e percentual calculado.
- Comunicados e informações internas em texto.
- Painel inicial, filtros de tarefas, paginação e telas adaptadas para celular.
- Bloqueio temporário após cinco falhas de login, por usuário ou endereço IP. Pessoas no mesmo IP podem ser afetadas; aguarde 15 minutos ou use o comando de desbloqueio abaixo.

Todos os usuários ativos veem todos os registros. Criador, responsável e superusuário podem editar/excluir tarefas e metas. Compromissos: criador e superusuário. Comunicados: apenas superusuário. Um responsável autorizado pode alterar os campos do registro, inclusive o responsável. Não há isolamento entre departamentos nem regras de gestão hierárquica nesta base.

Não inclui envio automático de e-mails, sincronização com Google Calendar, reuniões por vídeo próprias, upload de arquivos, comentários com histórico individual nem autenticação em dois fatores. Reuniões usam um link externo; informações do negócio são textos. O administrador redefine senhas esquecidas. O número de usuários não possui limite artificial no código; capacidade depende da hospedagem e do uso.

## Antes de colar comandos

Execute um bloco de cada vez e pare se aparecer erro. Não compartilhe o arquivo .env. Não use `docker compose down -v`: o `-v` remove o volume do banco.

Substitua IP_DA_VPS pelo IP real e equipe.suaempresa.com.br pelo domínio real, sem manter esses exemplos literalmente. Os dados locais são de teste; a VPS começa com um banco vazio. O pacote original não contém .env, senhas ou banco de teste.

1. **Instale Docker no Mac.** Abra https://docs.docker.com/desktop/setup/install/mac-install/ e baixe a edição Apple Silicon. Arraste para Aplicativos, abra e espere o motor iniciar. Ele executa o site e o banco sem instalar tudo no macOS. Confira os termos de licença do Docker Desktop para sua empresa.

2. **Instale o editor.** Baixe VS Code em https://code.visualstudio.com/. Ele serve para abrir e alterar os arquivos, que são seus.

3. **Extraia o ZIP em Downloads.** A pasta deve ficar em `~/Downloads/portal-empresa`. Guarde o ZIP original: será enviado ao servidor sem as configurações locais.

4. **Abra o Terminal e entre na pasta.** Command + Espaço, digite Terminal, Enter:

```bash
cd ~/Downloads/portal-empresa
docker --version
docker compose version
```

As duas versões devem aparecer. Se Docker não conectar, abra o aplicativo Docker.

5. **Gere configurações locais.**

```bash
sh preparar.sh
```

O script cria .env com senhas aleatórias. Não altera um .env existente. Não apague esse arquivo depois de criar o banco.

6. **Ligue o sistema.**

```bash
docker compose up -d --build
docker compose logs --tail=50 web
```

Aguarde as mensagens de inicialização do Gunicorn. Abra http://localhost:8000. A tela de login confirma que a aplicação respondeu. Só este computador consegue abrir o endereço local.

7. **Crie o administrador.**

```bash
docker compose exec web python manage.py createsuperuser
```

Escolha um nome de usuário, informe e-mail e uma senha forte de pelo menos 12 caracteres. A senha não aparece enquanto você digita. Entre no navegador com esses dados.

8. **Crie duas contas de teste.** Em Pessoas → Usuários → Adicionar, crie ana e bruno com senhas diferentes. Deixe Ativo marcado; não marque Equipe/Staff nem Superusuário. Preencha os nomes e salve. Cada pessoa precisa da própria conta.

9. **Cadastre uma tarefa.** Tarefas → Adicionar: título Enviar relatório, responsável ana, prazo amanhã, prioridade Normal e situação A fazer. Salve. Entre como ana em janela privada, edite e mude para Em andamento. Isso verifica a gravação e a responsabilidade.

10. **Agende uma reunião.** Compromissos → Adicionar: título Reunião semanal, início amanhã às 10h, fim às 10h30, participantes ana e bruno. Salve e veja o Calendário. Todos os horários usam America/Sao_Paulo; o link da chamada é opcional.

11. **Cadastre uma meta.** Metas → Adicionar: título Entregas do mês, responsável ana, alvo 10, atingido 3, unidade entregas e prazo no fim do mês. A tela deve mostrar 30%.

12. **Publique uma informação interna.** Entre como administrador, abra Comunicados → Adicionar, escreva o título e o texto e salve. Os funcionários leem; apenas o administrador altera.

13. **Teste a permissão.** Copie a URL de edição da tarefa da Ana. Entre como bruno em janela privada e cole a URL. Deve aparecer Acesso não permitido. Entre sem login e abra a lista de tarefas: deve voltar ao login. Os testes automáticos podem ser executados com:

```bash
docker compose exec web python manage.py test
```

14. **Faça uma alteração real no código.** No VS Code, abra a pasta. Em templates/base.html, troque `Portal <span>da equipe</span>` pelo nome da empresa. Salve e rode:

```bash
docker compose up -d --build
```

Atualize o navegador. Para levar esse código modificado à VPS, depois de salvar, crie um pacote sem segredos:

```bash
tar --exclude=.env --exclude=.git --exclude=backups --exclude=staticfiles --exclude=__pycache__ --exclude='*.pyc' --exclude='*.sqlite3' --exclude=.venv -czf ../portal-empresa-codigo.tar.gz .
```

O passo 17 dá as duas opções de envio: ZIP original ou código personalizado. O pacote de código inclui arquivos ocultos de configuração, mas exclui credenciais e dados.

15. **Contrate a VPS só depois do teste local.** Selecione Ubuntu 24.04, acesso root e, como estimativa inicial para uso leve, 2 vCPU, 4 GB RAM e 40 GB SSD. Guarde o IP e o acesso. Não é hospedagem compartilhada de sites. Compare preço de renovação e recursos; este roteiro não fixa preço nem promete capacidade medida.

16. **Configure domínio e firewall.** No DNS, crie registro A, nome equipe, valor IP_DA_VPS. Não use um registro AAAA errado para esse mesmo nome. No firewall da hospedagem, libere TCP 80 e 443 para a internet e TCP 22 somente para seu IP atual; mantenha saída de rede permitida. Não abra 5432 ou 8000. Se seu IP mudar, atualize a regra SSH pelo painel da hospedagem. Confirme o DNS pelo Mac:

```bash
dig +short equipe.suaempresa.com.br
```

Deve aparecer o IP da VPS. O banco não tem porta pública no Compose de produção.

17. **Envie os arquivos e instale Docker na VPS.** Se usou o ZIP original, no Mac:

```bash
scp ~/Downloads/portal-empresa.zip root@IP_DA_VPS:/root/
ssh root@IP_DA_VPS
```

Na primeira conexão, confira a impressão digital SSH com a hospedagem antes de aceitar. Dentro da VPS:

```bash
apt-get update
apt-get install -y unzip
unzip portal-empresa.zip
cd /root/portal-empresa
sh instalar-docker-ubuntu.sh
```

Se personalizou no passo 14, envie o arquivo tar.gz no lugar do ZIP:

```bash
scp ~/Downloads/portal-empresa-codigo.tar.gz root@IP_DA_VPS:/root/
ssh root@IP_DA_VPS
```

Na VPS nova:

```bash
mkdir -p /root/portal-empresa
tar -xzf /root/portal-empresa-codigo.tar.gz -C /root/portal-empresa
cd /root/portal-empresa
sh instalar-docker-ubuntu.sh
```

O instalador segue o repositório apt oficial do Docker. Não execute esse roteiro em servidor com outros serviços em uso.

18. **Configure e ligue a versão da internet.** Na VPS, na pasta /root/portal-empresa:

```bash
sh preparar.sh equipe.suaempresa.com.br
docker compose -f compose.prod.yaml up -d --build
docker compose -f compose.prod.yaml logs --tail=50 web
```

Espere a aplicação iniciar; então:

```bash
docker compose -f compose.prod.yaml exec web python manage.py createsuperuser
```

Abra https://equipe.suaempresa.com.br. O Caddy obtém e renova o certificado quando DNS, rede e portas estão corretos. Não ignore erros de certificado nesse endereço público. Crie um administrador novo; o teste local não foi migrado.

19. **Cadastre a equipe real.** Entre no site público, Pessoas → Usuários → Adicionar. Crie contas individuais e entregue credenciais individualmente. Peça a cada pessoa para usar Trocar senha no primeiro acesso. Teste pelo celular usando rede móvel. Só acrescente novos usuários nessa mesma tela quando a equipe crescer. Para desligamentos, desmarque Ativo, preservando os registros.

20. **Faça backup, teste restauração e guarde cópia fora da VPS.** Na VPS:

```bash
cd /root/portal-empresa
sh backup.sh
sh validar-backup.sh
sh agendar-backup.sh
```

O segundo comando restaura em um banco temporário e o remove depois; o banco real não é alterado. O terceiro agenda às 06h no fuso do servidor. Verifique o fuso com `timedatectl`; se for UTC, são 03h em Recife/São Paulo. O script mantém todas as cópias: acompanhe espaço e retenção.

No Terminal do Mac, em uma nova janela:

```bash
mkdir -p ~/Documents/backup-portal
scp root@IP_DA_VPS:/root/portal-empresa/backups/ultimo.dump ~/Documents/backup-portal/
scp root@IP_DA_VPS:/root/portal-empresa/.env ~/Documents/backup-portal/servidor.env
chmod 600 ~/Documents/backup-portal/servidor.env
```

Guarde também o pacote do código. Proteja essa pasta porque contém dados e credenciais. A cópia para o Mac é manual: repita diariamente ou configure um serviço de backup externo antes de depender do sistema. A cópia no servidor sozinha não protege contra perda da VPS. Teste também a cópia baixada: envie de volta com outro nome e rode validar-backup.sh nesse arquivo, como abaixo.

## Comandos úteis

Os comandos abaixo de administração são executados na VPS, dentro de /root/portal-empresa. A palavra USUARIO representa o nome de login real.

```bash
# Estado dos componentes
docker compose -f compose.prod.yaml ps
# Últimas mensagens da aplicação
docker compose -f compose.prod.yaml logs --tail=100 web
# Últimas mensagens do certificado / acesso público
docker compose -f compose.prod.yaml logs --tail=100 caddy
# Trocar uma senha esquecida (sem depender de e-mail)
docker compose -f compose.prod.yaml exec web python manage.py changepassword USUARIO
# Desbloquear tentativas de login; limpa TODOS os bloqueios, inclusive por IP
docker compose -f compose.prod.yaml exec web python manage.py axes_reset
# Conferir checagens de publicação
docker compose -f compose.prod.yaml exec web python manage.py check --deploy
# Conferir tamanho dos backups
du -sh backups
# Conferir execução do backup diário
tail -n 30 /var/log/portal-backup.log
```

Se o banco ainda estiver iniciando, aguarde antes de executar comandos com `exec`. Em falha de login repetida, a proteção limita usuário e IP; ambientes com IP compartilhado podem sofrer bloqueio conjunto.

### Testar a cópia externa

No Mac:

```bash
scp ~/Documents/backup-portal/ultimo.dump root@IP_DA_VPS:/root/portal-empresa/backups/copia-externa.dump
```

Na VPS:

```bash
sh validar-backup.sh backups/copia-externa.dump
```

### Recuperar em uma VPS nova após perda do servidor

Use uma VPS nova, com o mesmo código e PostgreSQL 17. Repita a instalação do Docker, coloque o código em /root/portal-empresa e recupere o .env guardado como /root/portal-empresa/.env (permissão 600). Envie ultimo.dump para /root/portal-empresa. Não gere um .env novo por cima. Antes de iniciar web e Caddy, suba apenas o banco:

```bash
docker compose -f compose.prod.yaml up -d db
docker compose -f compose.prod.yaml ps
```

Espere db aparecer como healthy. Importe para o banco NOVO e vazio:

```bash
docker compose -f compose.prod.yaml exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl --exit-on-error' < ultimo.dump
docker compose -f compose.prod.yaml up -d --build
```

Não execute essa importação sobre banco existente com dados. Atualize o registro DNS para o novo IP. Os usuários e dados voltam ao estado do backup; certificados são reemitidos pelo Caddy. A sessão de teste temporária não substitui o ensaio de recuperação do servidor inteiro.

## Onde alterar cada coisa

| Arquivo | Função |
| --- | --- |
| templates/base.html | Nome e menu do portal |
| static/app.css | Cores, espaços e aparência |
| templates/dashboard.html | Página inicial |
| core/models.py | Campos guardados no banco |
| core/forms.py | Formulários de edição |
| core/views.py | Regras de acesso e funcionamento |
| core/tests.py | Testes automáticos |
| config/settings.py | Configuração do Django |
| compose.yaml | Execução no Mac |
| compose.prod.yaml | Execução na VPS |
| Caddyfile | HTTPS e encaminhamento para o sistema |

Após alterar apenas telas ou regras, reconstrua com `docker compose up -d --build` localmente. Se alterar os campos em models.py, gere a migração dentro do contêiner e copie-a para o código local antes de reconstruir e publicar:

```bash
docker compose up -d --build
docker compose exec web python manage.py makemigrations core
docker compose cp web:/app/core/migrations/. ./core/migrations/
docker compose up -d --build
```

Teste primeiro no Mac. Migrações de dados exigem cuidado; faça backup antes de publicar. Este roteiro não executa mudanças de esquema automaticamente por invenção: o start.sh só aplica migrações já presentes no código.

## Manutenção

As versões Python estão fixadas no requirements.txt para a base testada. Isso não faz atualizações de segurança sozinhas. Periodicamente revise versões suportadas, atualize primeiro no ambiente local, execute os testes, faça backup e publique o código atualizado. Nunca rode uma atualização de versão principal do PostgreSQL apenas trocando a tag: ela exige migração planejada.

Antes de atualizar a produção:

```bash
sh backup.sh
sh validar-backup.sh
```

Após enviar o código atualizado sem .env e sem backups, reconstrua:

```bash
docker compose -f compose.prod.yaml up -d --build
```

Os volumes mantêm os dados. Manter um volume não é a mesma coisa que ter backup.

## Verificação desta entrega

- 13 testes automatizados passaram com SQLite: autenticação, páginas protegidas, CRUD, autorização de acesso direto, CSRF, validação de datas e metas, usuário inativo e bloqueio por tentativas.
- Verificados sintaxe dos scripts shell, geração de configuração local/produção e preservação de .env existente.
- YAML dos dois Compose analisado; sem porta pública do banco em produção.
- Arquivos estáticos compilados; verificações Django executadas. `check --deploy` apresenta dois avisos opcionais de HSTS para subdomínios/preload, deliberadamente não ativados para não impor HTTPS a outros subdomínios futuros. HTTPS do próprio portal está configurado.
- Docker, PostgreSQL real, provisionamento de VPS, emissão de certificado e restauração real via PostgreSQL não foram executados neste ambiente. Não houve teste de carga de 20 usuários. Complete os testes dos passos 13, 18 e 20 na sua instalação.
- A inspeção visual por Chromium não pôde ser concluída por restrição do ambiente. As páginas foram verificadas por respostas HTTP nos testes.

## Referências

- https://docs.docker.com/desktop/setup/install/mac-install/
- https://docs.docker.com/engine/install/ubuntu/
- https://docs.docker.com/compose/how-tos/startup-order/
- https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- https://caddyserver.com/docs/automatic-https
