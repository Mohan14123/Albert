import secrets


def generate_keys():
    jwt_secret = secrets.token_hex(32)
    token_encryption_key = secrets.token_hex(32)
    print("Add these to your .env file:")
    print(f"JWT_SECRET={jwt_secret}")
    print(f"TOKEN_ENCRYPTION_KEY={token_encryption_key}")

if __name__ == "__main__":
    generate_keys()
