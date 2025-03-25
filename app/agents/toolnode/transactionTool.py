from langchain.tools import Tool
from langchain.prompts import BasePromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents import initialize_agent, Tool
from typing import Dict, Any
import json
import random


# Define transaction schema
class WalletTransactionSchema:
    def __init__(self, chain_index: str, from_addr: str, to_addr: str, tx_amount: str, token_symbol: str,
                 token_address: str, ext_json: str):
        self.chain_index = chain_index
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.tx_amount = tx_amount
        self.token_symbol = token_symbol
        self.token_address = token_address
        self.ext_json = ext_json


# The main transaction broadcast tool
def transaction_broadcast_tool():
    return Tool(
        name="transactionBroadcastTool",
        func=transaction_broadcast,
        description="Broadcast a transaction to a blockchain"
    )


# Helper function to simulate transaction broadcast
def transaction_broadcast(tool_input: WalletTransactionSchema) -> Dict[str, Any]:
    try:
        # Log the preparation of transaction
        print(
            f"Preparing transaction from {tool_input.from_addr} to {tool_input.to_addr} on chain {tool_input.chain_index}")
        print(f"Token: {tool_input.token_symbol} ({tool_input.token_address}), Amount: {tool_input.tx_amount}")

        # Get chain-specific information
        chain_info = get_chain_info(tool_input.chain_index)

        # Parse additional parameters
        additional_params = {}
        try:
            if tool_input.ext_json:
                additional_params = json.loads(tool_input.ext_json)
        except json.JSONDecodeError as e:
            print(f"Failed to parse extJson: {e}")

        # Generate transaction data based on chain type
        tx_data = generate_transaction_data(chain_info['name'], {
            "from": tool_input.from_addr,
            "to": tool_input.to_addr,
            "amount": tool_input.tx_amount,
            "token_symbol": tool_input.token_symbol,
            "token_address": tool_input.token_address,
            **additional_params
        })

        # Verify signature if provided
        signature = additional_params.get("signature")
        if signature:
            is_valid_signature = verify_signature(chain_info['name'], tx_data, signature)
            if not is_valid_signature:
                return {
                    "error_type": "SIGNATURE_ERROR",
                    "error_message": f"Invalid signature for {chain_info['name']} transaction"
                }

        # Simulate broadcasting transaction
        tx_hash = broadcast_transaction(chain_info['name'], tx_data, signature)

        return {
            "sign_data": signature or (chain_info['signature_prefix'] + "..."),
            "tx_hash": tx_hash,
            "gas_estimation": f"{get_estimated_gas_fee(chain_info['name'])} {chain_info['native_currency']}",
            "chain": chain_info['name'],
            "status": "success",
            "timestamp": "2025-03-19T00:00:00Z"  # Use current timestamp in real code
        }
    except Exception as e:
        return {
            "error_type": "TX_ERROR",
            "error_message": f"Transaction preparation failed: {str(e)}"
        }


# Helper function to get chain-specific information
def get_chain_info(chain_index: str) -> Dict[str, Any]:
    normalized_chain_id = chain_index.upper()

    chain_map = {
        "1": {"name": "Ethereum", "native_currency": "ETH", "signature_prefix": "0x", "tx_hash_prefix": "0x"},
        "ETH": {"name": "Ethereum", "native_currency": "ETH", "signature_prefix": "0x", "tx_hash_prefix": "0x"},
        "56": {"name": "BSC", "native_currency": "BNB", "signature_prefix": "0x", "tx_hash_prefix": "0x"},
        "BSC": {"name": "BSC", "native_currency": "BNB", "signature_prefix": "0x", "tx_hash_prefix": "0x"},
        "TRON": {"name": "TRON", "native_currency": "TRX", "signature_prefix": "", "tx_hash_prefix": ""},
        "SOL": {"name": "Solana", "native_currency": "SOL", "signature_prefix": "", "tx_hash_prefix": ""},
        "SOLANA": {"name": "Solana", "native_currency": "SOL", "signature_prefix": "", "tx_hash_prefix": ""}
    }

    return chain_map.get(normalized_chain_id, {"name": "Ethereum", "native_currency": "ETH", "signature_prefix": "0x",
                                               "tx_hash_prefix": "0x"})


# Generate transaction data for different chains
def generate_transaction_data(chain: str, details: Dict[str, Any]) -> Dict[str, Any]:
    if chain == "Ethereum":
        return {
            "from": details['from'],
            "to": details['token_address'] or details['to'],
            "value": '0x0' if details['token_address'] else to_hex(details['amount']),
            "data": '0x' if not details['token_address'] else generate_erc20_transfer_data(details['to'],
                                                                                           details['amount']),
            "gas_limit": '0x' + hex(100000)[2:],
            "gas_price": '0x' + hex(5000000000)[2:],
            "chain_id": 1
        }

    if chain == "BSC":
        return {
            "from": details['from'],
            "to": details['token_address'] or details['to'],
            "value": '0x0' if details['token_address'] else to_hex(details['amount']),
            "data": '0x' if not details['token_address'] else generate_erc20_transfer_data(details['to'],
                                                                                           details['amount']),
            "gas_limit": '0x' + hex(100000)[2:],
            "gas_price": '0x' + hex(5000000000)[2:],
            "chain_id": 56
        }

    if chain == "TRON":
        return {
            "owner_address": details['from'],
            "to_address": details['to'],
            "amount": 0 if details['token_address'] else int(details['amount'] or '0'),
            "asset_name": details['token_symbol'],
            "contract_address": details['token_address'],
            "visible": True,
            "permission_id": 0
        }

    if chain == "Solana":
        return {
            "from_pubkey": details['from'],
            "to_pubkey": details['to'],
            "lamports": 0 if details['token_address'] else convert_to_lamports(details['amount'] or '0'),
            "mint": details['token_address'],
            "recent_blockhash": details.get('recent_blockhash', 'simulated-blockhash'),
            "program_id": details['token_address'] or '11111111111111111111111111111111'
        }

    return {
        "from": details['from'],
        "to": details['to'],
        "amount": details['amount'],
        "token": details['token_symbol'],
        "token_address": details['token_address']
    }


# Verify signature for different chains
def verify_signature(chain: str, tx_data: Dict[str, Any], signature: str) -> bool:
    print(f"Verifying {chain} signature for transaction...")
    return True


# Broadcast transaction to different chains
def broadcast_transaction(chain: str, tx_data: Dict[str, Any], signature: str = None) -> str:
    print(f"Broadcasting transaction to {chain}...")
    prefixes = {"Ethereum": "0x", "BSC": "0x", "TRON": "", "Solana": ""}
    prefix = prefixes.get(chain, "0x")
    random_hash = ''.join([random.choice('0123456789abcdef') for _ in range(64)])
    return f"{prefix}{random_hash}"


# Convert amount to hex for EVM chains
def to_hex(value: str) -> str:
    try:
        if not value:
            return '0x0'
        return '0x' + hex(int(float(value) * 1e18))[2:]
    except Exception:
        return '0x0'


# Generate ERC20 transfer data
def generate_erc20_transfer_data(to: str, amount: str) -> str:
    transfer_fn_signature = '0xa9059cbb'
    padded_addr = to[2:].rjust(64, '0') if to.startswith('0x') else to.rjust(64, '0')
    amount_in_wei = hex(int(float(amount) * 1e18))[2:].rjust(64, '0')
    return f"{transfer_fn_signature}{padded_addr}{amount_in_wei}"


# Convert amount to lamports (Solana's smallest unit)
def convert_to_lamports(amount: str) -> int:
    try:
        return int(float(amount) * 1e9)
    except Exception:
        return 0


# Helper to get estimated gas fee for the chain
def get_estimated_gas_fee(chain: str) -> str:
    gas_estimates = {
        "Ethereum": "0.002",
        "BSC": "0.0005",
        "TRON": "5",
        "Solana": "0.000005"
    }
    return gas_estimates.get(chain, "0.001")
