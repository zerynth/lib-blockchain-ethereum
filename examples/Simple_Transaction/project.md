# Simple Transaction

Transfer value from an address to another through an Ethereum transaction.

In this example the Ropsten test network is used, so no real value is 
actually being transferred, but it acts exactly the same way that it would
be in the real Ethereum network.


## Preparation

### Creating an address and get some Ether in it (MetaMask)

- Install the MetaMask browser extension from https://metamask.io/
- Choose the Ropsten test network from top-right corner (instead of the main
  network)
- Request your first Ether from https://faucet.metamask.io/, since we are
  using the test network, they have no real money value.
- Export and note your Ethereum private key from MetaMask pressing the three
  lines menu button, Details, Export private key (you will be promped for the
  password you created when you installed MetaMask)


### Registering to a RPC node (Infura)

- In order to interact with the Ethereum blockchain, a RPC node exposing API
  is needed. In this example we'll be using https://infura.io that offer this
  service for free. Register to their website and note your API key (e.g.
  607c53ff4845226fa6c4b060fd1db12d).


### Configuring the example

- Edit the `config.py` file and change your Wi-Fi informations.
- In the same file insert your Ethereum address and private key.
  This is the address that your microcontroller will be using to send some
  currency.
- You can also customize the receiver address (e.g. you can return some Ether
  to the faucet address that you can copy from https://faucet.metamask.io/)
  and the amount of Wei to be sent (note that 1e18 Wei = 1 Ether).



## Running the example
- After completing the previous part, you should be able to run the code and
  make your first transaction.
- You can use https://ropsten.etherscan.io to real time monitor your address or
  transactions status.
