import os

import mercadopago


def gerar_link_pagamento(preco_consulta):
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN nao configurado.")
    sdk = mercadopago.SDK(token)

    payment_data = {
        "items": [
            {
                "id": "id_usuario",
                "title": "titulo",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": preco_consulta,
            }
        ],
        "back_urls": {
            "success": "https://127.0.0.1:8080/compracerta",
            "failure": "https://127.0.0.1:8080/compraerrada",
            "pending": "https://127.0.0.1:8080/compraemprocesso",
        },
        "auto_return": "all"
    }

    result = sdk.preference().create(payment_data)
    payment = result["response"]
    link_iniciar_pagamento = payment["init_point"]
    return link_iniciar_pagamento