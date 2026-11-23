"""Configuração do Sphinx para a documentação do Simple Mark.

Gera a documentação a partir das docstrings (padrão Google) do backend.

HTML: ``sphinx-build -b html docs docs/_build/html``
PDF:  ``sphinx-build -b rinoh docs docs/_build/pdf``
"""

import os
import sys
from datetime import date
from pathlib import Path

# -- Caminho do código --------------------------------------------------------
# O backend usa imports absolutos a partir da pasta backend/ (ex.: ``from core.config
# import ...``), então é ela que entra no sys.path.
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "backend"))

# -- Variáveis de ambiente ----------------------------------------------------
# core/config.py levanta ValueError se DATABASE_URL não existir. Para a
# documentação basta um valor fictício: o SQLAlchemy só cria a engine, não
# conecta ao banco na importação. setdefault não sobrescreve um .env real.
os.environ.setdefault("DATABASE_URL", "postgresql://docs:docs@localhost:5432/docs")
os.environ.setdefault("AMBIENTE", "teste")

# -- Informações do projeto ---------------------------------------------------
project = "Simple Mark"
author = "James, João Marcos, Gustavo, Raíssa e Vitor"
copyright = f"{date.today().year}, {author}"
release = "1.0"
version = release

# -- Configuração geral -------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

language = "pt_BR"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Bibliotecas que não estão instaladas no ambiente da documentação (código
# legado de pagamento em routers/Pagamento, feito em Flask). O autodoc as
# substitui por objetos falsos; o app não é afetado. "apiMercadoPago" é
# importado por routers/Pagamento/pagamento.py como módulo de topo.
autodoc_mock_imports = ["mercadopago", "flask", "apiMercadoPago"]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autoclass_content = "both"

# -- Napoleon (docstrings no padrão Google) -----------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
# Seções "Attributes:" viram campos :ivar: (evita duplicar os atributos de dataclasses).
napoleon_use_ivar = True

# -- Saída HTML ---------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_title = "Simple Mark — Documentação"
html_static_path = ["_static"]
html_logo = str(RAIZ / "assets" / "logosm.jpeg")

# -- Saída PDF (rinohtype, sem LaTeX) -----------------------------------------
# O rinohtype não traz tradução para português: registramos uma para "pt_BR",
# senão títulos fixos do PDF (sumário, índice, notas) sairiam em inglês.
# A referência é guardada no próprio módulo do rinoh porque ele a mantém só
# como weakref.
try:
    import rinoh.language as _rinoh_language
    from rinoh.language.cls import Language as _RinohLanguage

    _rinoh_language.PT_BR = _RinohLanguage(
        "pt_br", "Português (Brasil)",  # o rinoh busca o código em minúsculas
        figure="Figura", table="Tabela", contents="Sumário",
        list_of_figures="Lista de figuras", list_of_tables="Lista de tabelas",
        chapter="Capítulo", index="Índice",
        attention="Atenção!", caution="Cuidado!", danger="PERIGO!",
        error="Erro", hint="Dica", important="Importante", note="Nota",
        tip="Dica", warning="Aviso", seealso="Veja também",
    )
except ImportError:  # rinohtype não instalado: só o HTML será gerado
    pass

rinoh_documents = [
    dict(
        doc="index",
        target="SimpleMark",  # gera docs/_build/pdf/SimpleMark.pdf
        title="Simple Mark",
        subtitle="Documentação do código do backend",
        author=author,
        logo=str(RAIZ / "assets" / "logosm.jpeg"),
    )
]
