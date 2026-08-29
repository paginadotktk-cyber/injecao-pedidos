import requests
import random
import time
import uuid
from datetime import datetime, timezone, timedelta

url = "https://api.utmify.com.br/api-credentials/orders"
token = "AAqWMWSWaaY3X56E482A9igntGOcipUKufLG"

headers = {
    "x-api-token": token,
    "Content-Type": "application/json"
}

def calcular_valor_execucao():
    # Converte explicitamente para Horário de Brasília (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br)
    
    dia_semana = agora.weekday()  # 0 a 4 = Seg a Sex | 5 e 6 = Sáb e Dom
    hora_atual = agora.hour

    # Segunda a Sexta: 15k a 20k | Fim de semana: 25k a 30k
    if dia_semana < 5:
        meta_dia = random.uniform(15000.01, 19999.99)
    else:
        meta_dia = random.uniform(25000.01, 29999.99)

    # 07h -> 30% | 14h -> 40% | 23h -> 30%
    if hora_atual < 10:
        percentual = 0.30
    elif hora_atual < 18:
        percentual = 0.40
    else:
        percentual = 0.30

    faturamento_alvo = round(meta_dia * percentual + random.uniform(-30.0, 30.0), 2)
    return max(faturamento_alvo, 100.0)

total_transacoes = random.randint(3, 7)
faturamento_alvo = calcular_valor_execucao()

print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Meta: R$ {faturamento_alvo:.2f} ({total_transacoes} vendas)")

valores = []
for i in range(total_transacoes - 1):
    media_restante = (faturamento_alvo - sum(valores)) / (total_transacoes - i)
    val = round(random.uniform(media_restante * 0.6, media_restante * 1.4), 2)
    valores.append(val)

ultimo_valor = round(faturamento_alvo - sum(valores), 2)
valores.append(ultimo_valor)
random.shuffle(valores)

for i, valor_venda in enumerate(valores, 1):
    order_id = f"MAC-INJECT-{uuid.uuid4().hex[:6].upper()}"
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    valor_em_centavos = int(round(valor_venda * 100))
    
    payload = {
        "orderId": order_id,
        "platform": "TerminalMac",
        "paymentMethod": "credit_card",
        "status": "paid",
        "createdAt": now_utc,
        "approvedDate": now_utc,
        "refundedAt": None,
        "customer": {
            "name": f"Cliente Validação {i}",
            "email": f"cliente{i}@teste.com",
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
            print(f"[{i}/{total_transacoes}] ✅ Sucesso: R$ {valor_venda:.2f} (ID: {order_id})")
        else:
            print(f"[{i}/{total_transacoes}] ❌ Erro {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
        break
        
    time.sleep(1)

print(f"Finalizado. Total: R$ {sum(valores):.2f}")
