# Overview

Skipper-go is a Golang-based bot for EVM-based Cosmos chains that captures cyclic arbitrage opportunities across all major DEXs on Evmos (Diffusion, EvmoSwap, Cronus) by backrunning transactions that trade against particular pools. Execution is carried out by an on-chain smart contract written in Solidity (also included in the repo for your own deployment / learning purposes).

# Basic Setup and Environment

This bot requires golang, follow the directions to install here:
```
https://go.dev/doc/install
```

Check your Golang is functioning:
```
go version
```

Clone the repository:
```
git clone https://github.com/skip-mev/skipper.git
```

Move into the main skipper directory:
```
cd skipper
```

Move into the skipper-go sub-directory:
```
cd skipper-go
```

# Deploying the contract

This bot requires deployment of a Solidity-based smart contract to the chain being searched on. Skipper-go depends on Foundry as our smart contract toolkit for deployment and testing. Follow the installation process here:
```
https://github.com/foundry-rs/foundry#installation
```

Move into the contracts sub-directory within skipper-go:
```
cd contracts
```

The next step is to obtain the private key of the account you'd like to deploy the searching contract from. 
- Note: This account must be able to pay the tx fees for contract creation. The easiest way to obtain a private key is to have a MetaMask wallet and export the private key.

After obtaining your private key, run the foundry deploy script (example below for Evmos, must change the private key value with your own private key):
```
forge script script/Deploy.s.sol --fork-url https://eth.bd.evmos.org:8545 --broadcast --private-key <YOUR PRIVATE KEY HERE>
```

When the script is run you can find the deployed contract address in the output (example output provided below):

```
✅ Hash: 0xdf97ec4fb589fc1f7f669c3fbe38b3b183f6e7df9cd5b9a127472063eeec2191
Contract Address: 0xb940dd85b6a3b5855f5558ac83c3fc1318d49f32
Block: 11815376
Paid: 0.016408108 ETH (713396 gas * 23 gwei)
```

# Converting evmos into wevmos

Now that the contract is deployed, you must fund the contract by sending your desired amount of Wrapped EVMOS (WEVMOS) you want to trade with to the contract address:

First, you can go to: https://app.evmos.org/assets to convert your evmos into wevmos (connect wallet, click on evmos asset, click the wrap button on the evmos dropdown and convert desired amount to wevmos).

Then, add the wevmos token contract to your metamask (click import tokens at the bottom). For reference, here is a mintscan link to the verified contract: https://www.mintscan.io/evmos/evm/contract/0xD4949664cD82660AaE99bEdc034a0deA8A0bd517

Lastly, transfer the amount of wevmos you want to use for arbing to your newly deployed contract.

# Running the bot

Once you have deployed the multihop contract and funded it, you can start the bot by running (from the main directory of the folder):

```
go build -o backrunner
```

and

```
./backrunner start --config=</path/to/skipper-go/config> --multihop=<YOUR CONTRACT ADDRESS HERE> --key=<YOUR PRIVATE KEY HERE>
```

The accepted flags are (ALL MUST BE CHANGED):

- `--config`: path to `skipper-go/config` directory (**optional** by default this will be `./config`).
- `--multihop`: address of the deployed Multihop contract.
- `--key`: private key of the wallet that deployed the Multihop contract.

# Withdrawing funds from the contract

In order to withdraw funds from the Multihop contract to the owners wallet, run the following command:

```
go build -o backrunner
```

and

```
./backrunner withdraw --config=</path/to/skipper-go/config> --multihop=<YOUR CONTRACT ADDRESS HERE> --key=<YOUR PRIVATE KEY HERE>
```

See above for an explanation of the flags.

# Configuration

`config.json`:

|                       | Description                                         | Default                                             |
| --------------------- | --------------------------------------------------- | --------------------------------------------------- |
| base_token            | token all arbitrages start and end with.            | 0xD4949664cD82660AaE99bEdc034a0deA8A0bd517 (WEVMOS) |
| cosmos_rpc            | Cosmos RPC API endpoint                             | https://evmos-rpc.polkachu.com                      |
| cosmos_rest           | Cosmos REST API endpoint                            | https://rest.bd.evmos.org:1317                      |
| eth_rpc               | Ethereum JSON-RPC endpoint                          | wss://eth.bd.evmos.org:8546                         |
| poll_ms               | How often to poll for new pending transactions      | 500                                                 |
| min_profit_wei        | Minimum profit in [wei](https://eth-converter.com/) | 10000000000000000 (0.1)                             |
| skip_sentinal_url     | Skip's EVMOS sentinal URL                           | https://evmos-9001-2-api.skip.money                 |
| auction_house_address | Address to send validator payments to               | evmos17yqtnk08ly94lgz3fzagfu2twsws33z7cpkxa2        |
| bid_percent           | % of profit to bid in the Skip auction              | 0.5 (50%)                                           |

If you'd prefer to use different API endpoints, you can find more [here](https://docs.evmos.org/develop/api/networks) or run your own EVMOS node.
