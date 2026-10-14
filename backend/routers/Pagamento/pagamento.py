from flask import Blueprint, render_template
from apiMercadoPago import gerar_link_pagamento

# Cria o Blueprint (o nome 'web' é só um apelido interno)
web_bp = Blueprint('web', __name__)

@web_bp.route("/")
def homepage():
    return render_template("homepage.html")

@web_bp.route("/compracerta")
def compra_certa():
    return render_template("compracerta.html")

@web_bp.route("/compraerrada")
def compra_errada():
    return render_template("compraerrada.html")