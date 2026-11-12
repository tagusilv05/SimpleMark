#!/usr/bin/env bash
# Script de testes do SimpleMark.
#
# Uso:
#   ./testar.sh                 # backend (pytest) + frontend (lint + build)
#   ./testar.sh backend         # só os testes do backend
#   ./testar.sh frontend        # só lint e build do frontend
#   ./testar.sh smoke           # smoke test da API já rodando (docker compose up)
#   ./testar.sh tudo            # backend + frontend + smoke
#
# Argumentos extras depois de "backend" vão direto para o pytest, ex.:
#   ./testar.sh backend -k videochamada -x
#
# Variáveis:
#   API_URL   (padrão http://localhost:8080)  base da API no smoke test
#   FRONT_URL (padrão http://localhost)       front servido pelo Docker
#   PYTHON    (padrão python3)                interpretador usado para criar a venv

set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$RAIZ/.venv"
PYTHON="${PYTHON:-python3}"
API_URL="${API_URL:-http://localhost:8080}"
FRONT_URL="${FRONT_URL:-http://localhost}"

VERDE=$'\e[32m'; VERMELHO=$'\e[31m'; AMARELO=$'\e[33m'; NEGRITO=$'\e[1m'; FIM=$'\e[0m'
declare -a RESULTADOS=()
FALHOU=0

titulo() { printf '\n%s==> %s%s\n' "$NEGRITO" "$1" "$FIM"; }
ok()     { RESULTADOS+=("${VERDE}✔${FIM} $1"); }
erro()   { RESULTADOS+=("${VERMELHO}✘${FIM} $1"); FALHOU=1; }
aviso()  { RESULTADOS+=("${AMARELO}!${FIM} $1"); }

# ---------------------------------------------------------------- backend
testar_backend() {
  titulo "Backend: pytest"

  if [[ ! -x "$VENV/bin/python" ]]; then
    echo "Criando ambiente virtual em .venv ..."
    "$PYTHON" -m venv "$VENV" || { erro "backend: não foi possível criar a venv"; return; }
  fi

  # Reinstala as dependências só quando o requirements.txt mudar.
  local carimbo="$VENV/.requirements.sha"
  local hash_atual
  hash_atual="$(sha256sum "$RAIZ/requirements.txt" | cut -d' ' -f1)"
  if [[ ! -f "$carimbo" || "$(cat "$carimbo")" != "$hash_atual" ]]; then
    echo "Instalando dependências do backend ..."
    "$VENV/bin/pip" install -q --upgrade pip &&
      "$VENV/bin/pip" install -q -r "$RAIZ/requirements.txt" ||
      { erro "backend: falha ao instalar dependências"; return; }
    echo "$hash_atual" > "$carimbo"
  fi

  # Os testes usam SQLite em memória (ver backend/tests/conftest.py):
  # não precisam do PostgreSQL nem do Docker.
  if (cd "$RAIZ/backend" && "$VENV/bin/python" -m pytest -q "$@"); then
    ok "backend: testes passaram"
  else
    erro "backend: há testes falhando"
  fi
}

# --------------------------------------------------------------- frontend
testar_frontend() {
  titulo "Frontend: lint e build"
  cd "$RAIZ/frontend" || { erro "frontend: pasta não encontrada"; return; }

  # O Vite 8 exige Node 22.18+ (ver "engines" no package.json).
  local node_major
  node_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  if (( node_major < 22 )); then
    erro "frontend: Node $(node -v 2>/dev/null || echo ausente) é antigo; instale o Node 22.18+ (ex.: nvm install 22)"
    cd "$RAIZ"; return
  fi

  if [[ ! -d node_modules ]]; then
    echo "Instalando dependências do frontend ..."
    npm ci || { erro "frontend: falha no npm ci"; cd "$RAIZ"; return; }
  fi

  # Sem --fix: o script só verifica, não altera arquivos.
  if npx --no-install oxlint . && npx --no-install eslint . ; then
    ok "frontend: lint sem erros"
  else
    erro "frontend: lint encontrou problemas"
  fi

  # Build para uma pasta temporária, sem sobrescrever o dist/ do projeto.
  local saida
  saida="$(mktemp -d)"
  if npx --no-install vite build --outDir "$saida" --emptyOutDir; then
    ok "frontend: build compilou"
  else
    erro "frontend: build falhou"
  fi
  rm -rf "$saida"
  cd "$RAIZ"
}

# ------------------------------------------------------------------ smoke
# Confere se uma requisição devolve o status esperado.
checar() {
  local descricao="$1" esperado="$2" metodo="$3" url="$4"; shift 4
  local status
  status="$(curl -s -o /dev/null -w '%{http_code}' -X "$metodo" "$@" "$url")"
  if [[ "$status" == "$esperado" ]]; then
    ok "smoke: $descricao ($status)"
  else
    erro "smoke: $descricao — esperado $esperado, recebido $status"
  fi
}

testar_smoke() {
  titulo "Smoke test da API em $API_URL"

  if ! curl -s -o /dev/null --max-time 5 "$API_URL/openapi.json"; then
    erro "smoke: API fora do ar em $API_URL (rode: docker compose up --build -d)"
    return
  fi

  local v1="$API_URL/api/v1"
  checar "documentação OpenAPI"                    200 GET  "$API_URL/openapi.json"
  checar "busca pública de profissionais"          200 GET  "$v1/profissionais/busca"
  checar "busca rejeita especialidade curta"       422 GET  "$v1/profissionais/busca?especialidade=a"
  checar "/auth/eu sem token é bloqueado"          401 GET  "$v1/auth/eu"
  checar "/auth/eu com token inválido é bloqueado" 401 GET  "$v1/auth/eu" -H "Authorization: Bearer token-invalido"
  checar "login com senha errada é recusado"       401 POST "$v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"identificador":"naoexiste@simplemark.test","senha":"senha-errada-123"}'
  checar "validação de documento inexistente"      404 GET  "$v1/documentos/validar/codigo-que-nao-existe"

  if curl -s -o /dev/null --max-time 5 "$FRONT_URL"; then
    checar "frontend responde" 200 GET "$FRONT_URL/"
  else
    aviso "smoke: frontend não está no ar em $FRONT_URL (ignorado)"
  fi
}

# ------------------------------------------------------------------- main
modo="${1:-padrao}"; [[ $# -gt 0 ]] && shift

case "$modo" in
  backend)  testar_backend "$@" ;;
  frontend) testar_frontend ;;
  smoke)    testar_smoke ;;
  tudo)     testar_backend; testar_frontend; testar_smoke ;;
  padrao)   testar_backend; testar_frontend ;;
  -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
  *) echo "Modo desconhecido: $modo (use backend, frontend, smoke ou tudo)"; exit 2 ;;
esac

titulo "Resumo"
printf '%s\n' "${RESULTADOS[@]}"
exit "$FALHOU"
