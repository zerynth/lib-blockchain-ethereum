# Smart contract example

This example shows how to call some smart contract functions, get the return
value, or transfer Ether to a payable function.

In this example the Ropsten test network is used, so no real value is 
actually being transferred, but it acts exactly the same way that it would
be in the real Ethereum network.



## Game rules

This smart contract act as shooter for a virtual 20-faces dice.

A player can ask the shooter to roll the dice paying any amount (with a
minimum 5 Wei) using the `bet` function.

After rolling the dice, if the sum of the number is greater or equal
to 14, the player wins the jackpot. In any case his bet becomes part of the
jackpot itself.

**Note:** the smart contract source code it's included in this example folder.
A live version of the contract can be found on the Ropsten network at this
address: [0xf7a270b24d2859002c0f414b0a0c97e4c794f5cc](https://ropsten.etherscan.io/address/0xf7a270b24d2859002c0f414b0a0c97e4c794f5cc).



## Preparation

### Creating an address and get some Ether in it (MetaMask)

- Install the MetaMask browser extension from https://metamask.io/
- Choose the Ropsten test network from top-right corner (instead of the main
  network)
- Request your first Ether from https://faucet.metamask.io/, since we are
  using the test network, they have no real money value.
- Export and note your Ethereum private key from MetaMask pressing the three
  lines menu button, Details, Export private key (you will be prompted for the
  password you created when you installed MetaMask)


### Registering to a RPC node (Infura)

- In order to interact with the Ethereum blockchain, a RPC node exposing API
  is needed. In this example we'll be using https://infura.io that offer this
  service for free. Register to their website and note your API key (e.g.
  607c53ff4845226fa6c4b060fd1db12d).


### Configuring the example

- Edit the `config.py` file and change your Wi-Fi informations.
- In the same file insert your Ethereum address and private key.
  This is the address that your microcontroller will be using to call the smart
  contract.


## Running the example
- After completing the previous part, you should be able to run the code and
  make your first bet.
- You can use https://ropsten.etherscan.io to real time monitor your address or
  transactions status. After your bet has been mined, check your balance to see
  if you won or just lost some Ether.
