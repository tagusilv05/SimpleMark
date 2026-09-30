<!-- Arquivo criado por Victor -->
# Simple Mark

Cadastro de paciente e de profissional de saúde, login e autenticação dos três perfis. Não há cadastro de administrador: na subida da API a conta da Helena é gravada no banco se ainda não existir (`nordestino1971@gmail.com` / `Senha123`).

O identificador do login pode ser o e-mail ou o CPF.

## Como executar

Na pasta do projeto, com o ambiente virtual já criado:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
docker compose up -d
.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

O PostgreSQL sobe pelo Docker, na porta 5432, com usuário, senha e banco `simplemark`.

Para ver as tabelas no navegador, abra o Adminer em `http://127.0.0.1:8081`. Sistema: PostgreSQL. Servidor: `postgres`. Usuário, senha e banco: `simplemark`.

Os testes desta parte:

```powershell
.\venv\Scripts\python.exe -m pytest
```

## Rotas

| Método | Caminho | Quem acessa |
| --- | --- | --- |
| POST | `/api/v1/cadastro/paciente` | Público |
| POST | `/api/v1/cadastro/profissional` | Público. A conta fica inativa até o administrador validar |
| POST | `/api/v1/auth/login` | Público. E-mail ou CPF, mais a senha. Vale para paciente, profissional de saúde já validado e administrador |
| GET | `/api/v1/auth/eu` | Autenticado. Confere o token e devolve o perfil |
| GET | `/api/v1/administracao/profissionais/pendentes` | Administrador |
| POST | `/api/v1/administracao/profissionais/{id_profissional}/validar` | Administrador |

## Organização

- `app/api`: rotas de cadastro, login e autenticação
- `app/services`: regras de cadastro e de login
- `app/repositories`: consultas ao banco
- `app/models`: tabelas
- `app/schemas`: entrada e saída da API
- `app/core`: configuração, sessão do banco, senha e token
