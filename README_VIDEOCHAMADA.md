# SimpleMark — Videochamada com Jitsi Meet

Integração do backend do SimpleMark com o [Jitsi Meet](https://jitsi.org/jitsi-meet/). Para cada teleconsulta, o sistema:

- gera o link da sala **no próprio backend**, sem chamar nenhuma API externa;
- guarda o link no banco (um link por consulta, que nunca é trocado);
- mostra o link pela API **somente** ao médico responsável e ao paciente da consulta;
- envia o link por e-mail ao paciente.

No reagendamento, **o link continua o mesmo** e o paciente recebe um e-mail com a data antiga e a nova. No cancelamento, o link deixa de ser exibido e o paciente é avisado por e-mail.

> Escopo: apenas backend. Nenhum arquivo de frontend foi criado ou alterado.
>
> Esta integração substitui a do Google Meet (`README_GOOGLE_MEET.md`, removido). O Jitsi não exige conta paga, credenciais nem API.

---

## Sumário

1. [Como funciona](#como-funciona)
2. [O nome da sala e a segurança](#o-nome-da-sala-e-a-segurança)
3. [Arquivos criados, alterados e removidos](#arquivos-criados-alterados-e-removidos)
4. [Banco de dados (migration)](#banco-de-dados-migration)
5. [Endpoints](#endpoints)
6. [Variáveis de ambiente](#variáveis-de-ambiente)
7. [Testando os e-mails com o Mailpit](#testando-os-e-mails-com-o-mailpit)
8. [Teste manual pelo Swagger (passo a passo)](#teste-manual-pelo-swagger-passo-a-passo)
9. [E-mails enviados ao paciente](#e-mails-enviados-ao-paciente)
10. [Um link por consulta, falhas e retentativas](#um-link-por-consulta-falhas-e-retentativas)
11. [LGPD e logs](#lgpd-e-logs)
12. [Testes](#testes)
13. [Decisões tomadas e pontos para validar](#decisões-tomadas-e-pontos-para-validar)

---

## Como funciona

```
POST /consulta/confirmar-consulta
        │
        ├─► grava a consulta (como antes)
        ├─► gera o link na mesma requisição:  JITSI_BASE_URL/simplemark-<aleatório>
        │     (sem rede: só secrets.token_urlsafe)
        │
        │  resposta imediata, sem mudança no formato
        ▼
 Tarefa em segundo plano (FastAPI BackgroundTasks)
        └─► e-mail de confirmação ao paciente (SMTP, até 3 tentativas)
```

- **Geração síncrona.** Gerar o link é só sortear um nome de sala. Não há chamada externa que possa falhar ou demorar, então o link nasce junto com a consulta. Só o e-mail fica em segundo plano.
- **Sem status de integração.** Os estados `pendente`, `gerado` e `erro` só existiam porque o Google podia falhar. Agora a consulta ativa tem link ou ganha um na hora. O campo `status_integracao_meet` foi removido da API e do banco.
- **Link sob demanda.** Consultas criadas antes desta integração, ou cujo link não chegou a ser gravado, ganham o link:
  - quando o médico ou o paciente chamam `GET /api/v1/consultas/{id}/videochamada` (o paciente recebe o e-mail com o link);
  - pelo `POST .../videochamada/reprocessar`;
  - no reagendamento;
  - na própria tarefa do e-mail de confirmação.
- **Fuso:** datas e horas nos e-mails estão em `America/Sao_Paulo`.

---

## O nome da sala e a segurança

No Jitsi, **qualquer pessoa que souber o nome da sala consegue entrar**. Por isso:

- O nome é `simplemark-` + `secrets.token_urlsafe(16)`. São 16 bytes aleatórios (128 bits), escritos em 22 caracteres. Exemplo: `https://meet.jit.si/simplemark-3q2Xh0b9vKc4mWf1ZpL7Ag`.
- O nome **não leva** id da consulta, nome do paciente, nome do médico, especialidade, data ou qualquer outro dado.
- O link só é devolvido ao médico responsável e ao paciente da consulta. Para qualquer outra pessoa, a API responde 404.
- O banco tem índice único em `meet_link`: duas consultas nunca compartilham a mesma sala.

### Cancelamento: a sala não é "fechada"

O Jitsi público (`meet.jit.si`) não permite fechar nem bloquear uma sala pelo backend: ela existe enquanto alguém estiver dentro. Ao cancelar uma consulta, a proteção é:

1. o link **deixa de ser devolvido** pela API (`meet_link: null` em todas as rotas);
2. o e-mail de cancelamento **não inclui** o link;
3. o nome da sala é imprevisível. Quem não recebeu o link antes não tem como descobri-lo.

O link continua gravado no banco, para auditoria, mas não é mais exibido. Quem já tinha o link (o médico e o paciente) ainda conseguiria abrir a sala. Para impedir isso de fato, seria preciso um servidor Jitsi próprio com autenticação (JWT ou lobby), o que fica para o futuro e não exige mudar o código além de `JITSI_BASE_URL` e da autenticação.

---

## Arquivos criados, alterados e removidos

Todos os caminhos são relativos a `backend/`, exceto os marcados com *(raiz)*.

### Removidos

| Arquivo | Motivo |
|---|---|
| `services/google_calendar.py` | Cliente do Google Calendar; não é mais usado |
| `README_GOOGLE_MEET.md` *(raiz)* | Substituído por este arquivo |

### Criados

| Arquivo | Responsabilidade |
|---|---|
| `README_VIDEOCHAMADA.md` *(raiz)* | Esta documentação |

### Alterados (em relação à versão com Google Meet)

| Arquivo | Alteração |
|---|---|
| `core/integracoes.py` | Saem `GOOGLE_*` e `CONSULTA_DURACAO_PADRAO_MINUTOS`; entra `JITSI_BASE_URL`. SMTP e retentativas continuam |
| `services/videochamada.py` | Geração local do link, geração sob demanda, e-mails em segundo plano; sai toda a sincronização com o Google |
| `services/envio_email.py` | Texto "Link da videochamada (Google Meet)" passa a "Link da videochamada" |
| `repositories/videochamada.py` | A trava (`FOR UPDATE`) passa a reler a linha (`populate_existing`); sai `marcar_status_integracao` |
| `schemas/videochamada.py` | Sai `status_integracao_meet` |
| `routers/videochamada.py` | GET gera o link sob demanda; reprocessar aceita qualquer consulta ativa e reenvia o e-mail |
| `routers/confirmar_consulta.py` | Gera o link na requisição e só o e-mail vai para segundo plano (a resposta não mudou) |
| `schemas/consulta_paciente.py`, `services/consulta_paciente.py` | Sai `status_integracao_meet`; `meet_link` continua |
| `models/models.py` | Saem `google_event_id`, `status_integracao_meet` e o CHECK; entra o índice único `ix_consulta_meet_link` |
| `database/migracoes.py` | Remove as colunas do Google, limpa links antigos do Meet e cria o índice único |
| `tests/test_videochamada.py` | Reescrito sem o Google (26 testes) |
| `requirements.txt` *(raiz)* | Saem `google-api-python-client` e `google-auth` |
| `compose.yaml` *(raiz)* | Saem as variáveis do Google; entram `JITSI_BASE_URL` e o serviço `mailpit` |

Inalterados desde a versão anterior: `main.py` e `tests/conftest.py` (o router continua registrado em `/api/v1`).

**Nenhuma biblioteca nova.** O link usa `secrets` e o e-mail usa `smtplib` e `email`, todos da biblioteca padrão do Python.

---

## Banco de dados (migration)

O projeto não usa Alembic. Tabelas novas são criadas pelo `create_all`, e as mudanças em tabelas existentes ficam em `database/migracoes.py`. Esse arquivo é idempotente: roda a cada inicialização e só no PostgreSQL.

Colunas de videochamada na tabela `consulta`:

| Coluna | Tipo | Descrição |
|---|---|---|
| `meet_link` | `VARCHAR(255)`, nulo, **índice único** `ix_consulta_meet_link` | Link da sala no Jitsi |
| `data_geracao_link` | `TIMESTAMP WITH TIME ZONE`, nulo | Quando o link foi gerado (UTC) |

### Por que o campo continua `meet_link`

Renomear para `link_videochamada` exigiria um `RENAME COLUMN` condicional na migration e mudaria o nome do campo na API (`/videochamada` e `/consultas/minhas`). O ganho seria só o nome. "Meet" também é parte do nome "Jitsi Meet", então o campo continua descrevendo o que guarda.

### O que a migration faz

1. `ADD COLUMN IF NOT EXISTS meet_link` e `data_geracao_link` (bancos anteriores à videochamada).
2. `DROP INDEX IF EXISTS ix_consulta_google_event_id` e `DROP COLUMN IF EXISTS google_event_id`.
3. `DROP CONSTRAINT IF EXISTS ck_consulta_status_integracao_meet` e `DROP COLUMN IF EXISTS status_integracao_meet`.
4. Apaga links antigos do Google (`meet_link LIKE 'https://meet.google.com/%'`). Essas consultas ganham link do Jitsi sob demanda.
5. `CREATE UNIQUE INDEX IF NOT EXISTS ix_consulta_meet_link`.

**Por que remover em vez de só ignorar `google_event_id` e `status_integracao_meet`:** os valores só tinham sentido no Google, que não é mais usado. Além disso, `status_integracao_meet` era `NOT NULL` com CHECK, e uma coluna órfã confundiria quem lesse o banco.

A migration foi validada num PostgreSQL real, rodando duas vezes seguidas em cada cenário:

- banco com as colunas e o índice do Google, com uma consulta `gerado` (link do Meet) e uma `pendente`;
- banco anterior à videochamada;
- banco novo.

Nos três casos, o resultado final é o mesmo: só `meet_link` e `data_geracao_link`, com o índice único, e nenhum link do Google.

---

## Endpoints

Os endpoints de videochamada:

- exigem `Authorization: Bearer <token>`;
- ficam sob o prefixo `/api/v1`;
- respondem erros no formato `{"mensagem": "..."}`;
- aparecem no Swagger em `/docs`.

### `GET /api/v1/consultas/{id_consulta}/videochamada` (alterado)

Retorna o link. Acesso do **médico responsável** e do **paciente** da consulta. Qualquer outra pessoa recebe **404**, sem revelar se a consulta existe.

**Novo:** se a consulta estiver ativa e ainda não tiver link (consulta antiga), o link é gerado nesta chamada e o paciente recebe o e-mail de confirmação em segundo plano. As próximas chamadas devolvem o mesmo link e não enviam e-mail de novo.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/consultas/12/videochamada
```

Resposta `200`:

```json
{
  "id_consulta": 12,
  "data": "2026-11-05",
  "hora": "14:00:00",
  "status_consulta": "agendada",
  "meet_link": "https://meet.jit.si/simplemark-3q2Xh0b9vKc4mWf1ZpL7Ag",
  "data_geracao_link": "2026-10-14T17:02:11Z"
}
```

`meet_link` vem `null` se a consulta foi cancelada, ou se foi realizada sem nunca ter tido link. O campo `status_integracao_meet` foi **removido**.

### `POST /api/v1/consultas/{id_consulta}/videochamada/reprocessar` (alterado)

Garante o link e **reenvia ao paciente o e-mail de confirmação** em segundo plano. Aceito para o médico ou o paciente de uma consulta **ativa**.

- Se a consulta não tem link, o link é gerado.
- Se já tem, o link é mantido (nunca é trocado).

Antes, este endpoint só funcionava com status `erro`. Agora cobre consultas antigas e e-mails que não chegaram. O corpo da requisição é vazio.

Resposta `202`:

```json
{
  "mensagem": "Link da videochamada garantido. O e-mail ao paciente será reenviado.",
  "consulta": {
    "id_consulta": 12,
    "data": "2026-11-05",
    "hora": "14:00:00",
    "status_consulta": "agendada",
    "meet_link": "https://meet.jit.si/simplemark-3q2Xh0b9vKc4mWf1ZpL7Ag",
    "data_geracao_link": "2026-10-14T17:02:11Z"
  }
}
```

| Código | Situação |
|---|---|
| `400` | Consulta cancelada ou realizada |
| `404` | Consulta inexistente ou de outra pessoa |

O `409` ("status diferente de erro") deixou de existir.

### `PATCH /api/v1/consultas/{id_consulta}/reagendar` (comportamento interno alterado)

**Somente o médico responsável.** Move a consulta para um horário livre da agenda do profissional.

- **O link continua o mesmo.** Se a consulta ainda não tinha link, ele é gerado agora.
- Em segundo plano, o paciente recebe um e-mail com a data antiga, a nova e o link.

Request:

```json
{ "data": "2026-11-05", "hora": "16:00:00" }
```

Resposta `200`:

```json
{
  "mensagem": "Consulta reagendada com sucesso.",
  "consulta": {
    "id_consulta": 12,
    "data": "2026-11-05",
    "hora": "16:00:00",
    "status_consulta": "agendada",
    "meet_link": "https://meet.jit.si/simplemark-3q2Xh0b9vKc4mWf1ZpL7Ag",
    "data_geracao_link": "2026-10-14T17:02:11Z"
  }
}
```

| Código | Situação |
|---|---|
| `403` | Quem pediu é o paciente, não o profissional da consulta |
| `400` | Consulta cancelada ou realizada; data/hora iguais às atuais; data no passado; horário inexistente na agenda (`data_horario`) |
| `409` | Novo horário já ocupado por outra consulta |
| `404` | Consulta inexistente ou de outra pessoa |

### `PATCH /api/v1/consultas/{id_consulta}/cancelar` (comportamento interno alterado)

Cancela a consulta (status `cancelada`). Aceito para o **médico ou o paciente** da consulta.

- O link deixa de ser devolvido pela API.
- Em segundo plano, o paciente recebe um e-mail de cancelamento, **sem o link**.
- O corpo da requisição é vazio.

Resposta `200`:

```json
{
  "mensagem": "Consulta cancelada com sucesso.",
  "consulta": {
    "id_consulta": 12,
    "data": "2026-11-05",
    "hora": "14:00:00",
    "status_consulta": "cancelada",
    "meet_link": null,
    "data_geracao_link": "2026-10-14T17:02:11Z"
  }
}
```

| Código | Situação |
|---|---|
| `400` | Consulta já cancelada ou já realizada |
| `404` | Consulta inexistente ou de outra pessoa |

### Endpoints existentes

**`POST /consulta/confirmar-consulta`**: mesma entrada e mesma resposta (`{"mensagem": "Consulta confirmada com sucesso", "id_consulta": 12}`). Agora o link é gravado antes da resposta, e só o e-mail vai para segundo plano. Se gravar o link falhar por algum motivo, a consulta não é desfeita: o link é gerado na tarefa do e-mail ou na primeira consulta ao link.

**`GET /consultas/minhas`** e **`GET /consultas/minhas/{id_consulta}`** (paciente): continuam trazendo `meet_link` (`null` se a consulta foi cancelada ou ainda não tem link). O campo `status_integracao_meet` foi **removido**.

**`GET /consultas_profissionais/{id_profissional}/consultas`**: não foi alterado e não traz o link, porque não tem autenticação. O médico obtém o link pelo `GET /api/v1/consultas/{id}/videochamada`.

---

## Variáveis de ambiente

Coloque no `.env` da raiz. O `compose.yaml` repassa todas ao container do backend.

```bash
# --- Videochamada (Jitsi Meet) ---
# Servidor onde as salas são abertas. Para usar um Jitsi próprio no futuro,
# basta trocar este valor (ex.: https://videochamada.seudominio.com.br).
JITSI_BASE_URL=https://meet.jit.si

# Tentativas de envio de cada e-mail e espera inicial do backoff (segundos)
VIDEOCHAMADA_TENTATIVAS=3
VIDEOCHAMADA_BACKOFF_SEGUNDOS=2

# --- E-mail (SMTP) ---
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USUARIO=agenda@seudominio.com.br
SMTP_SENHA=senha-de-app
SMTP_REMETENTE="SimpleMark <agenda@seudominio.com.br>"
SMTP_USAR_TLS=true      # STARTTLS (porta 587)
SMTP_SSL=false          # true para SSL direto (porta 465)
```

| Variável | Obrigatória | Padrão |
|---|---|---|
| `JITSI_BASE_URL` | Não | `https://meet.jit.si` |
| `VIDEOCHAMADA_TENTATIVAS` | Não | `3` |
| `VIDEOCHAMADA_BACKOFF_SEGUNDOS` | Não | `2` |
| `SMTP_HOST` | Sim, para enviar e-mail | — |
| `SMTP_PORT` | Não | `587` |
| `SMTP_USUARIO` / `SMTP_SENHA` | Se o servidor exigir login | — |
| `SMTP_REMETENTE` | Não | valor de `SMTP_USUARIO` |
| `SMTP_USAR_TLS` | Não | `true` |
| `SMTP_SSL` | Não | `false` |

**Removidas:**

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_SERVICE_ACCOUNT_FILE`
- `GOOGLE_CALENDAR_DELEGATED_USER`
- `GOOGLE_CALENDAR_ID`
- `CONSULTA_DURACAO_PADRAO_MINUTOS`

Se ainda estiverem no seu `.env`, podem ser apagadas.

> Sem `SMTP_HOST`, o link continua sendo gerado normalmente. Só o envio do e-mail falha, e a falha fica registrada em log.

---

## Testando os e-mails com o Mailpit

O [Mailpit](https://mailpit.axllent.org/) é um servidor SMTP falso: ele recebe os e-mails e os mostra numa caixa de entrada web, **sem entregar nada** a ninguém. Ele já está no `compose.yaml`:

| Porta | Uso |
|---|---|
| `1025` | SMTP (onde o backend envia) |
| `8025` | Caixa de entrada web: http://localhost:8025 |

### `.env` com o backend no Docker (`docker compose up`)

```bash
SMTP_HOST=mailpit        # nome do serviço no compose
SMTP_PORT=1025
SMTP_USAR_TLS=false      # o Mailpit não tem STARTTLS por padrão
SMTP_SSL=false
SMTP_USUARIO=            # sem login
SMTP_SENHA=
SMTP_REMETENTE="SimpleMark <nao-responda@simplemark.local>"
```

### `.env` com o backend fora do Docker (`uvicorn` local)

Use as mesmas variáveis, com `SMTP_HOST=localhost`. Suba só o Mailpit com `docker compose up -d mailpit`.

### Roteiro de teste

1. `docker compose up --build`
2. Confirme uma consulta (`POST /consulta/confirmar-consulta`).
3. Abra http://localhost:8025: o e-mail "Sua teleconsulta está confirmada" aparece com o link `https://meet.jit.si/simplemark-...`.
4. Reagende (`PATCH .../reagendar`) e cancele (`PATCH .../cancelar`): aparecem os e-mails de reagendamento (com a data antiga e a nova e o mesmo link) e de cancelamento (sem link).

> `SMTP_USAR_TLS=false` é importante: com o padrão `true`, o backend tenta STARTTLS, o Mailpit recusa e o envio falha após as 3 tentativas, o que aparece no log. Em produção, mantenha `true`.

---

## Teste manual pelo Swagger (passo a passo)

Roteiro para testar a videochamada inteira pelo navegador, do cadastro ao cancelamento, usando:

- o **Swagger**: http://localhost:8080/docs
- o **Mailpit**: http://localhost:8025
- o **Adminer**: http://localhost:8000 (só para descobrir um id e, no fim, apagar os dados de teste)

Os usuários do seed não têm senha, então o roteiro cria os seus próprios: um paciente, um médico e um "outro paciente" para testar o bloqueio de acesso.

### Antes de começar

1. Configure o `.env` para o Mailpit, como em [Testando os e-mails com o Mailpit](#testando-os-e-mails-com-o-mailpit).
2. Suba tudo com `docker compose up --build` e espere aparecer `Uvicorn running` no log.
3. Abra http://localhost:8080/docs e http://localhost:8025 em abas separadas.

### Como usar o Swagger

- **Executar uma rota:** clique na rota para abrir, depois em **Try it out**. Edite o corpo (Request body) ou os parâmetros e clique em **Execute**. A resposta aparece logo abaixo, em **Server response**.
- **Entrar como um usuário:** clique no botão **Authorize** (cadeado, no topo da página), cole **só o token**, sem a palavra `Bearer`, e clique em **Authorize** e depois em **Close**.
- **Trocar de usuário:** abra o **Authorize**, clique em **Logout** e cole o token do outro usuário.

Ao longo do roteiro, **anote** os valores marcados com 📝. Eles são usados nos passos seguintes.

> Use datas no futuro. Os exemplos usam `2026-12-01`; se essa data já tiver passado, troque por outra em **todos** os passos.

### Passo 1: cadastrar o paciente

**Cadastro → `POST /api/v1/cadastro/paciente`**

```json
{
  "nome": "Paciente Teste Jitsi",
  "cpf": "526.018.159-06",
  "orgao_emissor": "SSP-PI",
  "data_nascimento": "1990-01-01",
  "genero": "Não informado",
  "telefone": "(86) 99999-0001",
  "email": "paciente.jitsi@example.com",
  "senha": "Senha123",
  "consentimento_lgpd": true,
  "cep": "64000-000",
  "cidade": "Teresina",
  "logradouro": "Rua Teste",
  "numero": "1",
  "bairro": "Centro"
}
```

Resposta esperada: `201`. 📝 Anote o `id` da resposta (um UUID): é o **ID_USUARIO_PACIENTE**.

### Passo 2: cadastrar o outro paciente

Mesma rota, com outro CPF e outro e-mail. Ele serve para provar que quem não participa da consulta não vê o link.

```json
{
  "nome": "Outro Paciente Teste",
  "cpf": "083.016.613-05",
  "orgao_emissor": "SSP-PI",
  "data_nascimento": "1990-01-01",
  "genero": "Não informado",
  "telefone": "(86) 99999-0002",
  "email": "outro.jitsi@example.com",
  "senha": "Senha123",
  "consentimento_lgpd": true,
  "cep": "64000-000",
  "cidade": "Teresina",
  "logradouro": "Rua Teste",
  "numero": "2",
  "bairro": "Centro"
}
```

Resposta esperada: `201`.

### Passo 3: cadastrar o médico

**Cadastro → `POST /api/v1/cadastro/profissional`**

```json
{
  "nome": "Medico Teste Jitsi",
  "cpf": "186.091.390-34",
  "orgao_emissor": "SSP-PI",
  "data_nascimento": "1980-01-01",
  "genero": "Não informado",
  "telefone": "(86) 99999-0003",
  "email": "medico.jitsi@example.com",
  "senha": "Senha123",
  "consentimento_lgpd": true,
  "cep": "64000-000",
  "cidade": "Teresina",
  "logradouro": "Rua Teste",
  "numero": "3",
  "bairro": "Centro",
  "numero_conselho": "CRM-PI 99999",
  "orgao_conselho": "CRM-PI",
  "info_profissional": "Médico de teste da videochamada",
  "especialidades": ["Cardiologia"]
}
```

Resposta esperada: `201`. 📝 Anote:

- o `id`: é o **ID_USUARIO_MEDICO**;
- o `id_profissional`: é o **ID_PROFISSIONAL**.

O médico nasce com `"status": false`, porque precisa ser aprovado pelo administrador antes de entrar.

### Passo 4: aprovar o médico como administrador

1. **Autenticação → `POST /api/v1/auth/login`** com o administrador inicial:
   ```json
   { "identificador": "nordestino1971@gmail.com", "senha": "Senha123" }
   ```
   📝 Anote o `access_token`: é o **TOKEN_ADMIN**. Cole-o no **Authorize**.
2. **Administração → `POST /api/v1/administracao/profissionais/{id_profissional}/validar`**, com `id_profissional` = **ID_PROFISSIONAL**. Resposta esperada: `200`, com `"status": true`.

### Passo 5: fazer login com os três usuários

Use **Autenticação → `POST /api/v1/auth/login`** três vezes, sempre com a senha `Senha123`, e 📝 anote os três tokens:

| Identificador | Token |
|---|---|
| `paciente.jitsi@example.com` | **TOKEN_PACIENTE** |
| `medico.jitsi@example.com` | **TOKEN_MEDICO** |
| `outro.jitsi@example.com` | **TOKEN_OUTRO** |

### Passo 6: descobrir o vínculo do médico com a especialidade (Adminer)

Os horários da agenda pertencem ao vínculo médico + especialidade (`id_esp_prof`), e nenhuma rota da API devolve esse id para um médico que acabou de ser cadastrado. Ele vem do banco, pelo Adminer:

1. Abra http://localhost:8000 e entre com:
   - **Sistema:** PostgreSQL
   - **Servidor:** `db`
   - **Usuário**, **Senha** e **Base de dados:** os valores de `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` do seu `.env`
2. Clique em **Comando SQL** e rode, trocando `ID_PROFISSIONAL` pelo número anotado:
   ```sql
   SELECT id_esp_prof, id_especialidade
   FROM profissional_especialidade
   WHERE id_profissional = ID_PROFISSIONAL;
   ```
3. 📝 Anote o **ID_ESP_PROF** e o **ID_ESPECIALIDADE**.

### Passo 7: criar horários na agenda do médico

**Horarios Profissionais → `POST /profissional/horarios`**

Esta rota não pede login. Ela cria dois horários livres, às 14h e às 16h. O das 16h é usado no reagendamento.

```json
{
  "id_esp_prof": ID_ESP_PROF,
  "datas": ["2026-12-01"],
  "lista_horarios": [
    { "hora_inicio": "14:00:00", "hora_fim": "14:45:00" },
    { "hora_inicio": "16:00:00", "hora_fim": "16:45:00" }
  ]
}
```

Resposta esperada: `201`.

### Passo 8: confirmar a consulta (o link é gerado aqui)

**Consulta → `POST /consulta/confirmar-consulta`**

Esta rota também não pede login.

```json
{
  "id_usuario_paciente": "ID_USUARIO_PACIENTE",
  "id_usuario_profissional": "ID_USUARIO_MEDICO",
  "id_especialidade": ID_ESPECIALIDADE,
  "data": "2026-12-01",
  "hora": "14:00:00",
  "tipo": "consulta",
  "status": "agendado",
  "valor": 200
}
```

Resposta esperada: `200`, com `{"mensagem": "Consulta confirmada com sucesso", "id_consulta": ...}`. 📝 Anote o **ID_CONSULTA**.

✅ **Confira no Mailpit:** chegou para `paciente.jitsi@example.com` o e-mail **"Sua teleconsulta está confirmada"**, com o link `https://meet.jit.si/simplemark-...`, a data `terça-feira, 01/12/2026 às 14:00 (horário de Brasília)` e as orientações. O e-mail não menciona a especialidade.

### Passo 9: ver o link como médico e como paciente

**Videochamada da consulta → `GET /api/v1/consultas/{id_consulta}/videochamada`**, com `id_consulta` = **ID_CONSULTA**.

1. No **Authorize**, entre com o **TOKEN_MEDICO** e execute. Resposta: `200`, com `meet_link` = `https://meet.jit.si/simplemark-` seguido de 22 caracteres aleatórios. 📝 Anote o **LINK**.
2. Troque para o **TOKEN_PACIENTE** e execute de novo. Resposta: `200`, com **o mesmo LINK**.

✅ Confira que o nome da sala não tem o id da consulta nem nome de ninguém, só `simplemark-` e caracteres aleatórios.

🎥 Para ver a sala de verdade, abra o **LINK** no navegador. O `meet.jit.si` pode pedir que quem abre a sala faça login.

### Passo 10: confirmar que mais ninguém vê o link

Na mesma rota do passo 9:

| Token no Authorize | Resposta esperada |
|---|---|
| **TOKEN_OUTRO** | `404`, `{"mensagem": "Consulta não encontrada."}`, sem link |
| **TOKEN_ADMIN** | `404` |
| Nenhum (clique em **Logout**) | `401` |

### Passo 11: reenviar o e-mail (reprocessar)

Entre com o **TOKEN_PACIENTE** (ou o **TOKEN_MEDICO**).

**Videochamada da consulta → `POST /api/v1/consultas/{id_consulta}/videochamada/reprocessar`**

Resposta esperada: `202`, com o **mesmo LINK**. O link nunca é trocado.

✅ **Mailpit:** chega um segundo e-mail **"Sua teleconsulta está confirmada"**, com o mesmo link.

### Passo 12: reagendar

**Videochamada da consulta → `PATCH /api/v1/consultas/{id_consulta}/reagendar`**

```json
{ "data": "2026-12-01", "hora": "16:00:00" }
```

1. Com o **TOKEN_PACIENTE**: resposta `403`, porque só o médico pode reagendar.
2. Com o **TOKEN_MEDICO**: resposta `200`, com `"hora": "16:00:00"` e **o mesmo LINK**.

✅ **Mailpit:** chega **"Sua teleconsulta foi reagendada"**, com a data antiga (14:00), a nova (16:00), o aviso "O link da videochamada continua o mesmo." e o mesmo LINK.

### Passo 13: cancelar

**Videochamada da consulta → `PATCH /api/v1/consultas/{id_consulta}/cancelar`** (sem corpo), com o **TOKEN_PACIENTE** ou o **TOKEN_MEDICO**.

1. Resposta: `200`, com `"status_consulta": "cancelada"` e `"meet_link": null`.
2. Execute o `GET .../videochamada` do passo 9 de novo: agora `"meet_link": null`. O link não é mais exibido.
3. Execute o cancelamento de novo: resposta `400`, `{"mensagem": "A consulta já está cancelada."}`.

✅ **Mailpit:** chega **"Sua teleconsulta foi cancelada"**, **sem** link.

### Resultado esperado no Mailpit

O paciente de teste recebe **4 e-mails**, e o "outro paciente" não recebe nenhum:

| # | Assunto | Tem o link? |
|---|---|---|
| 1 | Sua teleconsulta está confirmada | Sim |
| 2 | Sua teleconsulta está confirmada (reenvio) | Sim, o mesmo |
| 3 | Sua teleconsulta foi reagendada | Sim, o mesmo |
| 4 | Sua teleconsulta foi cancelada | Não |

Quem fizer o [teste extra](#teste-extra-consulta-antiga-sem-link) recebe mais uma "Sua teleconsulta está confirmada", com o link novo.

### Teste extra: consulta antiga sem link

Para simular uma consulta criada antes da videochamada, apague o link de uma consulta **ativa** no Adminer:

```sql
UPDATE consulta SET meet_link = NULL, data_geracao_link = NULL WHERE id_consulta = ID_CONSULTA;
```

Faça isso **antes do passo 13**, ou repita os passos 7 e 8 em outra data para ter uma consulta ativa nova. Depois, com o **TOKEN_MEDICO**, execute o `GET .../videochamada`. Um **link novo** é gerado na hora, e o paciente recebe o e-mail de confirmação. Executando o GET de novo, o link é o mesmo e nenhum e-mail novo é enviado.

### Limpar os dados de teste

No Adminer → **Comando SQL**, rode o bloco abaixo. Ele apaga **só** os usuários com e-mail `*.jitsi@example.com` e tudo o que foi criado para eles (consultas, horários, vínculo, conselho, sessões e o log da aprovação). Se algo falhar, nada é apagado.

```sql
BEGIN;
CREATE TEMP TABLE u_teste AS
  SELECT id FROM usuario WHERE email IN
  ('paciente.jitsi@example.com', 'outro.jitsi@example.com', 'medico.jitsi@example.com');
CREATE TEMP TABLE ep_teste AS
  SELECT pe.id_esp_prof, pe.id_conselho FROM profissional_especialidade pe
  JOIN profissional p ON p.id_profissional = pe.id_profissional
  WHERE p.id_usuario IN (SELECT id FROM u_teste);
CREATE TEMP TABLE c_teste AS
  SELECT id_consulta FROM consulta
  WHERE id_esp_prof IN (SELECT id_esp_prof FROM ep_teste)
     OR id_paciente IN (SELECT id_paciente FROM paciente WHERE id_usuario IN (SELECT id FROM u_teste));

DELETE FROM avaliacao WHERE id_consulta IN (SELECT id_consulta FROM c_teste);
DELETE FROM pagamento WHERE id_consulta IN (SELECT id_consulta FROM c_teste);
DELETE FROM documento_clinico WHERE id_consulta IN (SELECT id_consulta FROM c_teste);
DELETE FROM consulta WHERE id_consulta IN (SELECT id_consulta FROM c_teste);
DELETE FROM data_horario WHERE id_esp_prof IN (SELECT id_esp_prof FROM ep_teste);
DELETE FROM profissional_especialidade WHERE id_esp_prof IN (SELECT id_esp_prof FROM ep_teste);
DELETE FROM info_conselho WHERE id_conselho IN (SELECT id_conselho FROM ep_teste);
DELETE FROM profissional WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM paciente WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM log_acao_administrador WHERE id_usuario_alvo IN (SELECT id FROM u_teste);
DELETE FROM banimento WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM sessao_login WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM credencial WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM endereco WHERE id_usuario IN (SELECT id FROM u_teste);
DELETE FROM usuario WHERE id IN (SELECT id FROM u_teste);
COMMIT;
```

Para limpar o Mailpit, use o botão **Delete all** na caixa de entrada (http://localhost:8025).

### Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `422` no cadastro com mensagem de CPF | O CPF precisa ser válido. Use os do roteiro ou gere outro válido |
| `409` no cadastro | CPF ou e-mail já cadastrado. Rode a limpeza acima ou troque os valores |
| `403` no login do médico | Faltou aprovar o médico (passo 4) |
| `401` nas rotas da videochamada | Token ausente ou expirado. Faça login de novo e atualize o **Authorize** |
| `400` "O novo horário não existe na agenda" no reagendamento | O horário das 16h não foi criado no passo 7, ou a data é diferente |
| `400` "A nova data e hora devem estar no futuro" | Troque `2026-12-01` por uma data futura em todos os passos |
| Nenhum e-mail no Mailpit | Confira o `.env` (`SMTP_HOST=mailpit`, `SMTP_PORT=1025`, `SMTP_USAR_TLS=false`) e recrie o container com `docker compose up --build`. O motivo aparece no log do backend como "e-mail de confirmação falhou" |
| `500` em `GET /consultas/minhas` | Problema anterior a esta integração: em bancos criados com uma versão antiga, a tabela `avaliacao` não tem a coluna `avaliacao`, que o modelo exige. Não afeta as rotas da videochamada |

---

## E-mails enviados ao paciente

| Evento | Assunto | Conteúdo |
|---|---|---|
| Consulta confirmada (ou link gerado sob demanda, ou reprocessamento) | Sua teleconsulta está confirmada | Nome do médico, data/hora (horário de Brasília), link e orientações |
| Reagendamento | Sua teleconsulta foi reagendada | Data antiga, data nova, o mesmo link e as orientações |
| Cancelamento | Sua teleconsulta foi cancelada | Data cancelada, **sem link** |

Orientações incluídas: testar câmera, microfone e fone; entrar alguns minutos antes; preferir um lugar reservado, silencioso e com internet estável.

Formato de data: `terça-feira, 05/11/2026 às 14:00 (horário de Brasília)`. As mensagens são enviadas em texto puro e em HTML.

---

## Um link por consulta, falhas e retentativas

### Uma consulta nunca recebe dois links

- O link só é gravado quando `meet_link` está vazio. Um link existente nunca é trocado.
- A linha da consulta fica travada (`SELECT ... FOR UPDATE`) entre a leitura e o commit.
- A leitura com trava usa `populate_existing`. Assim, uma requisição que já tinha a consulta em memória relê a linha e vê o link gravado por outra requisição, em vez de sobrescrevê-lo.
- O índice único em `meet_link` impede, no banco, que duas consultas usem a mesma sala.

Isso foi validado num PostgreSQL real com 8 requisições simultâneas por consulta, em 9 consultas: cada consulta recebeu exatamente um link.

### Retentativas e falhas

| Etapa | Resultado |
|---|---|
| Gerar o link | Não depende de rede. Se gravar falhar (ex.: banco fora do ar), a consulta já confirmada **continua salva**, e o link é gerado na tarefa do e-mail ou na próxima consulta ao link |
| Enviar e-mail | Até `VIDEOCHAMADA_TENTATIVAS` tentativas (padrão 3), com backoff exponencial (2s e 4s). A falha final fica só no log e não afeta o link nem a consulta. Para reenviar, use o `reprocessar` |
| Servidor reinicia antes de enviar o e-mail | O link já está gravado. Use o `reprocessar` para reenviar o e-mail |

---

## LGPD e logs

- **Nome da sala:** só `simplemark-` + valor aleatório. Nenhum id, nome, e-mail, especialidade ou dado clínico.
- **Nenhum dado sai para terceiros pelo backend.** Diferente do Google, não há chamada de API: o servidor do Jitsi só fica sabendo do nome da sala quando alguém entra nela. Quem entra escolhe o nome que vai exibir.
- **E-mails:** apenas nome do paciente, nome do médico, data/hora e link. A especialidade foi omitida de propósito, porque pode revelar a condição de saúde.
- **Logs** (logger `simplemark.videochamada`): só o id da consulta, a etapa e o tipo do erro. Nunca o link, o nome da sala, nome, e-mail ou dado clínico. Há um teste para isso.

---

## Testes

O padrão é o mesmo do projeto: pytest com SQLite em memória e `dependency_overrides` para simular o usuário logado. O envio de e-mail é substituído por um dublê, então nenhum teste usa a rede.

```bash
cd backend
pytest
```

Resultado: **77 testes passando** (51 que já existiam e 26 em `tests/test_videochamada.py`).

O que os testes da videochamada cobrem:

- **Confirmação:**
  - link no formato `https://meet.jit.si/simplemark-<22 caracteres>`;
  - e-mail com médico, data/hora de Brasília, link e orientações;
  - nada de especialidade nem "Google" no e-mail;
  - a resposta da rota não mudou.
- **Nome da sala:**
  - é só o prefixo mais o aleatório de 16 bytes (sem dado da consulta);
  - 500 links gerados são todos diferentes;
  - `JITSI_BASE_URL` é configurável.
- **Um link por consulta:**
  - repetir a geração não troca o link;
  - uma sessão com dados desatualizados não sobrescreve o link de outra requisição;
  - o índice único recusa a mesma sala em duas consultas.
- **E-mail:**
  - a tarefa gera o link que faltou;
  - falha total (backoff de 2s e 4s) não afeta o link;
  - falha temporária é recuperada.
- **Consulta inativa:** cancelada ou realizada não ganha link nem e-mail.
- **Logs:** sem link, nome ou e-mail.
- **Acesso:**
  - médico e paciente veem o link;
  - outro médico recebe 404 no GET, no reprocessar e no cancelar, e nenhum link é gerado.
- **Sob demanda:** consulta antiga ganha link no GET, com um único e-mail.
- **Listagem do paciente:** traz o link, sem `status_integracao_meet`.
- **Reprocessar:**
  - gera o link que falta;
  - mantém o link existente e reenvia o e-mail;
  - recusa consulta cancelada (400).
- **Reagendamento:**
  - mantém o link;
  - e-mail com 14:00 → 16:00 e o link;
  - consulta sem link ganha um;
  - 403 para o paciente;
  - horário inexistente (400) ou ocupado (409).
- **Cancelamento:**
  - a API não devolve mais o link, que continua gravado no banco;
  - e-mail sem link;
  - segundo cancelamento recusado;
  - nenhuma rota devolve o link depois.

---

## Decisões tomadas e pontos para validar

### Pontos para validar

1. **O GET com efeito colateral.** Para consultas antigas, `GET /api/v1/consultas/{id}/videochamada` grava o link e dispara um e-mail ao paciente (só na primeira vez). Isso resolve o problema das consultas "presas", mas um GET que envia e-mail é incomum. Se preferir, o GET pode só gerar o link, deixando o e-mail para o `reprocessar`.
2. **Reenvio sem limite.** O `reprocessar` reenvia o e-mail a cada chamada, sem limite de frequência. Médico ou paciente podem disparar vários e-mails seguidos ao paciente. Vale avaliar um limite.
3. **Sala que não fecha.** Depois do cancelamento, quem já tinha o link ainda consegue abrir a sala no `meet.jit.si`. Só um servidor Jitsi próprio com autenticação resolve isso.
4. **Políticas do `meet.jit.si`.** O servidor público é gratuito, mas pode exigir que o primeiro participante faça login (Google, GitHub etc.) para abrir a sala, além de ter limites de uso. Confirme se isso é aceitável para o projeto ou se é melhor ter um servidor próprio (basta trocar `JITSI_BASE_URL`).
5. **Links antigos do Google apagados.** A migration apaga os links `meet.google.com` gravados em bancos de desenvolvimento, e essas consultas ganham link do Jitsi sob demanda. Se algum banco tiver consultas reais com esses links, os pacientes vão receber o link novo.
6. **Os logs `INFO` não aparecem.** O projeto não configura `logging`. Para ver o log de cada etapa, adicione `logging.basicConfig(level=logging.INFO)` no `main.py`. Isso não foi feito para não alterar o comportamento existente.
7. **Ambiente de teste:** os testes rodaram em Python 3.12, mas o `Dockerfile.back` usa Python 3.14. Vale rodar `docker compose up --build` uma vez e testar o envio pelo Mailpit. O envio SMTP real não foi exercitado nos testes automatizados, que usam um dublê.

### Decisões tomadas

1. **Link síncrono, e-mail em segundo plano:** gerar o link não depende de rede. Assim ele nunca fica "pendente", e a resposta da rota não muda.
2. **`status_integracao_meet` removido** da API e do banco: com o Jitsi, a consulta ativa sempre tem link ou ganha um na hora.
3. **`meet_link` mantido** e **`google_event_id` removido** (ver [Banco de dados](#banco-de-dados-migration)).
4. **No cancelamento, o link continua gravado** (auditoria), mas não é mais exibido em nenhuma rota.
5. **O que não foi alterado:**
   - O `confirmar-consulta` continua sem autenticação.
   - O reagendamento não altera a flag `data_horario.ocupado`.
   - A listagem do profissional não recebeu o link.
6. **Grafias de status:** o `confirmar-consulta` grava `agendado`, `realizado` e `cancelado`, enquanto o resto do código usa `agendada`, `realizada` e `cancelada`. A videochamada reconhece as duas grafias, mas essa inconsistência continua no projeto.
