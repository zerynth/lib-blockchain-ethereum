"""
.. module:: ethereum

********
Ethereum
********

This module allows the creation of transactions and makes it easy to call contracts.

The Ethereum module is very easy to use: ::

    import streams
    from blockchain.ethereum import ethereum

    # prepare a transaction object
    tx = ethereum.Transaction()
    tx.set_value(1,ethereum.FINNEY)
    tx.set_gas_price("0x430e23411")
    tx.set_gas_limit("0x33450")
    tx.set_nonce(0)
    tx.set_receiver("0xde9F276DDff83727fB627D2C0728b5bAeA469373")
    tx.set_chain(ethereum.ROPSTEN)  # Test network

    # sign the transaction with a private key
    tx.sign("0xa5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5")

    # print hex RLP representation
    print(tx.to_rlp(True))

    # print Hashes
    print(tx.hash(False).hexdigest())
    print(tx.hash(True).hexdigest())

    # print full info
    print(tx)



The following constants are defined:

* :samp:`WEI`, minimum transactable unit
* :samp:`KWEI`, 1000 WEI
* :samp:`MWEI`, one million WEI
* :samp:`GWEI`, one billion WEI
* :samp:`SZABO`, 1000 GWEI
* :samp:`FINNEY`, one million GWEI
* :samp:`ETHER`, one billion GWEI
* :samp:`MAIN`, identifier of the main network
* :samp:`ROPSTEN`, identifier of the ropsten network
* :samp:`RINKEBY`, identifier of the rinkeby network
* :samp:`KOVAN`, identifier of the kovan network


    """

from crypto.ecc import ecc as ecc
from crypto.hash import keccak as keccak
from crypto.hash import sha2 as sha2
from bignum import bignum
from blockchain.ethereum import rlp

WEI    = 0
KWEI   = 3
MWEI   = 6
GWEI   = 9
SZABO  = 12
FINNEY = 15
ETHER  = 18

MAIN    = 1
ROPSTEN = 3
RINKEBY = 4
KOVAN = 42

def get_address(pv):
    """
.. function::get_address(pv)

    Given the private key *pv*, return the corresponding Ethereum address
    *pv* can be given in both binary or hex format (starting with 0x)

    """
    if pv.startswith("0x"):
        pv = ecc.hex_to_bin(pv)
    pbb = ecc.derive_public_key(ecc.SECP256K1,pv)
    pb = ecc.bin_to_hex(pbb)
    kk = keccak.Keccak()
    kk.update(pbb)
    dk = kk.hexdigest()
    db = kk.digest()
    addr = dk[-40:].lower()
    return "0x"+addr


def get_checksum_address(addr):
    """
.. function::get_checksum_address(addr)

    Given the the Ethereum address *addr*, return the checksummed address according to `EIP 55<https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md>`_

    """
    if addr.startswith("0x"):
        addr = addr[2:]
    kk = keccak.Keccak()
    kk.update(addr)
    vv = bytes(kk.hexdigest())
    baddr = bytearray(addr)
    for i,b in enumerate(baddr):
        if b>=__ORD('a') and b<=__ORD('f'):
            v = vv[i]
            if v>=__ORD('8'):
                baddr[i]=__ORD('A')+ (b-__ORD('a'))
    return "0x"+str(baddr)


# secp256k1 N
N = "115792089237316195423570985008687907852837564279074904382605163141518161494337"

def _pad32(topad):
    if topad.startswith('0x'):
        topad = topad[2:]
    return '0'*(64-len(topad)) + topad


# _supported_types = ('address', 'uint8', 'uint16', 'uint32')
def _in_uint_range(check_type):
    size = 256 if check_type == "uint" else int(check_type[4:])
    return size > 0 and size <= 256 and size % 8 == 0


def _in_int_range(check_type):
    size = int(check_type[3:])
    return size > 0 and size <= 256 and size % 8 == 0


def _in_bytes_range(check_type):
    size = int(check_type[5:])
    return size > 0 and size <= 32


_supported_types = (
    'address',
    ('uint',_in_uint_range),
    ('int',_in_int_range),
    ('bytes', _in_bytes_range)
)
def supported_type(check_type):
    for _supp_type in _supported_types:
        if (
            type(_supp_type) == PTUPLE and
            check_type.startswith(_supp_type[0]) and
            _supp_type[1](check_type)
        ):
            return True
        elif type(_supp_type) != PTUPLE and check_type == _supp_type:
            return True
    return False

def convert(arg_type, arg):
    if arg_type.startswith('uint'):
        return hex(int(arg))
    elif arg_type.startswith('int'):
        size = int(arg_type[3:])
        return hex(2**size + int(arg)) if arg < 0 else hex(int(arg))
    elif arg_type.startswith('bytes'):
        return ''.join([hex(int(x), prefix='') for x in bytes(arg)])
    else:
        raise UnsupportedError

class Transaction():
    """

=================
Transaction class
=================

.. class:: Transaction(chain=MAIN)

    Creates an instance of a Transaction  on the network id specified by *chain*.

    The resulting Transaction instance is empty and invalid. The following parameters must be at least specified by calling the appropriate setters:

    * receiver address
    * value to transfer
    * gas price
    * gas limit
    * transaction nonce

   Optionally, transaction data and network id can be set.
    """
    def __init__(self,chain=MAIN):
        self .tx = [b'',b'',b'',b'',b'',b'',b'',b'',b'']
        self.set_chain(chain)

    def set_receiver(self,address):
        """
.. method:: set_receiver(address)

        :param address: the receiver address in hex format starting with 0x

        Set the receiver address to *address*

        """
        if address.startswith("0x"):
            address = address[2:]
        self.tx[3] = ecc.hex_to_bin(address)

    def _set_value(self,value,unit,idx):
        bg = bignum.BigNum(value)
        if unit!=WEI:
            bgt = bignum.BigNum("1"+("0"*unit))
            bg.imul(bgt)
            bgt = None
        hh = bg.to_base(16)
        self.tx[idx] = ecc.hex_to_bin(hh)


    def set_value(self,value,unit=WEI):
        """
.. method:: set_value(value,unit=WEI)

        :param value: value to transfer as an hexadecimal string, bytes or integer
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction value.

        """
        self._set_value(value,unit,4)

    def set_gas_price(self,value,unit=WEI):
        """
.. method:: set_gas_price(value, unit=WEI)

        :param value: gas price in hexadecimal format
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction gas price.

        """
        self._set_value(value,unit,1)

    def set_gas_limit(self,value,unit=WEI):
        """
.. method:: set_gas_limt(value, unit=WEI)

        :param value: gas limit in hexadecimal format
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction gas limit.

        """
        self._set_value(value,unit,2)

    def set_nonce(self,value):
        """
.. method:: set_nonce(value)

        :param value: transaction nonce as integer

        Set transaction nonce.

        """
        self.tx[0] = value

    def set_data(self,value):
        """
.. method:: set_data(value)

        :param value: binary representation of transaction data. Can be hexadecimal or bytes.

        Set transaction data to *value*

        """
        if type(value)==PSTRING and value.startswith("0x"):
            value = bignum.BigNum(value)
            value = ecc.hex_to_bin(value.to_base(16))
        self.tx[5] = value

    def set_chain(self,chain):
        """
.. method:: set_chain(chain)

        :param chain: integer representing the network id of the Ethereum network

        Set the network id for the transaction.

        """
        self.chain = chain


    def to_rlp(self,hex=False):
        """
.. method:: to_rlp(hex)

        :param hex: boolean

        Return the `RLP <https://github.com/ethereum/wiki/wiki/RLP>`_ representation of the transaction in biney form. If *hex* is True, the hexadecimal representation is returned.
        """
        rlpt = rlp.encode(self.tx)
        if hex:
            return ecc.bin_to_hex(rlpt)
        else:
            return rlpt

    def __str__(self):
        res = ""
        res+= "Nonce:     "+str(self.tx[0])+"\n"
        res+= "Gas Price: "+ecc.bin_to_hex(self.tx[1])+"\n"
        res+= "Gas Limit: "+ecc.bin_to_hex(self.tx[2])+"\n"
        res+= "Address:   "+ecc.bin_to_hex(self.tx[3])+"\n"
        res+= "Value:     "+ecc.bin_to_hex(self.tx[4])+"\n"
        res+= "Data:      "+ecc.bin_to_hex(self.tx[5])+"\n"
        res+= "V:         "+hex(self.tx[6])+"\n"
        res+= "R:         "+ecc.bin_to_hex(self.tx[7])+"\n"
        res+= "S:         "+ecc.bin_to_hex(self.tx[8])
        return res

    def hash(self,full=True):
        """
.. method:: hash(full=True)

        :param full: boolean

        Return a hash instance (Keccak) of the transaction. To obtain the binary or string hash, call the methods digest/hexdigest on the result.
        If *full* is False, fields v,r,s of the transaction are set to default values as specified in `EIP-155 <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md>`_.

        """
        if not full:
            v = self.tx[6]
            r = self.tx[7]
            s = self.tx[8]
            self.tx[6] = self.chain
            self.tx[7] = b''
            self.tx[8] = b''

        # print(">>",self.to_rlp(True))
        rlpt = self.to_rlp()
        kk = keccak.Keccak()
        kk.update(rlpt)

        if not full:
            self.tx[6] = v
            self.tx[7] = r
            self.tx[8] = s

        return kk

    def sign(self,pv):
        """
.. method:: sign(pv)

        :param pv: private key in hexadecimal or binary format

        Generate a signed transaction according to EIP-155. Once signed, the transaction can be converted to RLP and broadcasted to the Ethereum network.

        """
        #accept hex and bin keys
        if pv.startswith("0x"):
            pv = pv[2:]
            pv = ecc.hex_to_bin(pv)


        #Check here: replay attacks eip https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md
        self.tx[6] = self.chain
        self.tx[7] = b''
        self.tx[8] = b''

        dk = self.hash(False).digest()

        v,rs = ecc.sign(ecc.SECP256K1,dk,pv,deterministic=sha2.SHA2(),recoverable=True)

        s = ecc.bin_to_hex(rs[32:])
        sbg = bignum.BigNum("0x"+s)
        bg2 = bignum.BigNum(2)
        s2bg = sbg.mul(bg2)
        Nbg = bignum.BigNum(N)

        #Check here: https://github.com/ethereum/py_ecc/blob/master/py_ecc/secp256k1/secp256k1.py#L109
        if s2bg.gte(Nbg):
            sn = Nbg.sub(sbg)
            s = sn.to_base(16)
            s = ecc.hex_to_bin(s)
            v = v^1
        else:
            s = rs[32:]


        self.tx[6] = v+self.chain*2+35
        self.tx[7] = rs[0:32]
        self.tx[8] = s


class Contract():
    """
==============
Contract class
==============

.. class:: Contract(rpc, contract_address, key=None, address=None, chain=MAIN)

    Prepare the device to interact with an Ethereum Smart Contract.

    Create an instance of the Contract class to:

        * call contract functions through paid transactions (functions modifying the blockchain)
        * call contract functions through simple, gas-free calls (functions not modifying the blockchain)

    A device can interact with an already created contract placed at address :samp:`contract_address`.

    :samp:`rpc` must be a valid :ref:`RPC <lib.blockchain.ethereum.rpc>` instance.
    :samp:`chain` is the optional network id.

    :samp:`key` and :samp:`address` represent device address and key needed only if paid transactions are executed.

    """
    def __init__(self, rpc, contract_address, key=None, address=None, chain=MAIN):
        self._rpc = rpc
        self._address = contract_address
        self._functions = {}
        self._key = key
        self._chain = chain

        self._from = address

    def register_function(self, function, gas_price=None, gas_limit=None, args_type=()):
        """
.. method:: register_function(function, gas_price=None, gas_limit=None, args_type=())

        :param function: function name
        :param gas_price: gas price for function execution, can be None, an tuple (value, unit) or a single integer value which will be considered in WEI unit
        :param gas_limit: gas limit for function execution, can be None, an tuple (value, unit) or a single integer value which will be considered in WEI unit
        :param args_type: a tuple specifying function arguments' type following `Ethereum ABI <https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI>`_, at the moment only a subset of possible types is supported: :code:`address`, :code:`uint<M>` where :code:`0 < M < 256 and M % 8 == 0`

        Register a contract function to be called.

        """
        args = []
        fsign = function + '('

        if len(args_type) == 0:
            fsign += ')'
        else:
            for i, arg_type in enumerate(args_type):
                # if arg_type not in _supported_types:
                if not supported_type(arg_type):
                    raise UnsupportedError
                args.append(arg_type)
                cc = (')' if i == len(args_type)-1 else ',')
                fsign += (arg_type + cc)

        kk = keccak.Keccak()
        kk.update(fsign)
        mth = '0x' + (kk.hexdigest()[:8]).lower()

        self._functions[function] = (mth, gas_price, gas_limit, args)

    def _build_transaction(self, function, nonce, value, args):
        fparam = self._functions[function]
        data = fparam[0]

        for i, arg in enumerate(args):
            if type(arg)==PSTRING and arg.startswith("0x"):
                data += _pad32(arg)
            else:
                registered_type = fparam[3][i]
                data += _pad32(convert(registered_type, arg))

        # full transaction or call "transaction"
        if nonce is not None:
            tx = Transaction()

            if value:
                tx.set_value(value[0],value[1])

            unit = WEI
            price = fparam[1]
            if type(price) == PTUPLE:
                unit = price[1]
                price = str(price[0])
            tx.set_gas_price(price, unit)

            unit = WEI
            limit = fparam[2]
            if type(limit) == PTUPLE:
                unit = limit[1]
                limit = str(limit[0])
            tx.set_gas_limit(limit, unit)

            tx.set_nonce(nonce)
            tx.set_receiver(self._address)
            tx.set_chain(self._chain)

            tx.set_data(data)
            tx.sign(self._key)

            tx = tx.to_rlp(True)
        else:
            tx = {}
            tx['to'] = self._address
            tx['from'] = self._from
            tx['data'] = data

        return tx

    def tx(self, function, nonce, value, args=()):
        """
.. method:: tx(function, nonce, value, args=())

        :param function: function to call
        :param nonce: transaction nonce as integer (can be obtained calling :ref:`rpc.getTransactionCount <lib.blockchain.ethereum.rpc.getTransactionCount>`)
        :param value: transaction value as a tuple (value,unit) or None
        :param args: call arguments as a tuple

        Call a previously registered function modifying the blockchain.

        """
        return self._rpc.sendTransaction(self._build_transaction(function, nonce, value, args))

    def call(self, function, args=(), rv=None):
        """
.. method:: call(function, args=(), rv=None)

        :param function: function to call
        :param args: call arguments as a tuple
        :param rv: return value: a tuple containing the number of expected bits and :samp:`str` or :samp:`int` to have respectively an hex string as the call return value or an integer obtained converting returned hex to decimal (e.g. :samp:`(160, str)` for a call returning an address)

        Call a previously registered function not modifying the blockchain.

        """
        res = self._rpc.simpleCall(self._build_transaction(function, None, None, args))
        if rv is None:
            return res

        toconv = res[-(rv[0]//8)*2:]
        if rv[1] == str:
            return '0x' + toconv
        if rv[1] == int:
            return int(toconv, 16)
        raise UnsupportedError


