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


    
.. function::get_address(pv)

    Given the private key *pv*, return the corresponding Ethereum address
    *pv* can be given in both binary or hex format (starting with 0x)

    
.. function::get_checksum_address(addr)

    Given the the Ethereum address *addr*, return the checksummed address according to `EIP 55<https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md>`_

    
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
    
.. method:: set_receiver(address)

        :param address: the receiver address in hex format starting with 0x

        Set the receiver address to *address*

        
.. method:: set_value(value,unit=WEI)

        :param value: value to transfer as an hexadecimal string, bytes or integer
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction value.

        
.. method:: set_gas_price(value, unit=WEI)

        :param value: gas price in hexadecimal format
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction gas price.

        
.. method:: set_gas_limt(value, unit=WEI)

        :param value: gas limit in hexadecimal format
        :param unit: a unit constant, default WEI

        Convert *value* to big number format according to *unit* and set the resulting big number as the transaction gas limit.

        
.. method:: set_nonce(value)

        :param value: transaction nonce as integer

        Set transaction nonce.

        
.. method:: set_data(value)

        :param value: binary representation of transaction data. Can be hexadecimal or bytes.

        Set transaction data to *value*

        
.. method:: set_chain(chain)

        :param chain: integer representing the network id of the Ethereum network

        Set the network id for the transaction.

        
.. method:: to_rlp(hex)

        :param hex: boolean

        Return the `RLP <https://github.com/ethereum/wiki/wiki/RLP>`_ representation of the transaction in biney form. If *hex* is True, the hexadecimal representation is returned.
        
.. method:: hash(full=True)

        :param full: boolean

        Return a hash instance (Keccak) of the transaction. To obtain the binary or string hash, call the methods digest/hexdigest on the result.
        If *full* is False, fields v,r,s of the transaction are set to default values as specified in `EIP-155 <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-155.md>`_.

        
.. method:: sign(pv)

        :param pv: private key in hexadecimal or binary format

        Generate a signed transaction according to EIP-155. Once signed, the transaction can be converted to RLP and broadcasted to the Ethereum network.

        
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

    
.. method:: register_function(function, gas_price=None, gas_limit=None, args_type=())

        :param function: function name
        :param gas_price: gas price for function execution, can be None, an tuple (value, unit) or a single integer value which will be considered in WEI unit
        :param gas_limit: gas limit for function execution, can be None, an tuple (value, unit) or a single integer value which will be considered in WEI unit
        :param args_type: a tuple specifying function arguments' type following `Ethereum ABI <https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI>`_, at the moment only a subset of possible types is supported: :code:`address`, :code:`uint<M>` where :code:`0 < M < 256 and M % 8 == 0`

        Register a contract function to be called.

        
.. method:: tx(function, nonce, value, args=())

        :param function: function to call
        :param nonce: transaction nonce as integer (can be obtained calling :ref:`rpc.getTransactionCount <lib.blockchain.ethereum.rpc.getTransactionCount>`)
        :param value: transaction value as a tuple (value,unit) or None
        :param args: call arguments as a tuple

        Call a previously registered function modifying the blockchain.

        
.. method:: call(function, args=(), rv=None)

        :param function: function to call
        :param args: call arguments as a tuple
        :param rv: return value: a tuple containing the number of expected bits and :samp:`str` or :samp:`int` to have respectively an hex string as the call return value or an integer obtained converting returned hex to decimal (e.g. :samp:`(160, str)` for a call returning an address)

        Call a previously registered function not modifying the blockchain.

        
