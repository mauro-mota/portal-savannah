# Publicação: etapas restantes

## Já preparado localmente

- Cópia a partir do pacote visual v2, preservando os originais.
- Demonstração isolada, sem dados reais, senhas compartilhadas ou poderes administrativos.
- Bloqueio de alterações no servidor e interface compatível.
- Testes adicionais e workflow de CI.
- README e estudo de caso sem resultados inventados.
- Exclusão de bases, segredos, backups e arquivos de máquina do pacote entregável.

## Informações e decisões necessárias

1. Acesso e pasta da VPS já foram identificados por leitura. Para uma futura implantação, usar novamente acesso autenticado sem enviar senha, chave privada ou .env em conversa.
2. A comparação de hashes já confirmou backend e templates da v2 no contêiner. O CSS personalizado do proxy foi incorporado à cópia local. Antes de implantar, revalidar a versão e o ponto de recuperação sem expor segredos.
3. Confirmar a conta GitHub, nome e visibilidade do repositório. Não criar repositório público antes de autorizar código, marca e licença.
4. Escolher endereço e hospedagem da demo. Na mesma VPS, usar projeto, volume, domínio e upstream separados; não iniciar um segundo Caddy nas portas 80/443 já ocupadas.
5. Confirmar onde o estudo de caso será publicado. O texto está pronto, mas ainda não existe um endereço de portfólio confirmado.

## Antes de expor a demo na internet

- Gerar segredo exclusivo e durável para a demo. Nunca copiar .env da equipe.
- Manter config.demo_settings e a base demo-data própria.
- Definir ALLOWED_HOSTS somente com o domínio da demo.
- Configurar CSRF_TRUSTED_ORIGINS com https e o domínio correto.
- Ativar PRODUCTION=1 somente atrás do proxy confiável.
- Configurar proxy de maneira que não se possa forjar X-Forwarded-Proto.
- Não disponibilizar porta do banco nem o upstream diretamente na internet.
- Validar TLS, redirecionamento HTTPS, cookies seguros, login de visitante, logout, páginas, filtros, responsividade e bloqueio de todas as mutações.
- Conferir que nenhum segredo, backup, banco ou dado de equipe entrou no repositório.
- Rodar testes e CI no commit exato a publicar.
- Só anunciar a publicação depois de verificar o endereço público.

## Para preservar a produção

A configuração original usa o nome Compose fixo portal-producao. Copiá-la para outra pasta não cria automaticamente uma instalação independente. Não reutilize esse nome nem os volumes da equipe. A demo fornecida usa savannah-portfolio-demo.

A validação de backup e restauração, o menor privilégio no PostgreSQL e a identificação de versões continuam pendentes na instalação real. Não executar comandos de recuperação, rotação de segredos, firewall ou migração sem examinar o ambiente e aprovar a ação correspondente.

## Licença e direitos

A publicação pode conceder acesso permanente ao código a terceiros. Confirmar titularidade e licença antes do envio público. Esta entrega não escolhe uma licença em nome do autor.

## Manutenção da demonstração

Agendar a limpeza de sessões expiradas com `DJANGO_SETTINGS_MODULE=config.demo_settings python manage.py clearsessions`. Esse comando atua somente na base da demo. Monitorar espaço em disco e tráfego; uma demo pública também precisa de manutenção. Não foi criado agendamento nesta entrega.
