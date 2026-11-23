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

Na primeira vez, crie o `.env` a partir do exemplo e troque **todos** os valores (gere senhas com `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`):

```bash
cp .env.example .env
```

Para executar o projeto no Docker, acesse a pasta raiz do projeto e execute o comando abaixo:

```bash
docker compose up --build -d
```
- O serviço `migracoes` aplica as migrações do banco (Alembic) antes de a API subir.
- A API estará disponível em: http://localhost:8080
- Acesse o Adminer em: http://localhost:8000 (só da própria máquina; o PostgreSQL não fica exposto na rede)

Se você já tinha um volume do banco criado **antes** da revisão de segurança, rode uma vez (faz backup, troca a senha e cria o usuário restrito da API):

```bash
bash scripts/banco/atualizar_banco_existente.sh
```

### Backup do banco

```bash
bash scripts/banco/backup.sh                       # gera backups/simplemark-<data>.dump.gpg
bash scripts/banco/restaurar.sh backups/<arquivo>  # restaura (substitui os dados atuais)
```

Os backups são criptografados com a `BACKUP_SENHA` do `.env` e ficam fora do Git. Copie-os para fora desta máquina.

Para remover os containers em execução:

```bash
docker compose down
```

# Documentação do código

A documentação do backend é gerada com o [Sphinx](https://www.sphinx-doc.org/) a partir das docstrings (padrão Google). Os arquivos de configuração ficam em `docs/`.

### Instalar as dependências (uma vez)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-docs.txt
```

### Gerar a documentação (sempre que o código mudar)

```bash
source .venv/bin/activate
bash docs/gerar_docs.sh        # HTML e PDF (ou: html / pdf)
```

O script recria os `.rst` dos módulos com o `sphinx-apidoc` e roda o `sphinx-build`. Não precisa de banco de dados nem de `.env`.

### Abrir

- HTML: abra `docs/_build/html/index.html` no navegador (`xdg-open docs/_build/html/index.html`).
- PDF: `docs/_build/pdf/SimpleMark.pdf` (gerado com o rinohtype, sem LaTeX).
