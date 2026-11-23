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
    """Renderiza a página inicial do protótipo.

    Returns:
        str: HTML renderizado de ``homepage.html``.
    """
    return render_template("homepage.html")

@web_bp.route("/compracerta")
def compra_certa():
    """Renderiza a página de pagamento aprovado.

    Returns:
        str: HTML renderizado de ``compracerta.html``.
    """
    return render_template("compracerta.html")

@web_bp.route("/compraerrada")
def compra_errada():
    """Renderiza a página de pagamento recusado.

    Returns:
        str: HTML renderizado de ``compraerrada.html``.
    """
    return render_template("compraerrada.html")