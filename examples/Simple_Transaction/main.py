import streams

# Ethereum modules
from blockchain.ethereum import ethereum
from blockchain.ethereum import rpc

# WiFi drivers
from espressif.esp32net import esp32wifi as net_driver # for ESP-32
# from broadcom.bcm43362 import bcm43362 as net_driver # for Particle Photon
from wireless import wifi

# SSL module for https
import ssl

# Configuration file
import config


# The SSL context is needed to validate https certificates
SSL_CTX = ssl.create_ssl_context(
    cacert=config.CA_CERT,
    options=ssl.CERT_REQUIRED|ssl.SERVER_AUTH
)


try:
    streams.serial()

    # Connect to WiFi network
    net_driver.auto_init()
    print("Connecting to wifi")
    wifi.link(config.WIFI_SSID, wifi.WIFI_WPA2, config.WIFI_PASSWORD)
    print("Connected!")
    print("Asking ethereum...")

    # Init the RPC node
    eth = rpc.RPC(config.RPC_URL, ssl_ctx=SSL_CTX)

    # Get our current balance
    balance = eth.getBalance(config.ADDRESS)
    print("Balance:", balance)
    if not balance:
        print(eth.last_error)
        raise Exception

    # Get network informations
    print("Gas Price:", eth.getGasPrice())
    nt = eth.getTransactionCount(config.ADDRESS)
    print("TCount:", nt)
    print("Chain:", eth.getChainId())

    # Prepare a transaction object
    tx = ethereum.Transaction()
    tx.set_value(config.WEI_AMOUNT, ethereum.WEI)
    tx.set_gas_price("0x430e23411")
    tx.set_gas_limit("0x33450")
    tx.set_nonce(nt)
    tx.set_receiver(config.RECEIVER_ADDRESS)
    tx.set_chain(ethereum.ROPSTEN)

    # Sign the transaction with the private key
    tx.sign(config.PRIVATE_KEY)

    # Print hex RLP representation
    print(tx.to_rlp(True))

    # Print hashes
    print(tx.hash(False).hexdigest())
    print(tx.hash(True).hexdigest())

    # Print full info
    print(tx)

    # Send the transaction
    tx_hash = eth.sendTransaction(tx.to_rlp(True))
    print("SENT!")
    print("Monitor your transaction at:\nhttps://ropsten.etherscan.io/tx/%s" % tx_hash)

except Exception as e:
    print(e)

while True:
    print(".")
    sleep(10000)
