import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


class BlockchainUtils:
    """
    Utility class to interact with Polygon blockchain.
    """

    def __init__(self):
        rpc_url = os.getenv("POLYGON_RPC_URL")
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")
        self.wallet_address = os.getenv("WALLET_ADDRESS")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not self.w3.is_connected():
            raise Exception("Blockchain connection failed")

    def get_balance(self):
        """
        Get wallet balance.
        """
        balance = self.w3.eth.get_balance(self.wallet_address)
        return self.w3.from_wei(balance, "ether")

    def get_nonce(self):
        """
        Get transaction nonce.
        """
        return self.w3.eth.get_transaction_count(self.wallet_address)

    def send_hash_transaction(self, document_hash: str):
        """
        Send a blockchain transaction with the document hash in data field.
        """

        nonce = self.get_nonce()

        tx = {
            "nonce": nonce,
            "to": self.wallet_address,
            "value": 0,
            "gas": 100000,
            "gasPrice": self.w3.to_wei("30", "gwei"),
            "data": self.w3.to_hex(text=document_hash),
            "chainId": 80002  # Polygon Amoy testnet
        }

        signed_tx = self.w3.eth.account.sign_transaction(
            tx,
            self.private_key
        )

        tx_hash = self.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        return tx_hash.hex()

    def get_transaction(self, tx_hash: str):
        """
        Fetch transaction details.
        """
        return self.w3.eth.get_transaction(tx_hash)

    def wait_for_receipt(self, tx_hash: str):
        """
        Wait until transaction is mined.
        """
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt