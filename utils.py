from xrpl.models.requests import AccountTx
from decimal import Decimal
import nest_asyncio
import datetime
import requests
import json
import xrpl
import os
import csv

def get_transactions_for_address(address, limit=350):
    """
    Fetches the most recent `limit` transactions for an XRP Ledger account.
    Returns a list of transaction dicts.
    """
    # Connect to a public XRPL node
    client = xrpl.clients.JsonRpcClient("https://s1.ripple.com:51234/")

    # Fetch account transactions
    request = AccountTx(
        account=address,
        ledger_index_min=-1,  # Earliest ledger
        ledger_index_max=-1,  # Latest ledger
        limit=limit
    )
    response = client.request(request)

    if not response.is_successful():
        raise Exception(f"Failed to fetch transactions: {response.result['error_message']}")

    transactions = response.result["transactions"]

    results = []
    for tx_entry in transactions:
      results.append(tx_entry)
    return results

def parse_xrp_transaction(transaction):
    """
    Parses an XRPL transaction to extract relevant details for scoring.
    :param transaction: A single XRPL transaction dictionary.
    :return: A dictionary with parsed transaction details.
    """
    # Extract general transaction details
    tx_json = transaction.get("tx_json", {})
    meta = transaction.get("meta", {})

    transaction_id = transaction.get("hash", "Unknown")
    ledger_index = transaction.get("ledger_index", "Unknown")
    timestamp = transaction.get("close_time_iso", "Unknown")

    # Fee conversion (drops to XRP)
    fee_drops = Decimal(tx_json.get("Fee", 0))
    fee_xrp = fee_drops / Decimal(10**6)

    # Delivered amount
    delivered_amount = meta.get("delivered_amount", {})
    if isinstance(delivered_amount, dict):
        amount = Decimal(delivered_amount.get("value", 0))
        token = delivered_amount.get("currency", "Unknown")
    else:
        # XRP amount (in drops) converted to XRP
        amount = Decimal(delivered_amount) / Decimal(10**6)
        token = "XRP"

    # Sender and recipient
    sender = tx_json.get("Account", "Unknown")
    recipient = tx_json.get("Destination", "Unknown")

    # Extract metadata from memos
    memos = tx_json.get("Memos", [])
    metadata = []
    for memo in memos:
        try:
            memo_data = bytes.fromhex(memo["Memo"]["MemoData"]).decode('utf-8')
            metadata.append(memo_data)
        except (KeyError, ValueError):
            metadata.append("Invalid or missing memo data")

    # Transaction type
    transaction_type = tx_json.get("TransactionType", "Unknown")

    # Return a parsed transaction dictionary
    return {
        "transaction_id": transaction_id,
        "ledger_index": ledger_index,
        "timestamp": timestamp,
        "from": sender,
        "to": recipient,
        "amount": float(amount),
        "token": token,
        "fees": float(fee_xrp),
        "type": transaction_type,
        "metadata": metadata,
        "status": meta.get("TransactionResult", "Unknown"),
    }

def process_address(address, limit):
    transactions = get_transactions_for_address(address, limit=limit)
    responses = []
    file_path = f"scoring_{address}.csv"
    with open(file_path, "a", newline="") as csvfile:
      writer = csv.writer(csvfile)

      # Optionally write headers if the file is new
      if os.stat(file_path).st_size == 0:
        writer.writerow(["Transaction Prompt", "Response"])
      for tx in transactions:
        parsed_transaction = parse_xrp_transaction(tx)
           
           
        response = requests.post(
          url="https://openrouter.ai/api/v1/chat/completions",
          headers={
            "Authorization": f"Bearer <API_KEY>",
          },
          data=json.dumps({
            "model": "openai/gpt-3.5-turbo", # set model as needed. i'm using gpt-3.5-turbo here for its performance given speed.
            "messages": [
                {
                    "role": "system",
                  "content": "Return a dollar value you believe is reasonable for the task followed by the justification. For example, your response can be '200$. This would take about 4 hours for an entry-level developer' where it starts with the cost of $200 and is followed by the justification for why you think it would cost that much. Let's think step by step."
                  #  and justify. The final sentence in your answer should end with the dollar amount. To be clear the absolute last set of characters in your output should be the price, just like the last set of characters in this system prompt is $50"
                },
              {
                "role": "user",
                "content": parsed_transaction['metadata'][0] if parsed_transaction['metadata'] else ""
              }
            ],
            "temperature": 0

          })
        )
        response.raise_for_status()
        response_data = response.json()
        writer.writerow([parsed_transaction['metadata'][0] if parsed_transaction['metadata'] else "", response_data]) # dumping the full response from Openrouter in the csv since there might be useful information in there.

