from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountLines
from xrpl.wallet import Wallet

import xrpl
from xrpl.models.requests import AccountTx
from decimal import Decimal
import nest_asyncio
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountLines
from xrpl.wallet import Wallet
import xrpl
from xrpl.models.requests import AccountTx
from decimal import Decimal
import nest_asyncio
import datetime
import requests
import json
import time
import concurrent.futures
import os
import csv
from decimal import Decimal
import datetime
from utils import process_address

nest_asyncio.apply()

address = "rnQUEEg8yyjrwk9FhyXpKavHyCRJM9BDMW" # Address that issues PFT

# Prepare the request to fetch trust lines
account_lines_request = AccountLines(
    account=address,
    ledger_index="validated"
)

# Send the request
client = JsonRpcClient("https://s1.ripple.com:51234/")
response = client.request(account_lines_request)
trust_lines = response.result.get("lines", [])
# Initialize a list to store addresses holding PFT
pft_holders = []

# Iterate through trust lines to find those with the PFT currency
for line in trust_lines:
    if line["currency"] == 'PFT':
        pft_holders.append(line["account"])

print(f'First 5 of {len(pft_holders)} PFT addresses: ', pft_holders[:5]) # Print the first 5 addresses and say how many addresses we have

nsize = len(pft_holders) # Number of PFT addresses

start_time = time.time() # Start the timer
lim = 350 # this will take a while. Change it to 2 (or something small) for testing

# Multithreading here to be time efficient
with concurrent.futures.ThreadPoolExecutor() as executor: 
    futures = [executor.submit(process_address, address, lim) for address in pft_holders] # Process each address in parallel
    concurrent.futures.wait(futures) # Wait for all threads to finish

end_time = time.time() # End the timer
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds for a max of {lim} transactions per address. There were {nsize} PFT addresses")
average_time = elapsed_time / lim
print(f"Average time per transaction: {average_time} seconds")