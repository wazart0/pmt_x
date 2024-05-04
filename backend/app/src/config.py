from dotenv import dotenv_values
import json

config = dotenv_values("/env/.env.local")
config = dotenv_values("/env/.env.local")

print("\nCONFIG:")
[print(f"\t{key}={config[key]}") for key in config]
print()


config['DB_URI'] = f'postgresql+psycopg2://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_NAME']}'
