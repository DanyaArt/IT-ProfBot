import socks
import socket
import requests

PROXY_HOST = "turbo.telehelp.top"
PROXY_PORT = 443

# Настройка SOCKS5
socks.set_default_proxy(socks.SOCKS5, PROXY_HOST, PROXY_PORT, rdns=True)
socket.socket = socks.socksocket

try:
    response = requests.get('https://api.telegram.org', timeout=10)
    print(f"✅ Прокси работает! Статус: {response.status_code}")
except Exception as e:
    print(f"❌ Прокси НЕ работает: {e}")
    print("💡 Рекомендуется использовать VPN вместо этого прокси")