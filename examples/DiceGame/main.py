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

# Use serial monitor
streams.serial()


def init_wifi():
    # Connect to WiFi network
    net_driver.auto_init()
    print("Connecting to wifi")
    wifi.link(config.WIFI_SSID, wifi.WIFI_WPA2, config.WIFI_PASSWORD)
    print("Connected!")


def send_bet():
    nt = eth.getTransactionCount(config.ADDRESS)
    tx = ethereum.Transaction()
    tx.set_value(config.BET_AMOUNT, ethereum.WEI)
    tx.set_gas_price(config.GAS_PRICE)
    tx.set_gas_limit("0x33450")
    tx.set_nonce(nt)
    tx.set_receiver(config.CONTRACT_ADDRESS)
    tx.set_chain(ethereum.ROPSTEN)
    tx.sign(config.PRIVATE_KEY)
    tx_hash = eth.sendTransaction(tx.to_rlp(True))
    return tx_hash


def print_balance():
    # Get our current balance from the net
    balance = eth.getBalance(config.ADDRESS)
    print("Current balance: ", balance)
    if not balance:
        print(eth.last_error)
        raise Exception


# Main
try:
    init_wifi()

    # Init the RPC node
    eth = rpc.RPC(config.RPC_URL, ssl_ctx=SSL_CTX)

    # Init smart contract object
    game = ethereum.Contract(
        eth,
        config.CONTRACT_ADDRESS,
        config.PRIVATE_KEY,
        config.ADDRESS,
        chain=ethereum.ROPSTEN
    )
    for name in config.CONTRACT_METHODS:
        method = config.CONTRACT_METHODS[name]
        game.register_function(
            name,
            config.GAS_PRICE,
            method["gas_limit"],
            args_type=method["args"]
        )

    # Run the game
    print_balance()
    jackpot = game.call('getJackpot', rv=(256, str))
    print('Current jackpot: %s' % jackpot)
    print('Betting %s Wei...' % config.BET_AMOUNT)
    nonce = eth.getTransactionCount(config.ADDRESS)
    tx_hash = game.tx('bet', nonce, value=(config.BET_AMOUNT, ethereum.WEI))
    print('Your bet has been placed, and the transaction is now being mined.')
    print('Monitor your balance at https://ropsten.etherscan.io/address/%s#internaltx to see if you won!' % config.ADDRESS)
    print('Reset your device to play again.')


except Exception as e:
    print(e)

while True:
    print(".")
    sleep(10000)
