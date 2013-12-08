# coding: utf-8
import plyvel

db = plyvel.DB('/box/___blkchn_plgrnd', create_if_missing=True)


class BitcoinAddress(object):
    def __init__(self, addr):
        self.addr = addr
        self.data = {}

    def _compute_in(self):
        ins = []
        result = 0
        for key, value in db.iterator(start='{0}-txo!'.format(self.addr),
                                      stop='{0}-txo!\xff'.format(self.addr)):
            txid = key.split('!')[-2]
            txindex = key.split('!')[-1]
            #spent = int(db.get('{0}-txo-spent!{1}!{2}'.format(self.addr, txid, txindex)))
            in_data = dict(ins=[], outs=[], result=0, result2=0, txid=txid,
                           block_time=int(db.get('{}-txo-time!{}!{}'.format(self.addr, txid, txindex))),
                           block_height=int(db.get('{}-txo-block!{}!{}'.format(self.addr, txid, txindex))))
            in_data['outs'].append((key.split('!')[0].replace('-txo', ''), int(value)))
            for key2, value2 in db.iterator(start='{0}-txo-in!{1}!'.format(ad, txid), stop='{0}-txo-in!{1}!\xff'.format(ad, txid)):
                in_data['ins'].append(value2)  # value2 => btc address
            in_data['result'] += int(value)
            in_data['result2'] += int(value)
            in_data['ins'] = list(set(in_data['ins']))
            ins.append(in_data)
        return ins

    def _compute_out(self):
        outs = []
        outs_by_txid = {}
        for key, value in db.iterator(start='{0}-txi!'.format(self.addr), stop='{0}-txi!\xff'.format(self.addr)):
            txid = key.split('!')[-2]
            txindex = key.split('!')[-1]
            txval = int(db.get('{0}-txo!{1}!{2}'.format(value, txid, txindex)))
            if not txid in outs_by_txid:
                outs_by_txid[txid] = dict(outs=[], ins=[self.addr], result=0, txid=txid,
                                          block_time=int(db.get('{}-txi-time!{}!{}'.format(key.split('!')[0].replace('-txi', ''), txid, txindex))),
                                          block_height=int(db.get('{}-txi-block!{}!{}'.format(key.split('!')[0].replace('-txi', ''), txid, txindex))))
            outs_by_txid[txid]['outs'].append((key, value, txval))
            outs_by_txid[txid]['result'] -= txval
#            _a = db.get('{}-txi!{}!{}'.format(key.split('!')[0].replace('-txi', ''), txid, txindex))
#            outs_by_txid[txid]['result'] -= int(db.get('{}-txo!{}!{}'.format(_a, txid, txindex)))
        outs = [v for k, v in outs_by_txid.iteritems()]
        return outs

    def history(self):
        res = []
        res.extend(self._compute_out())
        res.extend(self._compute_in())
        return sorted(res, key=lambda x: x['block_height'])

    def getbalance(self, unspent=True):
        #unspent=False to compute total received.

        balance = 0
        for key, value in db.iterator(start='{0}-txo!'.format(self.addr),
                                      stop='{0}-txo!\xff'.format(self.addr)):
            spent = int(db.get('{0}-txo-spent!{1}!{2}'.format(ad, key.split('!')[-2], key.split('!')[-1])))
            if unspent and spent == 0:
                balance += int(value)
            elif not unspent:
                balance += int(value)
        return balance / 1e8

    @classmethod
    def lastheight(cls):
        return int(db.get('last-height'))
