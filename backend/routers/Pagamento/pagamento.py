"""Blueprint Flask legado com as páginas do protótipo de pagamento.

Não é registrado no app FastAPI; as rotas de pagamento em uso ficam em
routers/pagamento.py.
"""

from flask import Blueprint, render_template
from apiMercadoPago import gerar_link_pagamento

# Cria o Blueprint (o nome 'web' é só um apelido interno)
web_bp = Blueprint('web', __name__)

@web_bp.route("/")
def homepage():
    """Renderiza a página inicial do protótipo."""
    return render_template("homepage.html")

@web_bp.route("/compracerta")
def compra_certa():
    """Renderiza a página de pagamento aprovado."""
    return render_template("compracerta.html")

@web_bp.route("/compraerrada")
def compra_errada():
    """Renderiza a página de pagamento recusado."""
    return render_template("compraerrada.html")