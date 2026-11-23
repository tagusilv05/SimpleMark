#!/usr/bin/env bash
# Regenera a documentação do Simple Mark (HTML e PDF) a partir das docstrings.
# Uso, na raiz do projeto (com o ambiente virtual ativado):
#   bash docs/gerar_docs.sh          # HTML e PDF
#   bash docs/gerar_docs.sh html     # só HTML
#   bash docs/gerar_docs.sh pdf      # só PDF
set -euo pipefail

cd "$(dirname "$0")/.."

ALVO="${1:-todos}"
PACOTES=(core database dependencies models schemas repositories services routers seed)

# 1. Recria os .rst dos módulos (sphinx-apidoc), um por pacote do backend.
#    repositories/consulta_profissional.py fica de fora: é código não usado e
#    não importa (faz "from models import Consulta", que não existe).
rm -rf docs/api
for pacote in "${PACOTES[@]}"; do
    sphinx-apidoc -f -M -e -T --implicit-namespaces -o docs/api "backend/$pacote" \
        "backend/$pacote/__pycache__" "backend/$pacote/*/__pycache__" \
        "backend/repositories/consulta_profissional.py" > /dev/null
done

# 2. Gera a saída.
if [[ "$ALVO" == "todos" || "$ALVO" == "html" ]]; then
    sphinx-build -b html docs docs/_build/html
    echo "HTML: docs/_build/html/index.html"
fi
if [[ "$ALVO" == "todos" || "$ALVO" == "pdf" ]]; then
    sphinx-build -b rinoh docs docs/_build/pdf
    echo "PDF:  docs/_build/pdf/SimpleMark.pdf"
fi
