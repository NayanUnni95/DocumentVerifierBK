from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

rpc = os.getenv("POLYGON_RPC_URL")
address = os.getenv("WALLET_ADDRESS")

w3 = Web3(Web3.HTTPProvider(rpc))

print("Connected:", w3.is_connected())

balance = w3.eth.get_balance(address)
print("Balance:", w3.from_wei(balance, "ether"))