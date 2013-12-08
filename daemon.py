# coding: utf-8
from collections import defaultdict
from urllib2 import HTTPError
import time
import os

import pyjsonrpc
import logging
from structlog import get_logger

logging.basicConfig(level=logging.INFO)
log = get_logger()

http_client = pyjsonrpc.HttpClient(
    url='http://localhost:7334/',
    username='thomas',
    password=os.environ.get('BITCOIND_PASSWORD')
)

GENESIS_TX = '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'


def get_block(block_height):
    """ Return the list of transactions (Tx) for the given block height. """
    if block_height > http_client.getblockcount():
        return None

    txlist = []

    b = http_client.getblockhash(block_height)
    blkdata = http_client.getblock(b)

    for tx in blkdata['tx']:
        try:
            if tx == GENESIS_TX:
                # Hard coded the first tx of the genesis block
                # because it's not available with bitcoind RPC API
                txlist.append({'txid': tx,
                               'in': [],
                               'out': [{'addr': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                                        'value': 5000000000}]})
                continue
            txdata = http_client.getrawtransaction(tx, 1)
            if txdata:
                txouts = []
                txins = []
                for _in in txdata['vin']:
                    if 'txid' in _in:
                        txins.append({'txid': _in['txid'],
                                      'vout': _in['vout']})
                    # TODO handle coinbase
                for out in txdata['vout']:
                    if out['scriptPubKey']['type'] == 'pubkeyhash' or out['scriptPubKey']['type'] == 'pubkey':
                        txouts.append({'addr': out['scriptPubKey']['addresses'][0],
                                       'value': int(out['value']*1e8)})
                txlist.append({'txid': tx,
                               'out': txouts,
                               'in': txins})
        except Exception, exc:
            log.exception(exc)

    return {'block_index': block_height,
            'block_time': blkdata['time'],
            'tx': txlist}

import plyvel

log.info('Starting...')

db = plyvel.DB('/box/blkchn_plgrnd_v10', create_if_missing=True)

log.info('DB Loaded')

#0 => 185044 => 1:38am to 2:20pm => roughly 13hours
block = int(db.get('last-height', 0))
log = log.bind(block=block)
log.info('Starting loop')

while 1:
    log.info('Processing new block')
    b = get_block(block)
    if not b:
        time.sleep(10)
        continue
    # Enumerate over all the TXs
    for tx in b['tx']:
        log = log.bind(block=block, tx=tx['txid'])
        log.info('Processing TX')
        with db.write_batch(transaction=True) as wb:
            # Store block time and height for the given TX
            wb.put('tx-time!{}'.format(tx['txid']), str(b['block_time']))
            wb.put('tx-block!{}'.format(tx['txid']), str(block))

        # Start by TXOs, in case a TXI is also TXO, we must process out first
        for txindex, _in in enumerate(tx['out']):
            # We map each TXO id + index to its address
            db.put('txo-addr!{}!{}'.format(tx['txid'], txindex), str(_in['addr']))
            with db.write_batch(transaction=True) as wb:
                wb.put('{}-txo!{}!{}'.format(_in['addr'], tx['txid'], txindex), str(_in['value']))
                # Set this TXO id + index unspent (once the txo is spent,
                # we update this value with the block height of the TX that spent it)
                # {}-txo-s => {}-txo-spent
                wb.put('{}-txo-spent!{}!{}'.format(_in['addr'], tx['txid'], txindex), '0')

        # Next we iterate TXIs
        for txinindex, txin in enumerate(tx['in']):
            # We fetch the previously set corresponding addr for the TXO id + index pointer
            txin_addr = db.get('txo-addr!{}!{}'.format(txin['txid'], txin['vout']))
            if txin_addr:
                with db.write_batch(transaction=True) as wb:
                    # We need to store some infos about TXIs for each TXOs, so we iterate them for each TXI
                    for out_index, txo in enumerate(tx['out']):
                        out_addr = txo['addr']
                        wb.put('{}-txo-in!{}!{}!{}'.format(out_addr, tx['txid'], out_index, txinindex), str(txin_addr))
                        wb.put('{}-txo-in-txid!{}!{}!{}'.format(out_addr, tx['txid'], out_index, txinindex), str(txin['txid']))
                        wb.put('{}-txo-in-vout!{}!{}!{}'.format(out_addr, tx['txid'], out_index, txinindex), str(txin['vout']))
                        # Store IN records to see where TXOs are spent
                        # pointer: {out addr}-txo!{txid}!{out index} => value
                        wb.put('{}-txi!{}!{}'.format(txin_addr, tx['txid'], out_index), str(out_addr))
                    # Store at which block height the tx is spent
                    wb.put('{}-txo-spent!{}!{}'.format(txin_addr, txin['txid'], txin['vout']), str(block))

        db.put('last-height', str(block))
        block += 1
        log = log.bind(block=block, tx=tx['txid'])
