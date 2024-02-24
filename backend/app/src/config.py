from dotenv import dotenv_values
import json

config = dotenv_values("/env/.env.local")

print("\nCONFIG:")
[print(f"\t{key}={config[key]}") for key in config]
print()
