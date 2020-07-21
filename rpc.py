"""
.. module:: rpc

===
RPC
===

This module allows calling the JSON-RPC endpoints of a geth node. ::


    from blockchain.ethereum import rpc

    ...

    address = "0x84db76Ea20C2f55F94A87440fBE825fBE5476da1"

    # setup node address
    eth = rpc.RPC("ethereum.zerynth.com:8545")

    # retrieve balance
    print("Balance:",eth.getBalance(address))
    print("Gas Price:",eth.getGasPrice())
    nonce = eth.getTransactionCount(address)
    print("Transaction Count:",nonce)
    print("Chain:",eth.getChainId())



    """

# rpc interface to node
import socket
import requests
from bignum import bignum

bg = bignum.BigNum

class RPC():
    """
.. _lib.blockchain.ethereum.rpc:
=========
RPC class
=========

.. class:: RPC(host)

    Initialize a RPC instance with the geth node at *host*.
    *host* must also contain the port and the protocol (i.e. :samp:`https://mynode.com:8545`)

    """
    def __init__(self,host,additional_params=dict(),ssl_ctx=None):
        self.host = host
        self.net = 0
        self.balance = bg(0)
        self.last_error = ""
        self.additional_params = additional_params
        self.ssl_ctx = ssl_ctx

    def call(self,method,params=(),retry=10):
        """
.. method:: call(method,params=(),retry=10)

    :param method: the endpoint to call
    :param params: the list of parameters for the endpoint
    :param retry: the number of call retries before failing

    Call endpoint *method* with params *params*. Return the :samp:`result` field of the
    endpoint json response or None in case of error. Error reason can be retrieved in :samp:`self.last_error`.

        """
        self.last_error = ""
        js = {
            "jsonrpc":"2.0",
            "method":method,
            "id":1,
            "params":params
        }
        for param in self.additional_params:
            # Join additional parameters to basic ones
            js[param] = self.additional_params[param]

        while True:
            try:
                res = requests.post(self.host,json=js,ctx=self.ssl_ctx)
                if res:
                    rj = res.json()
                    if "error" in rj:
                        self.last_error = rj["error"]["message"]
                        raise Exception
                    elif "result" in rj:
                        return rj["result"]
                    else:
                        self.last_error = rj
                        raise Exception
            except Exception as e:
                retry -= 1
                if self.last_error == "":
                    self.last_error = str(e)
                if not retry:
                    break
        return None

    #parameters as 0x strings
    def getBalance(self,address,block_number="latest"):
        """
.. method:: getBalance(address,block_number="latest")

    :params address: Ethereum address
    :params block_number: the point in the blockchain up to which balance is calculated

    Return the current balance for address *address*. Previous balances can be retrieved by specifying a different *block_number*

        """
        return self.call("eth_getBalance",params=[address,block_number])

    def getGasPrice(self):
        """
.. method:: getGasPrice()

    Return the current gas price estimated by the Ethereum node. Return 0 on error.

        """
        r = self.call("eth_gasPrice")
        if r:
            return bg(r)
        return 0

    def getChainId(self):
        """
.. method:: getChainId()

    Return the Ethereum network id
        """
        r = self.call("net_version")
        if r is not None:
            return str(r)
        return 0

    def getTransactionCount(self,address,block_number="latest"):
        """
.. _lib.blockchain.ethereum.rpc.getTransactionCount:
.. method:: getTransactionCount(address,block_number="latest")

        :param address: Ethereum address
        :param block_number: the point in the blockchain up to which the transaction count is calculated

        Return the current transaction count for address *address*. The returned value can be used as nonce for the next transaction.
        Transaction counts at specific points in time can be retrieved by specifying a different *block_number*.

        """
        r = self.call("eth_getTransactionCount",params=[address,block_number])
        if r:
            return int(r,16)
        return -1

    def sendTransaction(self,tx,retry=10):
        """
.. method:: sendTransaction(tx,retry=10)

        :param tx: the hexadecimal hash of a signed transaction
        :param retry: the number of retries

        Send the raw transaction to the geth node in order to broadcast it to all nodes in the network. If correct, it will be eventually added to a mined block.

        """
        if not tx.startswith("0x"):
            tx="0x"+tx
        return self.call("eth_sendRawTransaction",params=[tx],retry=retry)

    def simpleCall(self, tx, block_number="latest",retry=10):
        """
.. method:: simpleCall(tx,block_number,retry=10)

        :param tx: the hexadecimal hash of a signed transaction
        :param block_number: the point in the blockchain up to which make the call
        :param retry: the number of retries

        Executes a new message call immediately without creating a transaction on the block chain.

        """
        return self.call("eth_call",params=[tx,block_number],retry=retry)

