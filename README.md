# BLCKCHN

Blckchn is an open source [Bitcoin](http://bitcoin.org/en/) [block chain](https://en.bitcoin.it/wiki/Block_chain) API/explorer.

It allows you to retrieve a [Blockchain](http://blockchain.info/)-like transactions history for any address.

It relies on the standard **bitcoind** daemon and communicate with JSON RPC.

**Work in progress**: It's still a draft, but under active development.

## Features

- Basic web interface an JSON RPC API
- Monitor transactions on any Bitcoin address
- Query history for any Bitcoin address

## Requirements

- [LevelDB](https://code.google.com/p/leveldb/)/[plyvel](https://github.com/wbolster/plyvel)
- [gevent](http://www.gevent.org/)
- https://github.com/gerold-penz/python-jsonrpc

## Installation

You must first install [LevelDB](https://code.google.com/p/leveldb/).

```console
sudo apt-get install libleveldb1 libleveldb-dev
```

```console
$ pip install bunch
```

## Donation

BTC 1PVvwmhs8rEfUpVYxWdBVk5DyZ15ZJDjPT


## License

Copyright (c) 2013 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

