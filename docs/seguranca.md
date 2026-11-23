# Revisão de segurança da API — Simple Mark

Revisão do backend (`backend/`, FastAPI + SQLAlchemy) feita em ambiente local em 22/11/2026.
Nenhuma lógica do app foi alterada: os achados abaixo trazem a correção sugerida com o
**antes** e o **depois**, para o grupo decidir e aplicar. O que foi adicionado ao repositório
foi só a suíte de testes `backend/tests/test_seguranca.py` e este relatório.

## Resumo dos achados

| # | Achado | Risco | Onde |
|---|--------|-------|------|
| 1 | Rotas de escrita da agenda, das consultas do profissional e de marcação de consulta **sem autenticação** (inclui vazamento de dados de pacientes e consulta criada com preço escolhido pelo cliente) | **Alto** | `routers/horarios_profissional.py`, `routers/consulta_profissional.py`, `routers/confirmar_consulta.py` |
| 2 | **Senha do administrador escrita no código** (e contas do seed com senha conhecida criadas em todo start) | **Alto** | `services/CadastroService/admin_inicial.py:17-19`, `seed/seed.py`, `main.py` |
| 3 | `SECRET_KEY` do JWT com valor padrão público; o `compose.yaml` não define a variável | Médio | `core/parametros.py:12`, `compose.yaml` |
| 4 | Mensagens de erro que repassam a exceção interna ao cliente; erros só em `print()` | Médio | `routers/horarios_profissional.py:69`, `routers/*minha_conta.py`, outros |
| 5 | Limite de tentativas só por conta: sem limite por IP (password spraying, bloqueio proposital de contas, spam de cadastro/recuperação/ouvidoria) | Médio | `services/LoginService/autenticacao.py`, `main.py` |
| 6 | Vitrine pública de avaliações expõe **nome completo do paciente** + data da consulta | Médio | `services/buscar_avaliacao_profissional.py:88` |
| 7 | Login responde mais rápido quando a conta não existe (enumeração por tempo) | Baixo | `services/LoginService/autenticacao.py:98-104` |
| 8 | Validações de entrada faltando (lote de horários sem limite, `hora_fim` > `hora_inicio`, `valor_consulta` aceita 0, upload lido inteiro antes de checar tamanho, `%`/`_` na busca) | Baixo | `schemas/horarios_profissional.py`, `schemas/porfissional_minha_conta.py`, `services/porfissional_minha_conta.py:146`, `repositories/busca_profissional.py:65` |
| 9 | Webhook do Mercado Pago não confere a assinatura `x-signature` | Baixo | `routers/pagamento.py` (`/pagamento/notificacao`) |
| 10 | CORS com métodos e cabeçalhos `*` e origens fixas no código | Baixo | `main.py:55-69` |
| 11 | `/docs` e `/openapi.json` abertos; PostgreSQL publicado na porta 5432 | Baixo | `main.py`, `compose.yaml` |
| — | SQL injection | — | **Nada encontrado** ✅ |
| — | Senhas sem hash | — | **Nada encontrado** (Argon2) ✅ |

**O que já está bom** (vale citar na apresentação):

- Todo acesso ao banco usa o ORM do SQLAlchemy (consultas parametrizadas). `text()` só aparece
  em `database/migracoes.py`, com SQL fixo, sem nenhum dado do usuário.
- Senhas com **Argon2** (`pwdlib`), código de login e de recuperação guardados só como HMAC.
- Login em **duas etapas** (senha + código por e-mail), sessão no banco ligada ao JWT (`sid`),
  expiração por inatividade (24 h), logout que encerra a sessão, conta banida/inativa barrada
  mesmo com token antigo.
- Bloqueio da conta após 5 erros de senha **ou** de código, mesma mensagem para conta
  inexistente e senha errada, e recuperação de senha que não revela se o e-mail existe.
- As rotas autenticadas checam o **dono** do recurso: "Minha conta" (`exigir_propria_conta`),
  consultas e pagamento do paciente (404 para consulta alheia), documentos, videochamada,
  avaliação e QR-Code (só o profissional responsável ou o paciente da consulta).
- Ouvidoria confere o **conteúdo** do anexo (assinatura do PDF/PNG/JPEG), não só a extensão,
  e salva com nome aleatório (`uuid`), sem *path traversal*.
- Status do pagamento é sempre buscado na API do Mercado Pago (não confia nos parâmetros
  do retorno nem do webhook).

---

## 1. Mapa das rotas

63 rotas: **36 exigem login**, **27 são públicas** — das quais **5 não deveriam ser** (🔴).
Gerado a partir dos `include_router` do `main.py`; a coluna "Acesso" vem das dependências
de cada rota (`UsuarioAtual`, `AdministradorAtual`, `PacienteAtual`).

| # | Método | Caminho | O que faz | Acesso |
|---|---|---|---|---|
| 1 | `GET` | `/profissional/horarios` | Lista os horarios de um profissional para uma data especifica | Pública (agendamento do paciente; só dados da agenda) |
| 2 | `POST` | `/profissional/horarios` | Cadastra horarios para um profissional | 🔴 **Pública — deveria exigir login** |
| 3 | `DELETE` | `/profissional/horarios/{id_horario}` | Deleta um horario especifico de um profissional | 🔴 **Pública — deveria exigir login** |
| 4 | `PUT` | `/profissional/horarios/{id_horario}` | Atualiza um horario especifico de um profissional | 🔴 **Pública — deveria exigir login** |
| 5 | `POST` | `/api/v1/cadastro/paciente` | Cria a conta do paciente, já ativa | Pública |
| 6 | `POST` | `/api/v1/cadastro/profissional` | Cria a conta do profissional, inativa até a validação do administrador | Pública |
| 7 | `POST` | `/api/v1/auth/login` | Etapa 1 do login: confere a senha e envia o código de confirmação por e-mail | Pública |
| 8 | `POST` | `/api/v1/auth/login/confirmar` | Etapa 2 do login: confere o código e, se estiver certo, abre a sessão | Pública |
| 9 | `GET` | `/api/v1/auth/eu` | Devolve os dados públicos da conta logada. Sem token válido, responde 401 | 🔒 Login |
| 10 | `POST` | `/api/v1/auth/sair` | Encerra a sessão do token atual (logout). Sem token válido, responde 401 | 🔒 Login |
| 11 | `POST` | `/api/v1/auth/senha/esqueci` | Etapa 1: envia o código de recuperação por e-mail | Pública |
| 12 | `POST` | `/api/v1/auth/senha/redefinir` | Etapa 2: confere o código e troca a senha | Pública |
| 13 | `POST` | `/api/v1/ouvidoria/manifestacoes` | Abre a manifestação e devolve o protocolo. Responde 422 com dados ou anexos inválidos | Pública |
| 14 | `GET` | `/api/v1/administracao/profissionais/pendentes` | Lista os profissionais que aguardam validação, sem os banidos | 🔒 Login + administrador |
| 15 | `POST` | `/api/v1/administracao/profissionais/{id_profissional}/validar` | Ativa a conta do profissional e registra a ação no log | 🔒 Login + administrador |
| 16 | `GET` | `/api/v1/administracao/usuarios/ids` | Lista os IDs de profissionais e pacientes, sem os banidos | 🔒 Login + administrador |
| 17 | `POST` | `/api/v1/administracao/profissionais/{id_profissional}/banir` | Bane o profissional, encerra as sessões dele e registra no log | 🔒 Login + administrador |
| 18 | `POST` | `/api/v1/administracao/pacientes/{id_paciente}/banir` | Bane o paciente, encerra as sessões dele e registra no log | 🔒 Login + administrador |
| 19 | `GET` | `/api/v1/administracao/logs` | Lista as ações registradas pelos administradores. Somente administrador | 🔒 Login + administrador |
| 20 | `GET` | `/api/v1/profissionais/busca` | Busca profissionais por especialidade, período, horário e valor da consulta | Pública |
| 21 | `GET` | `/api/v1/consultas_profissionais/{id_profissional}/consultas` | Lista as consultas do profissional, com os dados do paciente | 🔴 **Pública — deveria exigir login** |
| 22 | `POST` | `/api/v1/documentos/{documento_id}/qrcode` | Gera o código de verificação e o QR-Code da receita ou do atestado | 🔒 Login |
| 23 | `GET` | `/api/v1/documentos/validar/{codigo_verificacao}` | Confere se a receita ou o atestado foi emitido pela plataforma | Pública |
| 24 | `POST` | `/api/v1/receitas` | Emite a receita da consulta, já com código de verificação e QR-Code | 🔒 Login |
| 25 | `POST` | `/api/v1/atestados` | Emite o atestado da consulta, já com código de verificação e QR-Code | 🔒 Login |
| 26 | `GET` | `/api/v1/consultas/{id_consulta}/documentos` | Lista os documentos clínicos emitidos na consulta | 🔒 Login |
| 27 | `GET` | `/api/v1/documentos/{documento_id}` | Devolve um documento clínico emitido, por inteiro | 🔒 Login |
| 28 | `GET` | `/api/v1/consultas/{id_consulta}/videochamada` | Link da videochamada, para o profissional responsável ou o paciente da consulta | 🔒 Login |
| 29 | `POST` | `/api/v1/consultas/{id_consulta}/videochamada/reprocessar` | Gera o link se a consulta ainda não tiver (nunca troca um existente) e | 🔒 Login |
| 30 | `PATCH` | `/api/v1/consultas/{id_consulta}/reagendar` | Move a consulta para um horário livre da agenda do profissional | 🔒 Login |
| 31 | `PATCH` | `/api/v1/consultas/{id_consulta}/cancelar` | Cancela a consulta (profissional ou paciente dela) e avisa o paciente | 🔒 Login |
| 32 | `POST` | `/consultas/agendar` | Agenda uma consulta do paciente logado num horário livre | 🔒 Login |
| 33 | `GET` | `/consultas/minhas` | Lista as consultas do paciente logado, com filtros e paginação | 🔒 Login |
| 34 | `GET` | `/consultas/minhas/{id_consulta}` | Detalha uma consulta do paciente logado | 🔒 Login |
| 35 | `POST` | `/api/v1/avaliacoes` | Avalia uma consulta realizada do paciente logado (fluxo antigo) | 🔒 Login |
| 36 | `GET` | `/api/v1/avaliacoes/profissionais/{id_profissional}/media` | Média e total das avaliações do profissional. Rota pública | Pública |
| 37 | `POST` | `/api/v1/avaliacoes/consultas/{id_consulta}/avaliacao` | Grava a avaliação da consulta: 1 a 5 estrelas (opcional) e comentário | 🔒 Login + paciente |
| 38 | `GET` | `/api/v1/avaliacoes/consultas/{id_consulta}/avaliacao` | Devolve a avaliação que o paciente logado deu à consulta | 🔒 Login + paciente |
| 39 | `GET` | `/api/v1/avaliacoes/profissionais/{id_profissional}/avaliacoes` | Média e distribuição das estrelas do profissional. Rota pública | Pública |
| 40 | `GET` | `/api/v1/avaliacoes/profissionais/melhor-avaliados` | Ranking dos profissionais ativos pela média bayesiana das estrelas | Pública |
| 41 | `PUT` | `/profissionais/alterar-info-profissional` | Altera a descrição, a imagem e as especialidades do profissional | 🔒 Login |
| 42 | `GET` | `/profissionais/buscar-info-profissional/{id_usuario}` | Devolve a descrição do profissional e suas especialidades, conselho e valor | Pública |
| 43 | `PUT` | `/profissionais/alterar-valor-consulta` | Altera o valor da consulta do profissional numa especialidade | 🔒 Login |
| 44 | `POST` | `/profissionais/salvar-imagem-profissional` | Salva a imagem do profissional em uploads/profissionais e grava o caminho | 🔒 Login |
| 45 | `GET` | `/profissionais/buscar-imagem-profissional/{id_usuario}` | Devolve o arquivo da imagem do profissional | Pública |
| 46 | `GET` | `/profissionais/lista-especialidade` | Lista todas as especialidades cadastradas. Rota pública | Pública |
| 47 | `DELETE` | `/profissionais/excluir-especialidade` | Remove a especialidade do profissional, com os horários e o conselho dela | 🔒 Login |
| 48 | `GET` | `/usuario/buscar-info-usuario/{id_usuario}` | Dados pessoais da conta logada (o id precisa ser o dela) | 🔒 Login |
| 49 | `GET` | `/usuario/buscar-info-endereco/{id_usuario}` | Endereço da conta logada. Responde 404 se ela não tiver endereço | 🔒 Login |
| 50 | `PUT` | `/usuario/altera-info-pessoal` | Altera nome, e-mail e telefone (só os campos enviados) e devolve os dados atualizados | 🔒 Login |
| 51 | `PUT` | `/usuario/altera-endereco` | Altera o endereço (só os campos enviados) e devolve o endereço atualizado | 🔒 Login |
| 52 | `PUT` | `/usuario/alterar-senha` | Troca a senha da conta logada. Responde 400 se a senha atual estiver incorreta | 🔒 Login |
| 53 | `DELETE` | `/usuario/excluir-usuario` | Exclui a conta logada (paciente ou profissional) e os dados ligados a ela | 🔒 Login |
| 54 | `PATCH` | `/usuario/inativar-usuario` | Inativa a conta logada (id_usuario na query string) e encerra as sessões dela | 🔒 Login |
| 55 | `POST` | `/avaliacao/buscar-avaliacoes` | Lista as avaliações do profissional na especialidade, com o total por nota | Pública |
| 56 | `POST` | `/consulta/confirmar-consulta` | Cria a consulta, gera o link da videochamada e agenda o e-mail ao paciente | 🔴 **Pública — deveria exigir login** |
| 57 | `POST` | `/api/v1/pagamento/preferencia` | Cria a preferência de pagamento da consulta no Mercado Pago | 🔒 Login |
| 58 | `GET` | `/api/v1/pagamento/retorno/sucesso` | Retorno do Mercado Pago depois do pagamento aprovado | Pública |
| 59 | `GET` | `/api/v1/pagamento/retorno/pendente` | Retorno do Mercado Pago com pagamento pendente; mesmo tratamento do sucesso | Pública |
| 60 | `GET` | `/api/v1/pagamento/retorno/falha` | Retorno do Mercado Pago com pagamento recusado; mesmo tratamento do sucesso | Pública |
| 61 | `POST` | `/api/v1/pagamento/notificacao` | Webhook do Mercado Pago: atualiza o status local do pagamento notificado | Pública |
| 62 | `GET` | `/api/v1/pagamento/{id_consulta}` | Devolve o pagamento da consulta, sincronizado com o Mercado Pago | 🔒 Login |
| 63 | `GET` | `/` | Verifica se a API está no ar | Pública |

As 21 rotas públicas restantes são públicas de propósito (cadastro, login, recuperação de
senha, ouvidoria, busca e vitrine de profissionais, horários livres para o agendamento, validação de documento por QR-Code, retorno
e webhook do Mercado Pago). Elas estão listadas com o motivo em `PUBLICAS_ESPERADAS`, no teste
`test_rotas_publicas_sao_so_as_esperadas`: se alguém criar uma rota pública nova sem justificar,
o teste falha.

---

## 2. Achados

### Achado 1 — Rotas sem autenticação/autorização — **ALTO**

**Onde:**

| Rota | Arquivo | O que um anônimo consegue fazer hoje (comprovado pelos testes) |
|------|---------|------------------------------------------------------------------|
| `GET /api/v1/consultas_profissionais/{id_profissional}/consultas` | `routers/consulta_profissional.py:14` | Listar as consultas de **qualquer** profissional com nome, e-mail, telefone, data de nascimento e gênero dos pacientes (troca o id na URL — IDOR) |
| `POST/PUT/DELETE /profissional/horarios[...]` | `routers/horarios_profissional.py` | Criar, alterar e **apagar** horários da agenda de qualquer profissional |
| `POST /consulta/confirmar-consulta` | `routers/confirmar_consulta.py:19` | Marcar consulta em nome de qualquer paciente, **escolhendo o `valor` (ex.: R$ 0,01) e o `status`** (até `"realizado"`, o que libera avaliação sem consulta) |

**Por que é grave:** dados pessoais e de saúde (LGPD) expostos sem login; qualquer pessoa pode
bagunçar a agenda dos profissionais ou criar consultas falsas.

**Como corrigir** — usar as dependências que já existem em `dependencies/autenticacao.py` e
conferir que o recurso é de quem está logado.

*Consultas do profissional — antes:*

```python
@router.get("/{id_profissional}/consultas", response_model=list[ConsultaProfissionalOut])
def consultas_do_profissional(
    id_profissional: int,
    status: str | None = Query("agendada"),
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
```

*Depois:*

```python
from core.excecoes import ErroNegocio
from dependencies.autenticacao import UsuarioAtual

@router.get("/{id_profissional}/consultas", response_model=list[ConsultaProfissionalOut])
def consultas_do_profissional(
    usuario: UsuarioAtual,
    id_profissional: int,
    status: str | None = Query("agendada"),
    data_inicio: date | None = None,
    data_fim: date | None = None,
    db: Session = Depends(get_db),
):
    if usuario.profissional is None or usuario.profissional.id_profissional != id_profissional:
        raise ErroNegocio("Você só pode ver as suas próprias consultas.", 403)
```

*Horários — antes:*

```python
@router.delete("/{id_horario}", status_code=status.HTTP_200_OK)
def deletar_horario(id_horario: int, db: Session = Depends(get_db)):
```

*Depois* (o mesmo padrão em `POST` e `PUT`, conferindo o `id_esp_prof` do payload):

```python
def _exigir_vinculo_do_profissional(usuario, id_esp_prof: int, db: Session) -> None:
    vinculo = db.get(ProfissionalEspecialidade, id_esp_prof)
    profissional = usuario.profissional
    if vinculo is None or profissional is None or vinculo.id_profissional != profissional.id_profissional:
        raise ErroNegocio("Este horário não pertence à sua agenda.", 403)


@router.delete("/{id_horario}", status_code=status.HTTP_200_OK)
def deletar_horario(id_horario: int, usuario: UsuarioAtual, db: Session = Depends(get_db)):
    horario = db.get(DataHorario, id_horario)
    if horario is None:
        raise HTTPException(status_code=404, detail="Horario nao encontrado")
    _exigir_vinculo_do_profissional(usuario, horario.id_esp_prof, db)
    ...
```

> `GET /profissional/horarios` **continua público de propósito**: o paciente usa essa rota
> para ver os horários livres na tela de agendamento. Ela é segura porque devolve só dados da
> agenda (`id_horario`, `id_esp_prof`, `data_consulta`, `hora_inicio`, `hora_fim`, `ocupado`),
> sem nenhum dado de paciente. O teste `test_listagem_publica_de_horarios_so_traz_dados_da_agenda`
> garante que continue assim: se alguém acrescentar um campo pessoal na resposta, ele falha.

*Confirmar consulta — antes:*

```python
@router.post("/confirmar-consulta")
def confirmar_consulta(dados: ConfirmarConsultaInput, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
```

```python
class ConfirmarConsultaInput(BaseModel):
    id_usuario_paciente: uuid.UUID
    ...
    status: Literal["agendado", "realizado", "cancelado"]
    valor: float
```

*Depois:* o paciente vem do token; `status` e `valor` são decididos pelo servidor
(status inicial fixo e valor lido de `ProfissionalEspecialidade.valor_consulta`):

```python
@router.post("/confirmar-consulta")
def confirmar_consulta(
    dados: ConfirmarConsultaInput, paciente: PacienteAtual, tarefas: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if str(paciente.id_usuario) != str(dados.id_usuario_paciente):
        raise ErroNegocio("Você só pode marcar consultas para você.", 403)
```

```python
class ConfirmarConsultaInput(BaseModel):
    id_usuario_paciente: uuid.UUID
    id_usuario_profissional: uuid.UUID
    id_especialidade: int
    data: date
    hora: time
    tipo: Literal["consulta", "retorno"]
    # status e valor saem do corpo: o service usa "agendado" e o valor cadastrado
```

O frontend não precisa mudar: ele já envia `Authorization: Bearer` em todas as chamadas.

**Testes:** `test_rotas_da_agenda_e_consultas_exigem_login`,
`test_anonimo_nao_le_consultas_e_dados_de_pacientes_do_profissional`,
`test_anonimo_nao_apaga_horario_de_profissional`,
`test_anonimo_nao_marca_consulta_em_nome_de_paciente` (hoje `xfail`).

---

### Achado 2 — Credenciais do administrador no código-fonte — **ALTO**

**Onde:** `services/CadastroService/admin_inicial.py:17-19`

```python
EMAIL_ADMIN = "<e-mail real>"
SENHA_ADMIN = "Senha123"
CPF_ADMIN = "847.329.105-05"
```

`criar_admin_inicial()` roda a cada start da API (`main.py`). Além disso, `criar_seed()`
também roda em todo start e cria paciente e profissional com senha fixa (documentada na
própria docstring) e e-mails reais de integrantes.

**Risco:** o repositório está no GitHub: quem o ler sabe a senha do administrador. Hoje o
estrago é contido pelo segundo fator (código por e-mail), mas a segurança da conta mais
poderosa passa a depender só da caixa de e-mail de uma pessoa. A senha também é fraca e
igual em todas as instalações. Dados pessoais reais (e-mail, CPF) não deveriam estar no código.

**Como corrigir** — antes:

```python
EMAIL_ADMIN = "<e-mail real>"
SENHA_ADMIN = "Senha123"
CPF_ADMIN = "847.329.105-05"
```

Depois:

```python
EMAIL_ADMIN = os.getenv("ADMIN_EMAIL")
SENHA_ADMIN = os.getenv("ADMIN_SENHA")
CPF_ADMIN = os.getenv("ADMIN_CPF")


def criar_admin_inicial() -> None:
    if os.getenv("AMBIENTE") == "teste":
        return
    if not (EMAIL_ADMIN and SENHA_ADMIN and CPF_ADMIN):
        print("Admin inicial não criado: defina ADMIN_EMAIL, ADMIN_SENHA e ADMIN_CPF no .env")
        return
    ...
```

E no `main.py`, rodar o seed só em desenvolvimento:

```python
# antes
criar_seed()

# depois
if os.getenv("AMBIENTE") == "desenvolvimento":
    criar_seed()
```

Depois de mudar: **trocar a senha do admin** nos bancos que já existem (a antiga continua no
histórico do Git).

---

### Achado 3 — `SECRET_KEY` com valor padrão público — **MÉDIO**

**Onde:** `core/parametros.py:12`

```python
def segredo_jwt() -> str:
    return os.getenv("SECRET_KEY", "simplemark-dev-secret-troque-em-producao")
```

O `compose.yaml` não define `SECRET_KEY`, então no Docker os tokens são assinados com uma
chave que está no repositório. Quem a conhece consegue assinar tokens válidos; hoje ainda
falta o `sid` de uma sessão ativa (UUID aleatório), o que segura o ataque, mas a assinatura
deixa de proteger.

**Como corrigir** — depois:

```python
def segredo_jwt() -> str:
    segredo = os.getenv("SECRET_KEY")
    if not segredo:
        if os.getenv("AMBIENTE") == "teste":
            return "chave-so-para-testes"
        raise RuntimeError("Defina SECRET_KEY no .env (python -c 'import secrets; print(secrets.token_urlsafe(48))')")
    return segredo
```

```yaml
# compose.yaml, no serviço backend
      SECRET_KEY: ${SECRET_KEY}
```

**Testes relacionados (passando):** `test_token_com_assinatura_de_outra_chave_responde_401`,
`test_token_sem_assinatura_alg_none_responde_401`.

---

### Achado 4 — Mensagens de erro que vazam detalhes internos — **MÉDIO**

**Onde:**

- `routers/horarios_profissional.py:66-70` — qualquer exceção (inclusive erro do banco, que
  traz a SQL e os parâmetros) volta para o cliente:

  ```python
  except Exception as e:
      raise HTTPException(status_code=400, detail=f"Erro ao salvar horarios: {str(e)}")
  ```
- `detail=str(erro)` para `ValueError` em `routers/usuario_minha_conta.py:79`,
  `routers/porfissional_minha_conta.py` (várias), `routers/buscar_avaliacao_profissional.py:51`,
  `routers/confirmar_consulta.py`, `routers/documento_qrcode.py:62` (inclusive no 500).
  `ValueError` também é levantado por bibliotecas (ex.: `uuid.UUID("x")`, `int("x")`), cujas
  mensagens não foram feitas para o usuário.
- Erros inesperados vão para `print(f"ERRO REAL: {erro}")` em vez de um log.

**Como corrigir** — antes:

```python
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Erro ao salvar horarios: {str(e)}"
    )
```

Depois:

```python
import logging
logger = logging.getLogger(__name__)
...
except Exception:
    logger.exception("Falha ao salvar horários em lote")
    raise HTTPException(status_code=500, detail="Não foi possível salvar os horários.")
```

Para as mensagens de negócio, usar `ErroNegocio("mensagem para o usuário", status)` (o
padrão que o projeto já usa nas rotas novas) em vez de `ValueError` + `str(erro)`.

**Testes (passando):** `test_json_invalido_no_campo_dados_nao_vaza_detalhes`,
`test_erro_de_validacao_nao_ecoa_stack_trace`, `test_login_com_sql_injection_e_recusado_sem_detalhes`.

---

### Achado 5 — Limite de tentativas só por conta — **MÉDIO**

**O que existe (bom):** 5 erros seguidos de senha ou código bloqueiam a conta por 60 minutos
(`LOGIN_MAX_TENTATIVAS`, `LOGIN_BLOQUEIO_MINUTOS`); a recuperação de senha usa o mesmo contador
e não reenvia e-mail dentro do intervalo mínimo. Testado em `test_login_bloqueia_apos_tentativas_erradas`.

**O que falta:** nenhum limite por **IP/cliente**. Consequências:

- *password spraying*: testar uma senha comum (ex.: `Senha123`) em milhares de contas, 4 vezes
  cada, sem nunca bloquear nenhuma;
- bloqueio proposital: errar 5 vezes de propósito e travar a conta de outra pessoa por 1 hora;
- spam em `POST /cadastro/*`, `/auth/senha/esqueci` (dispara e-mails) e `/ouvidoria/manifestacoes`
  (até 5 anexos de 10 MB por requisição).

**Como corrigir** com `slowapi` (`pip install slowapi`) — antes (`main.py`):

```python
app = FastAPI()
registrar_erros(app)
```

Depois:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
registrar_erros(app)
```

```python
# routers/auth.py
@router.post("/login", ...)
@limiter.limit("10/minute")
def login(request: Request, dados: LoginEntrada, ...):
```

(o mesmo em `login/confirmar`, `senha/esqueci`, `senha/redefinir`, `cadastro/*` e `ouvidoria`).

---

### Achado 6 — Nome completo do paciente na vitrine pública de avaliações — **MÉDIO**

**Onde:** `POST /avaliacao/buscar-avaliacoes` (pública) — `services/buscar_avaliacao_profissional.py:88`

```python
avaliacao.append({
    "nome_paciente": usuario_paciente.nome,
    "data_consulta": consulta.data,
    "feedback": registro.feedback,
```

**Risco:** qualquer pessoa vê que "Fulano da Silva" se consultou com um cardiologista em tal
data e o que ele escreveu — dado de saúde (sensível pela LGPD) ligado a uma pessoa identificada.

**Como corrigir** — depois (mostrar só o primeiro nome e a inicial):

```python
def _nome_publico(nome: str) -> str:
    partes = (nome or "").split()
    if not partes:
        return "Paciente"
    return partes[0] if len(partes) == 1 else f"{partes[0]} {partes[-1][0]}."

avaliacao.append({
    "nome_paciente": _nome_publico(usuario_paciente.nome),
    ...
```

**Teste:** `test_vitrine_de_avaliacoes_nao_expoe_nome_completo_do_paciente` (hoje `xfail`).

---

### Achado 7 — Enumeração de contas pelo tempo de resposta — **BAIXO**

**Onde:** `services/LoginService/autenticacao.py:98-104`. A **mensagem** é a mesma para conta
inexistente e senha errada (testado em `test_login_nao_revela_se_a_conta_existe`), mas a conta
inexistente responde na hora, enquanto a existente calcula o Argon2 (~dezenas de ms). Medindo o
tempo, dá para descobrir quais e-mails/CPFs têm cadastro.

Antes:

```python
usuario = self._localizar(identificador)
if usuario is None:
    raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)

credencial = self.credenciais.buscar_para_atualizar(usuario.id)
if credencial is None:
    raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)
```

Depois:

```python
_HASH_FALSO = gerar_hash_senha("senha-que-ninguem-usa")  # calculado uma vez

usuario = self._localizar(identificador)
credencial = self.credenciais.buscar_para_atualizar(usuario.id) if usuario else None
if credencial is None:
    verificar_senha(senha, _HASH_FALSO)  # gasta o mesmo tempo de uma senha errada
    raise ErroNegocio(MENSAGEM_CREDENCIAL_INVALIDA, 401)
```

---

### Achado 8 — Validações de entrada que faltam — **BAIXO**

O back-end valida bem a maioria das entradas (Pydantic com `min_length`/`max_length`, CPF,
e-mail, faixas de nota e de dias, campos extras proibidos na avaliação) — ver os testes da
seção 3. Pontos que faltam:

**a) Lote de horários sem limite e sem checar o intervalo** (`schemas/horarios_profissional.py`).
Um único `POST` com 10.000 datas × 50 horários cria 500 mil linhas; `hora_fim` antes de
`hora_inicio` é aceito. O front limita a 366 dias, o back não.

Antes:

```python
class ItemHorarioItem(BaseModel):
    hora_inicio: time
    hora_fim: time

class HorariosEmLoteCreate(BaseModel):
    id_esp_prof: int
    datas: List[date]
    lista_horarios: List[ItemHorarioItem]
```

Depois:

```python
class ItemHorarioItem(BaseModel):
    hora_inicio: time
    hora_fim: time

    @model_validator(mode="after")
    def fim_depois_do_inicio(self):
        if self.hora_fim <= self.hora_inicio:
            raise ValueError("O horário final deve ser depois do inicial.")
        return self

class HorariosEmLoteCreate(BaseModel):
    id_esp_prof: int
    datas: List[date] = Field(min_length=1, max_length=366)
    lista_horarios: List[ItemHorarioItem] = Field(min_length=1, max_length=48)
```

**b) Valor da consulta** (`schemas/porfissional_minha_conta.py:59`): o service recusa negativo,
mas aceita `0` e valores absurdos.

```python
# antes
valor_consulta: float
# depois
valor_consulta: float = Field(gt=0, le=100_000)
```

**c) Upload da foto** (`services/porfissional_minha_conta.py:146-149`): só confere a extensão
do nome e lê o arquivo inteiro na memória antes de checar os 5 MB. Sugestão: ler no máximo
`TAMANHO_MAX_IMAGEM + 1` bytes e conferir o conteúdo com o Pillow (já instalado via `qrcode[pil]`).

```python
# antes
conteudo = await imagem.read()
if len(conteudo) > TAMANHO_MAX_IMAGEM:
    raise ErroNegocio("A imagem deve ter no máximo 5 MB.", 400)

# depois
conteudo = await imagem.read(TAMANHO_MAX_IMAGEM + 1)
if len(conteudo) > TAMANHO_MAX_IMAGEM:
    raise ErroNegocio("A imagem deve ter no máximo 5 MB.", 400)
try:
    Image.open(io.BytesIO(conteudo)).verify()
except Exception:
    raise ErroNegocio("O arquivo enviado não é uma imagem válida.", 400)
```

**d) Curingas na busca** (`repositories/busca_profissional.py:65`): o `ilike(f"%{texto}%")` é
parametrizado (**não** é SQL injection — testado), mas `%` e `_` digitados viram curingas
(`%` lista todas as especialidades). Inofensivo aqui; se quiserem tratar:

```python
termo = filtro.especialidade.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
query = query.filter(Especialidade.especialidade.ilike(f"%{termo}%", escape="\\"))
```

---

### Achado 9 — Webhook do Mercado Pago sem conferir assinatura — **BAIXO**

`POST /api/v1/pagamento/notificacao` aceita qualquer requisição. O impacto é pequeno porque o
status é sempre consultado na API do Mercado Pago (um webhook falso não aprova pagamento), mas
qualquer um pode fazer a API disparar chamadas ao Mercado Pago em volume. Correção: validar o
cabeçalho `x-signature` com a *secret* do webhook configurada no painel do Mercado Pago
(HMAC-SHA256 de `id:<data.id>;request-id:<x-request-id>;ts:<ts>;`) e responder 401 se não bater.

---

### Achado 10 — CORS — **BAIXO**

`main.py:55-69` usa uma lista explícita de origens (bom — não é `"*"`), mas com
`allow_methods=["*"]` e `allow_headers=["*"]` junto de `allow_credentials=True`, e as origens
fixas no código. Antes:

```python
allow_origins=[
    "http://localhost", "http://127.0.0.1",
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:8080", "http://127.0.0.1:8080",
],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
```

Depois:

```python
allow_origins=os.getenv("CORS_ORIGENS", "http://localhost,http://localhost:5173").split(","),
allow_credentials=False,  # o token vai no cabeçalho Authorization, não em cookie
allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
allow_headers=["Authorization", "Content-Type"],
```

---

### Achado 11 — Superfície exposta no deploy — **BAIXO**

- `/docs`, `/redoc` e `/openapi.json` ficam abertos: ótimos em desenvolvimento, mas entregam o
  mapa completo da API. Em produção: `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)`
  quando `AMBIENTE == "producao"`.
- `compose.yaml` publica o PostgreSQL em `5432:5432` (acessível de fora da máquina). Se só o
  backend usa o banco, remover o `ports:` do serviço `db` (os containers se falam pela rede
  interna do Compose).
- O JWT vale 7 dias (`core/seguranca.py`), mas quem manda é a sessão (24 h sem uso) — ok como está.

---

## 3. SQL injection — nenhum ponto encontrado

Busca feita por `text(`, `.execute(`, `exec_driver_sql`, `cursor()`, f-strings e `%`/`.format`
montando SQL em todo o `backend/`:

- `repositories/*` e `services/*`: só ORM (`db.query(...).filter(Modelo.campo == valor)`,
  `select(...)`, `update(...)`) — o SQLAlchemy envia os valores como parâmetros.
- `database/migracoes.py`: `text("ALTER TABLE ...")` com SQL **fixo**, sem dado externo.
- `repositories/busca_profissional.py:65`: `ilike(f"%{...}%")` — a f-string monta o **valor**
  do parâmetro, não a SQL (ver achado 8d).

Se um dia precisarem de SQL manual, o jeito seguro é:

```python
# NUNCA
db.execute(text(f"SELECT * FROM usuario WHERE email = '{email}'"))
# SEMPRE
db.execute(text("SELECT * FROM usuario WHERE email = :email"), {"email": email})
```

Testes (passando): `test_busca_de_profissional_trata_sql_injection_como_texto`,
`test_validacao_de_documento_trata_sql_injection_como_texto`,
`test_login_com_sql_injection_e_recusado_sem_detalhes` — com `' OR '1'='1`,
`'; DROP TABLE usuario; --`, `" OR 1=1 --` e `UNION SELECT`.

---

## 4. Testes automatizados — `backend/tests/test_seguranca.py`

```bash
cd backend
../.venv/bin/python -m pytest tests/test_seguranca.py -v      # só segurança
../.venv/bin/python -m pytest -rx                              # tudo, listando os xfail
```

Resultado atual: **131 passaram, 9 `xfail`** (suíte completa do projeto: 298 passaram, 9 `xfail`).

**Como a suíte funciona:**

- Usa **tokens reais**: cria uma `SessaoLogin` no banco de teste e assina o JWT com
  `gerar_token_acesso` — nada de `dependency_overrides` na autenticação, então o caminho
  inteiro (cabeçalho → JWT → sessão → usuário → perfil) é testado.
- Monta o app lendo os `include_router` do `main.py`: as rotas e prefixos são os mesmos da API
  real, e uma rota nova entra automaticamente nos testes.
- Os testes de entrada inválida têm **testes de controle** (a mesma requisição com dados válidos
  é aceita), para garantir que o 4xx vem do campo malicioso e não de outro erro.
- `xfail(strict=True)` marca as falhas que **ainda existem** (achados 1 e 6). Quando corrigirem,
  o pytest acusa `XPASS(strict)` como falha: aí é só apagar o `@pytest.mark.xfail` daquele teste,
  que passa a proteger a correção.

| Grupo | Testes | O que verificam |
|-------|--------|-----------------|
| Sem token / token inválido | `test_rota_protegida_sem_token_responde_401`, `..._com_token_invalido_...` (36 rotas cada) | Toda rota com login responde 401 sem token e com token lixo |
| Tokens forjados | `..._assinatura_de_outra_chave_...`, `..._alg_none_...`, `..._sessao_encerrada_...`, `..._sessao_inexistente_...`, `test_conta_inativa_nao_usa_token_antigo` | Assinatura, algoritmo `none`, logout e conta inativa |
| Perfis | `test_rotas_de_administracao_recusam_quem_nao_e_admin`, `test_admin_acessa_rotas_de_administracao` | 403 para paciente/profissional nas rotas de admin |
| Rotas públicas | `test_rotas_publicas_sao_so_as_esperadas`, `test_listagem_publica_de_horarios_so_traz_dados_da_agenda`, `test_rotas_da_agenda_e_consultas_exigem_login` (xfail) | Nenhuma rota pública nova sem justificativa; listagem de horários sem dado pessoal; achado 1 |
| IDOR | `test_usuario_nao_le_dados_de_outra_conta`, `..._altera_nem_exclui_outra_conta`, `test_profissional_nao_altera_valor_de_outro_profissional`, `test_paciente_nao_ve_consulta_de_outro_paciente`, `..._pagamento_de_consulta_alheia`, `test_estranho_nao_ve_videochamada_da_consulta`, `test_profissional_nao_emite_receita_em_consulta_de_outro`, `test_paciente_nao_le_documento_de_outro_paciente`, `test_paciente_nao_avalia_consulta_de_outro` + 4 xfail | Um usuário não lê nem altera dados de outro |
| SQL injection | 3 testes × 4 payloads | Payloads tratados como texto, tabelas intactas |
| Login | `test_login_nao_revela_se_a_conta_existe`, `test_login_bloqueia_apos_tentativas_erradas`, `test_senha_nao_e_guardada_em_texto_puro` | Mensagem genérica, bloqueio (429), hash Argon2 |
| Entrada inválida | cadastro (5 casos), avaliação (5), atestado (3), upload `.php`, anexo com conteúdo falso, HTML no nome, JSON quebrado | 422/400 sem gravar nada e sem stack trace |

---

## 5. Ordem sugerida de correção

1. Achado 1 (autenticação das 5 rotas) — e remover os `xfail` correspondentes.
2. Achado 2 (admin/seed) e achado 3 (`SECRET_KEY`) — só configuração, rápido.
3. Achados 4, 5 e 6.
4. Os de risco baixo, conforme o tempo.
