# generate_keys.py
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Gera par de chaves
private_key = ec.generate_private_key(ec.SECP256R1())

# Exporta a chave privada em formato PEM e depois base64url (como esperado pelo VAPID)
private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip("=")

# Exporta a chave pública no formato correto (raw)
public_key = private_key.public_key()
public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, 'big')
y = public_numbers.y.to_bytes(32, 'big')
public_bytes = b'\x04' + x + y  # uncompressed point format
public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip("=")

# Imprime
print("--- SUAS CHAVES VAPID ---\n")
print(f'VAPID_PUBLIC_KEY = "{public_key_b64}"')
print(f'VAPID_PRIVATE_KEY = "{private_key_b64}"')
print("\n-------------------------")
