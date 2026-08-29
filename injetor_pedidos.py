import requests
import random
import uuid
from datetime import datetime, timezone, timedelta

url = "https://api.utmify.com.br/api-credentials/orders"
token = "AAqWMWSWaaY3X56E482A9igntGOcipUKufLG"

headers = {
    "x-api-token": token,
    "Content-Type": "application/json"
}

def calcular_valor_execucao():
    # Converte para o Horário de Brasília (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br)
    
    dia_semana = agora.weekday()  # 0 a 4 = Seg a Sex | 5 e 6 = Sab e Dom
    hora_atual = agora.hour

    # 1. Meta diária quebrada
    if dia_semana < 5:
        # Segunda a Sexta: 15.000,00 a 19.999,99
        meta_dia = random.uniform(15000.01, 19999.99)
    else:
        # Sabado e Domingo: 25.000,00 a 29.999,99
        meta_dia = random.uniform(25000.01, 29999.99)

    # 2. Percentual por horário: 07h (30%), 14h (40%), 23h (30%)
    if hora_atual < 10:
        percentual = 0.30
    elif hora_atual < 18:
        percentual = 0.40
    else:
        percentual = 0.30

    # Valor cheio da rodada com centavos aleatórios quebrados
    faturamento_alvo = round(meta_dia * percentual + random.uniform(-25.0, 25.0), 2)
    return max(faturamento_alvo, 100.0)

# Define o valor único da transação
valor_venda = calcular_valor_execucao()
valor_em_centavos = int(round(valor_venda * 100))

order_id = f"MAC-INJECT-{uuid.uuid4().hex[:6].upper()}"
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

print("=" * 55)
print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Disparo Único")
print(f"Valor da Venda: R$ {valor_venda:.2f} (ID: {order_id})")
print("=" * 55)

payload = {
    "orderId": order_id,
    "platform": "TerminalMac",
    "paymentMethod": "credit_card",
    "status": "paid",
    "createdAt": now_utc,
    "approvedDate": now_utc,
    "refundedAt": None,
    "customer": {
        "name": "Cliente Validação",
        "email": "cliente@teste.com",
        "phone": "+5511999999999",
        "document": None,
        "country": "BR"
    },
    "products": [
        {
            "id": "PROD-TESTE",
            "name": "Produto Escala",
            "planId": None,
            "planName": None,
            "quantity": 1,
            "priceInCents": valor_em_centavos
        }
    ],
    "trackingParameters": {
        "utm_source": "tiktok",
        "utm_medium": "cpc",
        "utm_campaign": "escala_teste_mac",
        "utm_content": None,
        "utm_term": None
    },
    "commission": {
        "totalPriceInCents": valor_em_centavos,
        "gatewayFeeInCents": 0,
        "userCommissionInCents": valor_em_centavos,
        "currency": "BRL"
    },
    "isTest": False
}

try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        print(f"✅ Sucesso: Venda de R$ {valor_venda:.2f} injetada com sucesso!")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
except Exception as e:
    print(f"Erro de conexão: {e}")
