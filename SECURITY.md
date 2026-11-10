# Segurança e separação dos ambientes

Este projeto não foi submetido a uma auditoria completa de segurança.

A demonstração usa dados fictícios, base SQLite própria, usuários sem senha utilizável e entrada de visitante sem privilégios. Um middleware bloqueia métodos de escrita, exceto entrada e saída da sessão, e impede páginas administrativas e de alteração de registros ou senhas.

Não reutilize segredos, bancos, backups, volumes ou contas da produção. Não exponha uma conta administrativa compartilhada. O comando seed_demo não deve ser adaptado para popular uma base real.

As configurações de implantação originais exigem revisão no ambiente real. Pontos pendentes incluem privilégios da conta PostgreSQL, distribuição de variáveis aos serviços, backups externos, restauração e dependências atualizadas.

Nunca publique .env, *.sqlite3, dumps, backups, logs com dados pessoais ou chaves. A proteção via .gitignore não remove arquivos que já tenham sido commitados.

Antes de uma publicação real, verifique o commit exato, configuração do proxy, HTTPS, autorização de acesso e execução de testes. Reporte problemas ao responsável pelo projeto por um canal privado confirmado; não há canal público de segurança configurado nesta cópia.
