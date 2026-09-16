import requests
import random
import uuid
from datetime import datetime, timezone, timedelta

url = "https://api.utmify.com.br/api-credentials/orders"
token = "zZ6095MU1lEBKmJ4xluZxIMbVh5pnBiATart"

headers = {
    "x-api-token": token,
    "Content-Type": "application/json"
}

def calcular_valor_execucao():
    # Converte para o Horário de Brasília (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br)
    dia_semana = agora.weekday()  # 0 a 4 = Seg a Sex | 5 e 6 = Sab e Dom

    # Matemática do Faturamento da Shopify
    # Ticket Médio: R$ 95,88
    # Seg-Sex: Média 37 vendas/dia -> R$ 3.547,56
    # Sab-Dom (+30%): Média 48 vendas/dia -> R$ 4.602,24
    
    # Meta: Valor médio faturado no dia + 10%
    if dia_semana < 5:
        # Alvo da semana: ~R$ 3.902,31 (Com variação aleatória de R$ 50 para mais ou menos)
        valor_base = random.uniform(3850.00, 3950.00)
    else:
        # Alvo final de semana: ~R$ 5.062,46 (Com variação aleatória de R$ 50)
        valor_base = random.uniform(5010.00, 5110.00)

    # Adiciona alguns centavos quebrados finais para realismo
    faturamento_alvo = round(valor_base + random.uniform(-10.0, 10.0), 2)
    return max(faturamento_alvo, 100.0)

valor_venda = calcular_valor_execucao()
valor_em_centavos = int(round(valor_venda * 100))

order_id = f"MAC-INJECT-{uuid.uuid4().hex[:6].upper()}"
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

print("=" * 55)
print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Disparo Único UTMify")
print(f"Valor da Venda Consolidada (+10%): R$ {valor_venda:.2f} (ID: {order_id})")
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
        print(f"✅ Sucesso: Venda de R$ {valor_venda:.2f} injetada na UTMify!")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
except Exception as e:
    print(f"Erro de conexão: {e}")
