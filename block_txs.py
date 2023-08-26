import asyncio
import base64

import aiohttp

from hashlib import sha256

AKASH_REST_URL = 'https://akash-rest.publicnode.com'
REST_BLOCKS_URL = f'{AKASH_REST_URL}/blocks'
REST_TSX_URL = f'{AKASH_REST_URL}/txs'

BLOCK = 11260637


def get_tx_hash(tx: str) -> str:
    """
    Decode base64 transaction to bytes, get sha256 hash and convert to HEX.

    :param tx:
        Transaction in base64 format.
    """
    return sha256(base64.b64decode(tx)).hexdigest()


async def get_block_info(block_height: int) -> dict:
    """
    Get block dictionary at a certain height.

    :param block_height:
        Height of block.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{REST_BLOCKS_URL}/{block_height}') as resp:
            res = await resp.json()

    return res


async def get_block_tx_info(tx_hash: str) -> dict:
    """
    Get info about a certain transaction by hash.

    :param tx_hash:
        Transaction hash in sha256 format.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{REST_TSX_URL}/{tx_hash}') as resp:
            res = await resp.json()

    return res


async def get_all_txs_by_block(block: dict) -> dict | None:
    """
    Get info about all decoded transactions in a certain block.

    :param block:
    :return:
        All Transactions in dictionary with hashes by keys or None if there is no transactions.
    """
    list_encoded_txs = block['block']['data']['txs']
    if not list_encoded_txs:
        return None

    res = {}

    async def add_tx_to_res(tx_base64: str):
        tx_hash = get_tx_hash(tx_base64)
        res[tx_hash] = await get_block_tx_info(tx_hash=tx_hash)

    tasks = []
    for tx in list_encoded_txs:
        tasks.append(asyncio.create_task(add_tx_to_res(tx)))

    await asyncio.gather(*tasks)

    return res


async def main(block: int):
    block_obj = await get_block_info(block_height=block)
    txs = await get_all_txs_by_block(block=block_obj)
    return txs

if __name__ == "__main__":
    print(asyncio.run(main(block=BLOCK)))
