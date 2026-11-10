# Validação da cópia de portfólio

Data: 10/11/2026, UTC. Preparação em ambientes isolados e inspeção da VPS por leitura.

## Origem e comparação com produção

Base: portal-empresa-savannah-v2.tar.gz. O backend dos dois pacotes recebidos é idêntico; a v2 contém a interface Savannah e JavaScript.

A inspeção do contêiner em execução confirmou, por hashes, que 14 arquivos de backend/configuração e 11 templates correspondem à v2. Dockerfile, Compose original, start.sh e JavaScript também coincidem. Não foram lidos .env, credenciais ou registros da equipe.

O Caddy ativo serve dois CSS personalizados a partir de um volume separado, substituindo os estáticos da aplicação. Esses dois arquivos públicos foram preservados em static/ nesta cópia, em vez de depender da alteração manual no proxy. A sinalização da demo foi acrescentada ao app.css.

Hashes dos CSS públicos antes do acréscimo do aviso da demo:
- app.css: fceaa63ffa10a2cb09569985c11a4c5aa29de627c676f75fa9b8957a512b38de
- admin-savannah.css: 1898a32e6e8d33793675a1a8393f69d43340cc61ba42cf204a183c54c15f78bd

## Testes executados

- 13/13 testes originais passaram antes das alterações, com SQLite.
- 25/25 testes da aplicação passaram após as alterações, com SQLite.
- Os mesmos 25/25 passaram com PostgreSQL 17.11 real em Docker.
- 13/13 testes da demo passaram com SQLite e foram repetidos dentro do contêiner.
- Checagem Django: sem problemas.
- Nenhuma alteração de modelo sem migração detectada.
- Migração em base fictícia, seed idempotente e coleta de estáticos concluídos.
- pip check: sem conflitos.
- Sintaxe Python, JavaScript e scripts shell verificada.
- Dockerfile.demo e Compose da demo executados no Mac.
- Contêiner da demo saudável, acessível somente em 127.0.0.1:8010.
- Contêineres e rede do teste PostgreSQL foram removidos ao concluir; não foram usados dados ou volumes reais.

## Navegador

Revisadas as seis telas principais em 1280 px e 390 px, com o CSS preservado da versão publicada. Não houve estouro horizontal da página. Navegação pelo menu verificada em ambas as larguras.

Também foram verificados filtros, logout/reentrada e navegação voltar/avançar. A inspeção encontrou um timeout do worker síncrono ao lidar com conexão ociosa do navegador. A demo passou a usar um worker gthread com quatro threads. O problema foi reproduzido com conexão ociosa e revalidado com resposta HTTP 200; os fluxos de entrada e saída passaram após o ajuste.

O menu da conta recebeu nome acessível e foi incluído um favicon local. Esta revisão não equivale a auditoria completa de acessibilidade.

## Cobertura adicional

Demo: entrada sem senha, CSRF, destino local fixo, recusa de conta privilegiada, dados fictícios, seed repetível, recusa de base desconhecida, logout e bloqueio de escrita, administração e alteração de senha.

Aplicação: POST vazio, dias adjacentes do calendário, término de evento à meia-noite, consultas de participantes, escape de HTML, validação de datas/URLs/metas, filtros, permissões, CSRF e redirecionamento de login.

## Checagem pública limitada

A aplicação da equipe responde em HTTPS e redireciona a raiz para login. Foram observados cookie CSRF Secure, HSTS, X-Frame-Options DENY e X-Content-Type-Options nosniff. Não houve login na aplicação nem acesso a registros da equipe.

## Pendências reais

- Publicação pública da demo e do estudo de caso.
- Repositório confirmado e execução do CI remoto no commit a publicar.
- Teste do domínio, DNS, proxy e TLS da nova demo.
- Ensaio de recuperação de backup e teste de carga.
- Revisão de privilégios PostgreSQL e distribuição de segredos na produção.
- Auditoria completa de segurança e dependências.

O check --deploy com configurações de produção mantém dois avisos: HSTS para subdomínios e preload não ativados. Não foram habilitados automaticamente, pois afetam o domínio além desta aplicação.

O healthcheck preparado envia Host permitido e indicação de HTTPS quando PRODUCTION=1. O cenário público com proxy ainda deve ser validado no destino final.
