Simple Mark
===========

O **Simple Mark** é uma plataforma web para consultas médicas online, que conecta
pacientes e profissionais de saúde. O paciente encontra profissionais por
especialidade, consulta os horários disponíveis, agenda e paga a consulta e
participa do atendimento por videochamada. Profissionais gerenciam a agenda, as
consultas e emitem documentos clínicos (receitas e atestados com QR Code de
validação); administradores gerenciam os usuários da plataforma.

Esta documentação é gerada automaticamente com o Sphinx a partir das docstrings
(padrão Google) do backend, escrito em Python com **FastAPI**, **SQLAlchemy** e
**PostgreSQL**.

Organização do backend
----------------------

O ponto de entrada é ``backend/main.py``, que cria as tabelas, aplica as migrações,
cadastra o administrador inicial e registra as rotas no app FastAPI. O código segue
uma arquitetura em camadas:

* **routers** — rotas HTTP (endpoints) da API;
* **schemas** — modelos Pydantic de entrada e saída das rotas;
* **services** — regras de negócio;
* **repositories** — consultas e gravações no banco de dados;
* **models** — tabelas do banco (modelos SQLAlchemy);
* **core** — configuração, segurança, validadores e utilitários;
* **dependencies** — dependências injetadas pelo FastAPI (sessão do banco,
  autenticação, tratamento de erros);
* **database** — conexão com o banco e migrações;
* **seed** — dados iniciais para desenvolvimento.

Equipe: James, João Marcos, Gustavo, Raíssa e Vitor.

.. toctree::
   :maxdepth: 2
   :caption: Referência da API

   api/routers
   api/schemas
   api/services
   api/repositories
   api/models
   api/core
   api/dependencies
   api/database
   api/seed

Índices
-------

* :ref:`genindex`
* :ref:`modindex`
