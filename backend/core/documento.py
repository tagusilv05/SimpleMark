"""Tipo do documento clínico.

documento_clinico.tipo é Boolean no modelo do grupo. O significado de cada valor
não estava escrito em lugar nenhum, então fica centralizado aqui: se o combinado
for o contrário, troca-se só estas duas constantes.
"""

TIPO_RECEITA = True
TIPO_ATESTADO = False

RECEITA = "RECEITA"
ATESTADO = "ATESTADO"


def descrever_tipo(tipo: bool) -> str:
    return RECEITA if tipo == TIPO_RECEITA else ATESTADO
