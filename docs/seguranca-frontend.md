# Revisão de segurança do front-end — Simple Mark

Revisão feita em ambiente local, sobre o código do repositório (`frontend/`, Vue 3 + Vite + Pinia),
em 22/11/2026. Onde o problema do front só existe porque o back-end deixa de fazer a sua parte,
o back-end também foi olhado (itens marcados como **[back-end]**).

## Resumo

| # | Achado | Risco | Situação |
|---|--------|-------|----------|
| 1 | Rotas da API que o front trata como "só do profissional" não exigem login no back-end | **Alto** | Não corrigido (back-end) — correção proposta |
| 2 | Token de sessão guardado em `localStorage`/`sessionStorage` | **Médio** | Não corrigido (exige mudança no back-end) — mitigações propostas |
| 3 | Sem cabeçalhos de segurança nem CSP no servidor do front (nginx) | **Médio** | Corrigido (cabeçalhos) / CSP em modo *report-only* |
| 4 | `SECRET_KEY` do JWT cai num valor padrão público **[back-end]** | **Médio** | Não corrigido (configuração) |
| 5 | Links vindos da API usados em `<iframe :src>`, `<a :href>` e `window.location` sem checar o protocolo | Baixo | Corrigido |
| 6 | `window.open` / `target="_blank"` sem `noopener noreferrer` (*reverse tabnabbing*) | Baixo | Corrigido |
| 7 | Upload da foto de perfil sem nenhuma validação no front | Baixo | Corrigido |
| 8 | Dependências: 3 vulnerabilidades moderadas (`minimatch` via `eslint`) e pacotes desatualizados | Baixo | Corrigido (`npm audit fix`) |
| 9 | Limite do comentário da avaliação diferente entre front (500) e back (1000) | Baixo | Não corrigido (só inconsistência) |
| — | XSS por `v-html` / `innerHTML` | — | Nada encontrado ✅ |
| — | Segredos (chaves, tokens) escritos no front | — | Nada encontrado ✅ |

**O que já estava bom** (vale manter):

- Nenhum `v-html`, `innerHTML`, `eval` ou `new Function` em `src/`. Tudo é renderizado com `{{ }}`, que
  o Vue escapa automaticamente.
- Redirecionamento pós-login protegido contra *open redirect*: `useLogin.js` só aceita `?redirect=`
  que comece com `/` e não com `//`.
- O token é conferido no servidor a cada 5 minutos de navegação (`validarSessao`) e o 401 limpa a
  sessão local; o logout encerra a sessão também no servidor.
- `consultasAgendadas.vue` já zerava `aba.opener` antes de abrir a sala do Jitsi.
- A URL da API vem de `VITE_API_URL`; o token do Mercado Pago fica só no back-end (variável de ambiente).
- `dist/` e `.env` estão no `.gitignore`.

---

## 1. Rotas do back-end sem autenticação que o front "protege" — **ALTO** [back-end]

**Categoria:** validação/autorização que deveria existir no back-end.

**Onde:** o front só mostra a agenda e as consultas para quem está logado como profissional
(guarda de rotas em `frontend/src/router/index.js:316`), mas a guarda roda no navegador e pode
ser ignorada por qualquer pessoa que chame a API direto (curl, Postman, console do navegador).
Estas rotas não pedem token nenhum:

| Rota | Arquivo | O que um anônimo consegue |
|------|---------|---------------------------|
| `GET /api/v1/consultas_profissionais/{id_profissional}/consultas` | `backend/routers/consulta_profissional.py:14` | Ver as consultas **e os dados dos pacientes** de qualquer profissional, trocando o id na URL (IDOR) |
| `POST/PUT/DELETE /profissional/horarios[/{id}]` | `backend/routers/horarios_profissional.py` | Criar, alterar e apagar horários da agenda de qualquer profissional |
| `GET /profissional/horarios` | idem | Listar a agenda de qualquer profissional |
| `POST /consulta/confirmar-consulta` | `backend/routers/confirmar_consulta.py:19` | Criar consultas em nome de qualquer paciente |

Usadas pelo front em `dashboardProfissional.vue:81,160` e `configuracaoAgendaProfissional.vue:87,119,211-248`.

**Como corrigir:** usar as dependências que o projeto já tem em `backend/dependencies/autenticacao.py`
(`UsuarioAtual`, `PacienteAtual`) e conferir que o recurso pertence a quem está logado. Exemplo
para a listagem de consultas:

```python
# Antes
@router.get("/{id_profissional}/consultas", response_model=list[ConsultaProfissionalOut])
def consultas_do_profissional(
    id_profissional: int,
    status: str | None = Query("agendada"),
    ...
    db: Session = Depends(get_db),
):

# Depois
from dependencies.autenticacao import UsuarioAtual

@router.get("/{id_profissional}/consultas", response_model=list[ConsultaProfissionalOut])
def consultas_do_profissional(
    usuario: UsuarioAtual,
    id_profissional: int,
    status: str | None = Query("agendada"),
    ...
    db: Session = Depends(get_db),
):
    profissional = db.query(Profissional).filter_by(id_usuario=usuario.id_usuario).first()
    if profissional is None or profissional.id_profissional != id_profissional:
        raise HTTPException(status_code=403, detail="Acesso negado.")
```

O mesmo vale para os horários (conferir que o `id_profissional_especialidade` do payload/horário
é do profissional logado) e para `confirmar-consulta` (usar `PacienteAtual` e ignorar o
`id_paciente` vindo do corpo). O front não precisa mudar: ele já manda o `Authorization: Bearer`
em todas as chamadas (`frontend/src/services/api.js:104`).

> Não apliquei esta correção porque ela muda o comportamento da API e os testes do back-end
> precisam ser ajustados junto; fica como prioridade número 1 antes da entrega.

---

## 2. Token de sessão no `localStorage` / `sessionStorage` — **MÉDIO**

**Onde:** `frontend/src/stores/auth.js:36-65` — o objeto `{ token, usuario }` é salvo em
`localStorage` ("Lembrar de mim") ou `sessionStorage`, na chave `simplemark.auth`.

**Risco:** qualquer JavaScript que rode na página lê esse armazenamento. Se um dia entrar um XSS
(uma dependência comprometida, um `v-html` futuro, um script de terceiros), o atacante copia o token
e usa a conta da vítima de outra máquina. No `localStorage` o token sobrevive ao fechar o navegador,
o que aumenta a janela. Os dados do usuário salvos junto (nome, e-mail, perfil) também ficam
expostos a quem usar o mesmo computador.

Atenuantes que já existem: o token está ligado a uma sessão no banco (`sid`), que expira com 24 h sem
uso e é revogada no logout/banimento; o perfil salvo no navegador é reconferido no servidor.

**Como corrigir (ideal):** o back-end devolver o token num cookie
`HttpOnly; Secure; SameSite=Strict` em `/auth/login/confirmar`, ler o cookie em `sessao_atual` e o
front parar de guardar o token (passar a usar `fetch(..., { credentials: 'include' })`). Com
cookie é preciso proteção contra CSRF (o `SameSite=Strict` resolve na maioria dos casos).

**Mitigações se não der tempo:** manter o "Lembrar de mim" desmarcado por padrão (usa
`sessionStorage`), não salvar dados além do necessário junto do token e ativar a CSP do item 3,
que dificulta a execução de scripts injetados.

---

## 3. Sem cabeçalhos de segurança / CSP no nginx — **MÉDIO** — corrigido em parte

**Onde:** `Dockerfile.front` (configuração do nginx que serve o `dist/`).

**Risco:** sem `X-Frame-Options`/`frame-ancestors` o site pode ser embutido num `<iframe>` de outro
domínio (*clickjacking*); sem `X-Content-Type-Options` o navegador pode "adivinhar" o tipo de um
arquivo; sem CSP não há segunda barreira contra XSS.

**Antes:**

```dockerfile
RUN echo 'server { \
  listen 8000; \
  root /usr/share/nginx/html; \
  index index.html; \
  location / { \
```

**Depois:**

```dockerfile
RUN echo 'server { \
  listen 8000; \
  root /usr/share/nginx/html; \
  index index.html; \
  add_header X-Content-Type-Options "nosniff" always; \
  add_header X-Frame-Options "DENY" always; \
  add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
  add_header Permissions-Policy "geolocation=()" always; \
  add_header Content-Security-Policy-Report-Only "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: http://localhost:8080; connect-src 'self' http://localhost:8080; frame-src https://meet.jit.si; object-src 'none'; base-uri 'self'; frame-ancestors 'none'" always; \
  location / { \
```

(no arquivo real as aspas simples da CSP estão escapadas como `'"'"'` por causa do `echo '...'`;
a configuração gerada foi validada com `nginx -t`.)

A CSP foi colocada em modo **Report-Only**: o navegador só mostra no console o que *seria*
bloqueado, sem quebrar nada. Próximo passo: subir com `docker compose up --build`, navegar por
todas as telas, conferir o console e, sem violações, trocar
`Content-Security-Policy-Report-Only` por `Content-Security-Policy`. Se a API ou o Jitsi mudarem
de endereço (`VITE_API_URL`, `JITSI_BASE_URL`), ajustar `connect-src`, `img-src` e `frame-src`.

---

## 4. `SECRET_KEY` do JWT com valor padrão público — **MÉDIO** [back-end]

**Categoria:** segredos.

**Onde:** `backend/core/parametros.py:12` usa
`os.getenv("SECRET_KEY", "simplemark-dev-secret-troque-em-producao")`, e `compose.yaml` não
define `SECRET_KEY`. Ou seja, no Docker os tokens são assinados com uma chave que está no GitHub.

**Risco:** quem conhece a chave consegue assinar tokens. Hoje o estrago é limitado porque o token
também precisa de um `sid` de sessão ativa no banco, mas a proteção deixa de depender da assinatura.

**Como corrigir:** gerar uma chave (`python -c "import secrets; print(secrets.token_urlsafe(48))"`),
colocar no `.env` e repassar no `compose.yaml` (`SECRET_KEY: ${SECRET_KEY}`). Idealmente o back-end
deveria se recusar a subir sem ela fora do ambiente de teste.

Sobre o front: **nenhum segredo foi encontrado em `frontend/src`**. Lembrete importante — toda
variável `VITE_*` vai parar dentro do JavaScript entregue ao navegador, então só use `VITE_` para
coisas públicas (como a URL da API). Tokens do Mercado Pago, senhas de SMTP etc. ficam só no back-end,
como já está hoje.

---

## 5. Links da API em `iframe`/`href`/`location` sem checar o protocolo — **BAIXO** — corrigido

**Categoria:** XSS.

**Onde:** quatro lugares usavam uma URL vinda do servidor diretamente como destino:

- `views/profissional/chamadaAtendimento.vue` — `<iframe :src="meetLink">` (sala do Jitsi);
- `views/paciente/consultasAgendadas.vue` — `aba.location.href = dados.meet_link`;
- `views/pagamento/PagamentoView.vue` — `window.location.assign(resposta.init_point)` (Mercado Pago);
- `components/shared/DocumentoEmitido.vue` — `<a :href="documento.url_validacao">`.

**Risco:** o Vue escapa texto, mas **não** bloqueia `javascript:` em `:src`/`:href`. Se algum desses
valores chegasse como `javascript:...` ou `data:text/html,...` (dado adulterado no banco,
variável de ambiente errada, resposta interceptada), o código rodaria na origem do Simple Mark —
inclusive com acesso ao token do item 2. Hoje os valores são gerados pelo nosso back-end, por isso o
risco é baixo; a correção é defesa em profundidade.

**Correção:** novo helper `frontend/src/utils/url.js`, que só aceita URLs absolutas `http(s)`:

```js
export function urlExternaSegura(valor) {
  if (typeof valor !== 'string' || !valor.trim()) return null
  try {
    const url = new URL(valor.trim())
    return PROTOCOLOS_PERMITIDOS.has(url.protocol) ? url.toString() : null
  } catch {
    return null
  }
}
```

Testado: `https://meet.jit.si/sala` passa; `javascript:alert(1)`, `JaVaScRiPt:...`,
`data:text/html,...`, caminhos relativos, vazio e `null` viram `null`.

**`chamadaAtendimento.vue` — antes / depois:**

```js
// antes
meetLink.value = data.meet_link
// depois
meetLink.value = urlExternaSegura(data.meet_link)
```

**`consultasAgendadas.vue` — antes / depois:**

```js
// antes
if (!dados.meet_link) throw new Error('A chamada desta consulta ainda não está disponível.')
if (aba) {
  aba.opener = null
  aba.location.href = dados.meet_link
} else {
  window.location.href = dados.meet_link
}

// depois
const link = urlExternaSegura(dados.meet_link)
if (!link) throw new Error('A chamada desta consulta ainda não está disponível.')
if (aba) {
  aba.opener = null
  aba.location.href = link
} else {
  window.location.href = link
}
```

**`PagamentoView.vue` — antes / depois:**

```js
// antes
gravarMarca(consulta.value.id_consulta)
window.location.assign(resposta.init_point)

// depois
const checkout = urlExternaSegura(resposta.init_point)
if (!checkout) throw new Error('Link de pagamento inválido. Tente novamente.')
gravarMarca(consulta.value.id_consulta)
window.location.assign(checkout)
```

**`DocumentoEmitido.vue` — antes / depois** (inclui o item 6):

```vue
<!-- antes -->
<a :href="documento.url_validacao" target="_blank" rel="noopener" ...>

<!-- depois -->
<script setup>
const linkValidacao = computed(() => urlExternaSegura(props.documento.url_validacao))
</script>
<a v-if="linkValidacao" :href="linkValidacao" target="_blank" rel="noopener noreferrer" ...>
```

---

## 6. `window.open` sem `noopener` (*reverse tabnabbing*) — **BAIXO** — corrigido

**Onde:** `frontend/src/layouts/shared/PerfilConta.vue:220` (botão "Buscar CEP").

**Risco:** a página aberta (site dos Correios) recebe `window.opener` e pode trocar a aba do
Simple Mark por uma página falsa de login enquanto o usuário está na outra aba.

```js
// antes
window.open('https://buscacepinter.correios.com.br/app/endereco/index.php', '_blank')
// depois
window.open('https://buscacepinter.correios.com.br/app/endereco/index.php', '_blank', 'noopener,noreferrer')
```

Em `DocumentoEmitido.vue` o `rel="noopener"` virou `rel="noopener noreferrer"` (também não envia
a URL interna como *Referer*).

---

## 7. Upload da foto de perfil sem validação no front — **BAIXO** — corrigido

**Categoria:** validação.

**Onde:** `frontend/src/components/profissional/ProfilePhotoCard.vue` aceitava `image/*` e enviava
qualquer arquivo. O back-end (`backend/services/porfissional_minha_conta.py:41-55,146-149`) já
recusa extensões fora de JPG/PNG/WEBP/GIF e arquivos acima de 5 MB — então o servidor está protegido;
no front faltava só o aviso imediato (e `image/*` aceitava SVG, que o back recusaria).

```js
// antes
function onFileChange(event) {
  const file = event.target.files?.[0]
  if (file) emit('change', file)
  event.target.value = ''
}
```
```vue
<input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileChange" />
```

```js
// depois — mesmas regras do back-end
const TIPOS_ACEITOS = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
const TAMANHO_MAX = 5 * 1024 * 1024 // 5 MB

function onFileChange(event) {
  const file = event.target.files?.[0]
  erro.value = ''
  if (file && !TIPOS_ACEITOS.includes(file.type)) {
    erro.value = 'Envie uma imagem JPG, PNG, WEBP ou GIF.'
  } else if (file && file.size > TAMANHO_MAX) {
    erro.value = 'A imagem deve ter no máximo 5 MB.'
  } else if (file) {
    emit('change', file)
  }
  event.target.value = ''
}
```
```vue
<input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp,image/gif"
       class="hidden" @change="onFileChange" />
<p v-if="erro" class="w-full text-sm text-red-600" role="alert">{{ erro }}</p>
```

**Sugestão extra [back-end]:** o servidor confere só a *extensão* do nome do arquivo. Para ser
mais robusto, conferir também o conteúdo (assinatura do arquivo, por exemplo abrindo com Pillow,
que já está instalado via `qrcode[pil]`).

---

## 8. Dependências (`npm audit`) — **BAIXO** — corrigido

**Antes** (`cd frontend && npm audit`):

```
minimatch  7.0.0 - 11.0.0
Severity: moderate
minimatch has potential denial of service via globparts amplification - GHSA-g3hv-75wg-m249
  @eslint/config-array  0.23.0 - 0.23.5
  eslint  10.0.0-alpha.0 - 10.14.0
3 moderate severity vulnerabilities
```

São dependências só de desenvolvimento (lint), não vão para o site publicado — por isso risco baixo.

**Correção:** `npm audit fix` (atualizou só o `package-lock.json`; `eslint` 10.13.0 → 10.15.0).

**Depois:** `found 0 vulnerabilities`.

`npm outdated` ainda mostra atualizações de *patch* disponíveis (todas compatíveis com as faixas do
`package.json`): `vue` 3.5.44 → 3.5.46, `vite` 8.3.4 → 8.3.8, `vue-router` 5.4.0 → 5.5.1,
`tailwindcss` 4.3.3 → 4.3.5, entre outras. Recomendado rodar `npm update` e testar as telas.
Para acompanhar no futuro: `npm audit` antes de cada entrega.

---

## 9. Validações front × back

O back-end valida tudo o que o front valida nos formulários principais (cadastro de
paciente/profissional, CPF, minha conta, receita/atestado, ouvidoria com limite e tipo de anexo,
código de login/recuperação com 6 dígitos, nota da avaliação de 1 a 5) — ou seja, o front **não**
é a única barreira nesses pontos. Pontos de atenção:

- **Autorização** é o que falta, não validação de campo: ver item 1. Lembre que a guarda de rotas do
  Vue (`router/index.js`) e o perfil salvo no navegador servem só para a experiência do usuário;
  quem decide se pode é sempre a API.
- **Comentário da avaliação** — **Baixo**: o front limita a 500 caracteres
  (`views/paciente/avaliarConsulta.vue:165`) e o back aceita até 1000 (`backend/schemas/avaliacao.py:17`).
  Não é falha de segurança, mas é bom alinhar (escolher um valor e usar nos dois).

---

## Como verificar

```bash
cd frontend
npm audit                 # deve mostrar 0 vulnerabilidades
npx vite build            # build continua funcionando
npx eslint src/utils/url.js src/components/profissional/ProfilePhotoCard.vue \
  src/components/shared/DocumentoEmitido.vue src/layouts/shared/PerfilConta.vue \
  src/views/paciente/consultasAgendadas.vue src/views/profissional/chamadaAtendimento.vue
```

Observação: `npx eslint src/views/pagamento/PagamentoView.vue` acusa um `no-useless-assignment`
na linha 67 (`let status = null`) que já existia antes desta revisão e não tem relação com segurança.

## Arquivos alterados nesta revisão

- `frontend/src/utils/url.js` (novo)
- `frontend/src/views/profissional/chamadaAtendimento.vue`
- `frontend/src/views/paciente/consultasAgendadas.vue`
- `frontend/src/views/pagamento/PagamentoView.vue`
- `frontend/src/components/shared/DocumentoEmitido.vue`
- `frontend/src/layouts/shared/PerfilConta.vue`
- `frontend/src/components/profissional/ProfilePhotoCard.vue`
- `frontend/package-lock.json` (`npm audit fix`)
- `Dockerfile.front` (cabeçalhos de segurança no nginx)
