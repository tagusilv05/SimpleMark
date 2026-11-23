# Revisão de segurança da camada de banco de dados — Simple Mark

Revisão feita em ambiente local em 22/11/2026, sobre `compose.yaml`, `.env` (só nomes e
propriedades das variáveis — nenhum valor foi copiado para este relatório), histórico do Git,
`backend/database/`, `backend/models/`, `backend/repositories/`, `backend/seed/` e
`backend/services/CadastroService/admin_inicial.py`.

> **Atualização (22/11/2026):** as correções foram aplicadas — ver a coluna "Situação" e a
> seção [Correções aplicadas](#correções-aplicadas) no fim deste relatório.

## Resumo

| # | Achado | Risco | Onde | Situação |
|---|--------|-------|------|----------|
| 1 | Banco e Adminer **publicados na rede** com senha do banco **igual ao nome do usuário**, e essa mesma senha está no histórico público do GitHub | **Alto** | `compose.yaml` (`db`, `adminer`), `.env`, commit `14129b0` (`.env.example`) | ✅ Corrigido |
| 2 | **Dados reais** (e-mails e CPFs válidos) e senhas fixas no seed e no admin inicial, que rodam em **todo start** da API, no mesmo banco de produção | **Alto** | `backend/seed/seed.py`, `backend/services/CadastroService/admin_inicial.py`, `backend/main.py:48-50` | ✅ Corrigido |
| 3 | A API conecta como **superusuário** do PostgreSQL | Médio | `.env` (`DATABASE_URL` usa o `POSTGRES_USER`), `main.py` (`create_all` + `aplicar_migracoes` no start) | ✅ Corrigido |
| 4 | Esquema **sem versionamento** de migrações (`create_all` + `ALTER` avulsos a cada start; o Alembic foi removido) | Médio | `backend/main.py:46-47`, `backend/database/migracoes.py` | ✅ Corrigido |
| 5 | **Sem backup** e sem processo de restauração; anexos e fotos fora de volume | Médio | `compose.yaml`, `backend/uploads/` | ✅ Corrigido (scripts + volume; agendar a rotina é com vocês) |
| 6 | Dados pessoais e **de saúde** sem cuidado extra (sem criptografia de campo, sem política de retenção, `meet_link` é um segredo guardado em texto) | Médio | `backend/models/models.py`, `backend/models/ouvidoria.py` | ⏳ Pendente (decisão do grupo) |
| 7 | Os HMAC dos códigos de login/recuperação usam a `SECRET_KEY`, que não está definida no `.env` (cai no valor padrão público) | Baixo | `backend/core/seguranca.py:102-116`, `backend/core/parametros.py:12` | ✅ Corrigido |
| 8 | Sem `.dockerignore`: o `COPY ./backend` pode levar uploads (dados pessoais) para dentro da imagem | Baixo | `Dockerfile.back` | ✅ Corrigido |
| 9 | `.gitignore` não cobre dumps de banco (`*.sql`, `*.dump`) nem `.env.*` | Baixo | `.gitignore` | ✅ Corrigido |
| — | Queries montadas por concatenação (SQL injection) | — | **Nada encontrado** ✅ | — |
| — | Senhas de usuários em texto puro | — | **Nada encontrado** — Argon2 ✅ | — |
| — | Credenciais do banco escritas no código Python/compose | — | **Nada encontrado** — vêm do `.env`, que está no `.gitignore` ✅ | — |

---

## 1. Credenciais do banco

### O que está certo ✅

- O código lê a conexão só de `DATABASE_URL` (`backend/core/config.py`) e para com erro se ela
  não existir — nenhuma URL/senha escrita em `.py`.
- O `compose.yaml` usa `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}`, `${DATABASE_URL}` — os valores
  ficam no `.env`.
- O `.env` está no `.gitignore` e **nunca foi commitado** (conferido com
  `git log --all -- .env`). O `Dockerfile.back` copia só `./backend`, então o `.env` da raiz não
  entra na imagem.

### Achado 1 — Banco exposto na rede com senha fraca e já publicada — **ALTO**

Três problemas que, juntos, ficam graves:

1. **Senha igual ao usuário.** No `.env` atual, `POSTGRES_PASSWORD` tem o mesmo valor de
   `POSTGRES_USER` (10 caracteres, só letras). É a primeira combinação que qualquer ferramenta
   de ataque testa.
2. **Senha já pública.** O arquivo `.env.example` commitado em `14129b0` (29/09/2026, presente
   nas branches remotas `origin/victor-cadastro-*` e `origin/feature/bloqueio-recuperacao-sessao`)
   tem **exatamente** os mesmos `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` do `.env`
   atual. O arquivo foi apagado depois (`703fb1c`), mas continua no histórico do GitHub.
3. **Banco e Adminer publicados em todas as interfaces** (`compose.yaml`):

   ```yaml
   db:
     ports:
       - "5432:5432"      # PostgreSQL aberto para a rede
   adminer:
     ports:
       - "8000:8080"      # interface web de administração do banco
   ```

   `"5432:5432"` publica em `0.0.0.0`: qualquer máquina na mesma rede (Wi-Fi da faculdade, por
   exemplo) alcança o PostgreSQL e o Adminer. Com a senha do item 1/2, ela entra no banco com
   todos os dados de pacientes.

**Como corrigir**

a) Trocar a senha por uma forte e aleatória (e o `DATABASE_URL` junto):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Num volume que já existe, a variável `POSTGRES_PASSWORD` só vale na primeira criação; troque
também dentro do banco:

```bash
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "ALTER USER \"$POSTGRES_USER\" WITH PASSWORD 'NOVA_SENHA_AQUI';"
```

b) Não publicar o banco; deixar o Adminer só no `localhost` (ou só no `compose.override.yaml`):

```yaml
# antes
  db:
    ports:
      - "5432:5432"
  adminer:
    ports:
      - "8000:8080"

# depois
  db:
    # sem "ports": o backend acessa pela rede interna do Compose (host "db")
  adminer:
    ports:
      - "127.0.0.1:8000:8080"   # só acessível da própria máquina
```

c) Se quiserem um arquivo de exemplo, recriar o `.env.example` **só com valores fictícios**:

```dotenv
POSTGRES_USER=simplemark_app
POSTGRES_PASSWORD=troque-esta-senha
POSTGRES_DB=simplemark
DATABASE_URL=postgresql://simplemark_app:troque-esta-senha@db:5432/simplemark
SECRET_KEY=gere-com-secrets-token_urlsafe
```

> Reescrever o histórico do Git para apagar o commit não adianta muito (forks e clones já têm
> a senha). O que resolve é **trocar a senha**.

---

## 2. Senhas de usuários — ✅ correto

- A senha fica só em `credencial.senha_hash` (`backend/models/acesso.py:26`), gerada por
  `PasswordHash.recommended()` do `pwdlib` = **Argon2id** (`backend/core/seguranca.py`).
  `verify_and_update` também atualiza o hash quando os parâmetros recomendados mudam.
- Nenhuma coluna de senha em texto puro em nenhum modelo (`grep senha backend/models`).
- Os códigos de 6 dígitos (login e recuperação) também não ficam em texto puro: só um HMAC
  (`codigo_hash`), com prazo curto, uso único e bloqueio por tentativas.
- Teste automatizado: `test_senha_nao_e_guardada_em_texto_puro` em
  `backend/tests/test_seguranca.py` confere que o valor guardado começa com `$argon2`.

### Achado 7 — HMAC dos códigos usa a `SECRET_KEY` padrão — **BAIXO**

`calcular_hash_codigo_login` (`backend/core/seguranca.py:115-116`) usa `segredo_jwt()` como
chave. Como o `.env` não define `SECRET_KEY`, a chave é o valor padrão que está no código
(`backend/core/parametros.py:12`). Quem tiver um dump do banco calcula os 1 milhão de HMACs
possíveis em segundos. O risco é baixo porque o código expira em poucos minutos e é de uso
único — mas é mais um motivo para definir `SECRET_KEY` (ver `docs/seguranca.md`, achado 3):

```dotenv
# .env
SECRET_KEY=<saída de: python3 -c "import secrets; print(secrets.token_urlsafe(48))">
```

```yaml
# compose.yaml, serviço backend
      SECRET_KEY: ${SECRET_KEY}
```

---

## 3. Acesso ao banco

### Queries parametrizadas — ✅ correto

Busca em todo o `backend/` por `text(`, `.execute(`, `exec_driver_sql`, `cursor()`, f-strings e
`%`/`.format` montando SQL:

- `repositories/` e `services/` usam só o ORM (`db.query(Modelo).filter(Modelo.campo == valor)`,
  `select()`, `update()`, `delete()`): o SQLAlchemy sempre envia os valores como parâmetros.
- `database/migracoes.py` usa `text()` apenas com DDL **fixo**, sem nenhum dado externo.
- `repositories/busca_profissional.py:65` faz `ilike(f"%{texto}%")`: a f-string monta o *valor*
  do parâmetro, não a SQL — não é injeção (há testes com `' OR '1'='1`, `DROP TABLE` e
  `UNION SELECT` em `backend/tests/test_seguranca.py`).

Regra para o futuro, se precisarem de SQL manual:

```python
# NUNCA
db.execute(text(f"SELECT * FROM usuario WHERE cpf = '{cpf}'"))
# SEMPRE
db.execute(text("SELECT * FROM usuario WHERE cpf = :cpf"), {"cpf": cpf})
```

### Achado 3 — A API usa o superusuário do banco — **MÉDIO**

Na imagem oficial do PostgreSQL, o `POSTGRES_USER` é criado como **superusuário**. O
`DATABASE_URL` do `.env` usa esse mesmo usuário, então a API pode fazer qualquer coisa:
`DROP DATABASE`, ler arquivos do servidor (`COPY ... FROM PROGRAM`), criar outros usuários.
Hoje isso é "necessário" porque a API cria e altera tabelas sozinha a cada start
(`Base.metadata.create_all` e `aplicar_migracoes()` em `main.py:46-47`).

**Impacto:** qualquer falha na API (ou o vazamento da senha do achado 1) vira controle total do
servidor de banco, não só dos dados do app.

**Como corrigir** — separar dois usuários:

- `simplemark_admin` (dono do esquema): usado só para criar/migrar tabelas;
- `simplemark_app` (a API): só lê e grava dados.

```sql
-- rodar uma vez, como superusuário
CREATE ROLE simplemark_app LOGIN PASSWORD 'SENHA_FORTE_AQUI';
GRANT CONNECT ON DATABASE simplemark TO simplemark_app;
GRANT USAGE ON SCHEMA public TO simplemark_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO simplemark_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO simplemark_app;
-- tabelas criadas depois (pelas migrações) também liberadas para a API
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO simplemark_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO simplemark_app;
```

```dotenv
# antes
DATABASE_URL=postgresql://<POSTGRES_USER>:<senha>@db:5432/<db>
# depois
DATABASE_URL=postgresql://simplemark_app:<senha_app>@db:5432/simplemark
MIGRATION_DATABASE_URL=postgresql://simplemark_admin:<senha_admin>@db:5432/simplemark
```

Isso exige tirar o `create_all`/`aplicar_migracoes` do start da API (ver achado 4) — as
migrações passam a rodar com `MIGRATION_DATABASE_URL`, num passo separado.

---

## 4. Dados sensíveis

### Achado 6 — Dados pessoais e de saúde sem cuidado extra — **MÉDIO**

O que o banco guarda (`backend/models/`):

| Categoria (LGPD) | Tabela.coluna | Observação |
|------------------|---------------|------------|
| Identificação | `usuario.nome`, `cpf`, `orgao_emissor`, `data_nascimento`, `genero` | CPF e data de nascimento permitem fraude de identidade |
| Contato | `usuario.email`, `telefone`; `endereco.*` (CEP, logradouro, número, complemento) | |
| **Saúde — dado sensível (art. 5º, II e art. 11)** | `consulta` (com quem e em qual especialidade), `atestado.cid`, `atestado.dias_afastamento`, `receita_medicamento.*`, `documento_clinico.observacoes`, `avaliacao.feedback` | CID e medicamentos revelam diagnóstico |
| Texto livre / arquivos | `manifestacao_ouvidoria.descricao`, `anexo_ouvidoria` (arquivos em `uploads/ouvidoria`) | Pode conter qualquer coisa, inclusive laudos |
| Segredos de acesso | `consulta.meet_link` | Quem tem o link entra na sala da teleconsulta |
| Autenticação | `credencial.senha_hash`, `codigo_login.codigo_hash`, `sessao_login` | Já protegidos com hash/HMAC ✅ |
| Fotos | `profissional.path_imagem` (arquivo em `uploads/profissionais`) | Pública por design |
| Consentimento | `credencial.consentimento_lgpd`, `manifestacao_ouvidoria.aceite_lgpd` | Bom: o aceite é registrado ✅ |

**O que falta / como melhorar** (em ordem de custo-benefício):

1. **Acesso restrito ao banco** — achados 1 e 3. É a proteção que mais importa: hoje quem
   entra no banco vê tudo em texto claro.
2. **Backups criptografados** — achado 5 (um dump é uma cópia de todos esses dados).
3. **Criptografia de campo nos dados de saúde mais sensíveis** (`atestado.cid`,
   `receita_medicamento.medicamento/posologia`, `documento_clinico.observacoes`) — protege
   contra dump e contra quem tem acesso de leitura ao banco. Exemplo com `cryptography`:

   ```python
   # core/criptografia.py
   import os
   from cryptography.fernet import Fernet
   from sqlalchemy.types import TypeDecorator, Text

   _fernet = Fernet(os.environ["CHAVE_DADOS_SAUDE"])  # gerada com Fernet.generate_key()

   class TextoCriptografado(TypeDecorator):
       impl = Text
       cache_ok = True

       def process_bind_param(self, valor, dialeto):
           return None if valor is None else _fernet.encrypt(valor.encode()).decode()

       def process_result_value(self, valor, dialeto):
           return None if valor is None else _fernet.decrypt(valor.encode()).decode()
   ```

   ```python
   # models/models.py — antes
   cid = Column(String(10), nullable=True)
   # depois
   cid = Column(TextoCriptografado, nullable=True)
   ```

   (Exige migrar os dados existentes; colunas criptografadas não podem ser usadas em `WHERE`.)
4. **Política de retenção e exclusão.** Definir por quanto tempo cada dado fica e o que a
   exclusão da conta apaga. Atenção: prontuário/documentos médicos têm prazo legal de guarda
   (Resolução CFM nº 1.821/2007 fala em 20 anos), então "excluir conta" provavelmente deve
   **anonimizar** o usuário e manter os documentos clínicos, em vez de apagar tudo — vale
   confirmar com o professor.
5. **`meet_link`**: já é gerado com `secrets.token_urlsafe` (imprevisível ✅) e escondido da API
   quando a consulta é cancelada. Como é um segredo de acesso, apagar o link (`NULL`) depois da
   consulta realizada/cancelada reduz o que um dump expõe.
6. **Conexão com TLS** (`?sslmode=require` no `DATABASE_URL`) se um dia o banco ficar em outra
   máquina; dentro da rede interna do Docker não é necessário.

---

## 5. Migrações, dados de teste e backups

### Achado 4 — Esquema sem versionamento — **MÉDIO**

O esquema é criado por `Base.metadata.create_all(bind=engine)` e ajustado por
`aplicar_migracoes()` (`backend/main.py:46-47`), que roda **a cada start** uma lista de
`ALTER TABLE ... IF NOT EXISTS` / `DROP COLUMN IF EXISTS` em `backend/database/migracoes.py`.
O projeto começou com Alembic (`alembic.ini` e `alembic/` no commit `14129b0`), que foi removido.

**Riscos:**

- não há registro de **qual versão** do esquema cada banco tem, nem como voltar atrás;
- `create_all` não altera tabelas existentes — colunas novas em modelos não chegam a bancos
  antigos se alguém esquecer de escrever o `ALTER` à mão;
- `DROP COLUMN` e `UPDATE` em massa rodando automaticamente a cada start: um erro numa linha
  apaga dados em produção sem ninguém pedir;
- obriga a API a ter permissão de DDL (achado 3).

**Como corrigir** — voltar com o Alembic:

```bash
pip install alembic
cd backend && alembic init alembic
```

```python
# backend/alembic/env.py
from core.config import DATABASE_URL
from database.connection import Base
import models.models, models.acesso, models.administracao, models.ouvidoria, models.recuperacao_senha  # noqa

config.set_main_option("sqlalchemy.url", os.getenv("MIGRATION_DATABASE_URL", DATABASE_URL))
target_metadata = Base.metadata
```

```bash
alembic revision --autogenerate -m "esquema inicial"   # revisar o arquivo gerado!
alembic stamp head        # em bancos que já existem (marca como atualizados)
alembic upgrade head      # em bancos novos / a cada deploy
```

```python
# backend/main.py — antes
Base.metadata.create_all(bind=engine)
aplicar_migracoes()
criar_admin_inicial()
criar_seed()

# depois: o esquema é responsabilidade do "alembic upgrade head" (passo de deploy)
criar_admin_inicial()
if os.getenv("AMBIENTE") == "desenvolvimento":
    criar_seed()
```

Os testes não são afetados: eles já criam as tabelas com `create_all` no SQLite em memória
(`backend/tests/conftest.py`).

### Achado 2 — Dados reais e senhas fixas no seed e no admin inicial — **ALTO**

- `backend/seed/seed.py` cria um paciente e um profissional com **e-mails reais de integrantes**
  (Gmail e Outlook), **CPFs com dígito verificador válido** (podem pertencer a pessoas reais),
  telefones e uma **senha fixa** escrita na própria docstring.
- `backend/services/CadastroService/admin_inicial.py:17-19` cria o administrador com **e-mail
  real**, **CPF válido** e **senha fixa fraca** (`SENHA_ADMIN`).
- `main.py:48-50` chama `criar_admin_inicial()` e `criar_seed()` **sempre que a API sobe**, sem
  olhar o ambiente: o banco "de verdade" recebe contas de teste com senha conhecida, e o código
  público expõe dados pessoais de pessoas reais.

**Como corrigir:**

```python
# antes (admin_inicial.py)
EMAIL_ADMIN = "<e-mail real>"
SENHA_ADMIN = "<senha fixa>"
CPF_ADMIN = "<CPF real>"

# depois
EMAIL_ADMIN = os.getenv("ADMIN_EMAIL")
SENHA_ADMIN = os.getenv("ADMIN_SENHA")
CPF_ADMIN = os.getenv("ADMIN_CPF")
# e criar_admin_inicial() não faz nada se alguma delas faltar
```

```python
# antes (seed.py)
email="<e-mail real de integrante>",
cpf="<CPF válido>",

# depois — dados claramente fictícios
email="paciente.teste@example.com",   # domínio reservado para exemplos (RFC 2606)
cpf="000.000.001-91",                 # gerado para teste; nunca CPF de alguém
```

```python
# antes (main.py)
criar_seed()
# depois
if os.getenv("AMBIENTE") == "desenvolvimento":
    criar_seed()
```

Depois: trocar a senha das contas do seed e do admin que já existem nos bancos, e (opcional)
apagar as contas de seed do banco usado na apresentação.

O que já está certo nos **testes automatizados** ✅: usam SQLite em memória (`sqlite://`), nunca
tocam no banco do Docker, e o admin inicial é desligado com `AMBIENTE=teste`.

### Achado 5 — Sem backup e sem restauração testada — **MÉDIO**

Não há script, serviço nem documentação de backup. Os dados vivem só no volume Docker
`postgres_data`: um `docker compose down -v`, um disco corrompido ou um `DROP` acidental (achado 4)
perde tudo. Além disso, os anexos da Ouvidoria e as fotos dos profissionais ficam em
`backend/uploads/` **dentro do container**, sem volume — somem a cada rebuild da imagem.

**Como corrigir:**

```bash
# backup (rodar diariamente, por exemplo via cron)
mkdir -p backups
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
  | gpg --symmetric --cipher-algo AES256 -o "backups/simplemark-$(date +%F).dump.gpg"

# restauração (testar de vez em quando num banco vazio!)
gpg -d backups/simplemark-AAAA-MM-DD.dump.gpg \
  | docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean
```

- guardar os backups **fora** da máquina do servidor e **fora do Git** (achado 9);
- volume para os uploads:

  ```yaml
  backend:
    volumes:
      - uploads_data:/code/uploads
  volumes:
    postgres_data:
    uploads_data:
  ```

### Achado 8 — Sem `.dockerignore` — **BAIXO**

`Dockerfile.back` faz `COPY ./backend .` sem `.dockerignore`. Se houver arquivos em
`backend/uploads/` (anexos da Ouvidoria, fotos), um `.env` local ou um dump dentro de `backend/`
na hora do build, eles vão para dentro da imagem. Hoje `backend/uploads/` está vazio.

```gitignore
# .dockerignore (na raiz do projeto)
.env
.env.*
**/__pycache__
**/.pytest_cache
backend/uploads/
backups/
*.sql
*.dump
*.dump.gpg
frontend/node_modules
```

### Achado 9 — `.gitignore` não cobre dumps nem variações do `.env` — **BAIXO**

O `.gitignore` ignora `.env` e `backend/uploads/ouvidoria/`, mas não `backend/uploads/profissionais/`,
`.env.local`/`.env.producao` nem arquivos de backup. Sugestão de acréscimo:

```gitignore
# antes
.env
backend/uploads/ouvidoria/

# depois
.env
.env.*
!.env.example
backend/uploads/
backups/
*.sql
*.dump
*.dump.gpg
```

---

## Ordem sugerida

1. **Trocar a senha do banco** e tirar o `5432` (e o Adminer) da rede — achado 1.
2. Tirar dados reais e senhas fixas do seed/admin e rodar o seed só em desenvolvimento — achado 2.
3. Definir `SECRET_KEY` no `.env` — achado 7 (e achado 3 de `docs/seguranca.md`).
4. Usuário do banco só com permissão de dados + Alembic — achados 3 e 4 (andam juntos).
5. Backup automático e volume para os uploads — achado 5.
6. Criptografia de campo e política de retenção — achado 6, se houver tempo.

---

## Correções aplicadas

Todas testadas num PostgreSQL descartável (banco novo **e** banco criado do jeito antigo) e
depois aplicadas no volume local `simplemark_postgres_data`, com backup antes. A suíte de
testes do backend continua passando (298 passaram, 9 `xfail` já conhecidos).

| Achado | O que foi feito | Arquivos |
|--------|-----------------|----------|
| 1 | Senha do dono do banco trocada por uma aleatória de 43 caracteres (no `.env` **e** no banco, com `ALTER ROLE`); porta 5432 não é mais publicada; Adminer só em `127.0.0.1:8000`; `.env.example` recriado só com valores fictícios | `compose.yaml`, `.env`, `.env.example` |
| 2 | Admin inicial lê `ADMIN_EMAIL`/`ADMIN_SENHA`/`ADMIN_CPF` do `.env` e não faz nada se faltarem; seed com dados fictícios (`@example.com`, CPFs de teste, senha de `SEED_SENHA`) e só com `AMBIENTE=desenvolvimento`; exemplos do Swagger e do `README_VIDEOCHAMADA.md` sem o e-mail real | `admin_inicial.py`, `seed/seed.py`, `main.py`, `routers/auth.py`, `routers/cadastro.py`, `README_VIDEOCHAMADA.md` |
| 3 | Novo usuário `simplemark_app` só com `SELECT/INSERT/UPDATE/DELETE` (sem superusuário, sem DDL, sem acesso a `alembic_version`); a API usa `DATABASE_URL` com ele; o dono só é usado pelas migrações (`MIGRATION_DATABASE_URL`) | `banco/sql/usuario_app.sql`, `banco/init/01-usuario-app.sh`, `scripts/banco/atualizar_banco_existente.sh`, `compose.yaml` |
| 4 | Alembic de volta: migração `0001` gerada dos modelos; em banco antigo ela só aplica os ajustes do `migracoes.py` e marca a versão. Serviço `migracoes` no compose roda `alembic upgrade head` antes do backend. `create_all` e `database/migracoes.py` saíram do start da API | `backend/alembic.ini`, `backend/alembic/`, `backend/main.py`, `compose.yaml`, `requirements.txt` |
| 5 | `backup.sh` (pg_dump + GPG AES-256 com `BACKUP_SENHA`) e `restaurar.sh` (com confirmação e reaplicação das permissões); volume `uploads_data` para fotos e anexos | `scripts/banco/`, `compose.yaml` |
| 7 | `SECRET_KEY` aleatória no `.env` e repassada pelo compose (o backend não sobe sem ela) | `.env`, `compose.yaml` |
| 8 | `.dockerignore` criado | `.dockerignore` |
| 9 | `.gitignore` cobre `.env.*`, `backend/uploads/`, `backups/`, `*.sql`, `*.dump*` | `.gitignore` |

**Verificado no banco local depois da aplicação:** a senha antiga é recusada; a nova funciona;
o usuário da API lê e grava dados, mas recebe `permission denied` ao criar tabela, `must be owner`
ao apagar tabela e `permission denied` ao alterar `alembic_version`; `alembic current` = `0001`.

**Não aplicado (precisa de decisão do grupo):**

- **Achado 6** — criptografia de campo nos dados de saúde e política de retenção. Exige escolher
  onde guardar a chave, migrar os dados existentes e definir com o professor o que a exclusão de
  conta faz com documentos clínicos (prazo legal de guarda). O exemplo de código continua acima.
- **Colunas antigas** `pagamento.id_transacao` e `pagamento.metodo` existem no banco local mas
  não nos modelos (o `alembic check` aponta). São opcionais (aceitam `NULL`) e não atrapalham; 1
  pagamento tem dados nelas. Se não forem mais usadas, criem uma migração para removê-las:
  `alembic revision --autogenerate -m "remove colunas antigas de pagamento"`.
- **Contas do seed antigo** (com os e-mails reais) continuam no banco local; o seed novo cria
  contas `@example.com` separadas. Apaguem as antigas se não precisarem delas.
- A **senha atual da conta de administrador** que já existe no banco não muda com o `.env`
  (`ADMIN_SENHA` só vale quando a conta é criada): troquem-na pela tela "Minha conta".
- Achado 7 do `docs/seguranca.md` sobre o mesmo tema (senha fixa no código) também ficou
  resolvido pelo item 2 acima.
