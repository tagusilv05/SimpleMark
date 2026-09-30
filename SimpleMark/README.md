# Simple Mark

<p align="center">
  <img src="assets/logosm.jpeg" alt="Simple Mark" width="300">
</p>

# Sobre o projeto

O Simple Mark é uma plataforma web voltada para a realização de consultas médicas online, conectando pacientes e profissionais de saúde por meio de uma aplicação digital. A plataforma tem como objetivo facilitar o acesso aos serviços de saúde, permitindo que o paciente encontre profissionais por especialidade, consulte horários disponíveis, realize o agendamento e participe da consulta remotamente por meio de uma sala virtual. O sistema também disponibiliza funcionalidades específicas para profissionais de saúde e administradores, permitindo o gerenciamento de agendas, consultas, documentos clínicos e usuários.

# Funcionalidades
- 👤 Cadastro e autenticação de pacientes e profissionais.
- 🔎 Busca de profissionais por especialidade.
- 📅 Agendamento de consultas e gerenciamento da agenda.
- 💳 Pagamento das consultas durante o agendamento.
- 📹 Consultas por videoconferência.
- 📄 Emissão e gerenciamento de documentos clínicos, como receitas e atestados.
- ⭐ Avaliação dos profissionais após as consultas.
- 🔔 Notificações sobre consultas e alterações na agenda.
- 🔐 Controle de acesso de acordo com o perfil do usuário.

# Como Executar

### Pré-requisitos

- Docker instalado na máquina

Para executar o projeto no Docker, acesse a pasta raiz do projeto e execute o comando abaixo:

```bash
docker compose up --build -d
```
- A API estará disponível em: http://localhost:8080
- Acesse o Adminer em: http://localhost:8000

Para remover os containers em execução:

```bash
docker compose down
```
# Estrutura do Projeto
```
SimpleMark
├─ backend
│  ├─ core
│  │  └─ config.py
│  ├─ database
│  │  └─ connection.py
│  ├─ dependencies
│  │  └─ database.py
│  ├─ models
│  │  └─ models.py
│  ├─ repositories
│  ├─ routers
│  ├─ schemas
│  ├─ services
|  └─ main.py
├─ compose.yaml
├─ Dockerfile.back
├─ README.md
└─ requirements.txt
```