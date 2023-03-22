# Deploying the contract

To deploy the contract:

Install [Foundry](https://github.com/foundry-rs/foundry#installation), then:

```
cd contracts
```

Run the foundry deploy script:

```
forge script script/Deploy.s.sol --fork-url https://eth.bd.evmos.org:8545 --broadcast --private-key 0x000
```

When the script is run you can find the deployed contract address in the output:

```
✅ Hash: 0xdf97ec4fb589fc1f7f669c3fbe38b3b183f6e7df9cd5b9a127472063eeec2191
Contract Address: 0xb940dd85b6a3b5855f5558ac83c3fc1318d49f32
Block: 11815376
Paid: 0.016408108 ETH (713396 gas * 23 gwei)
```

**Now that the contract is deployed, you must fund the contract by sending your desired amount of Wrapped EVMOS (WEVMOS) you want to trade with to the address.**

# Running the bot

Once you have deployed the multihop contract, you can start the bot by running:

```
go build -o backrunner
```

and

```
./backrunner start --config=/path/to/skipper/skipper-go/config --multihop=0xXXX --key=
```

The accepted flags are:

- `--config`: path to `skipper/skipper-go/config` directory (**optional** by default this will be `./config`).
- `--multihop`: address of the deployed Multihop contract.
- `--key`: private key of the wallet that deployed the Multihop contract.

# Withdrawing funds from the contract

In order to withdraw funds from the Multihop contract to the owners wallet, run the following command:

```
go build -o backrunner
```

and

```
./backrunner withdraw --config=/path/to/skipper/skipper-go/config --multihop=0xXXX --key=
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
