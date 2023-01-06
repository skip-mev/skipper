# Quick Start

This bot requires:

- Python 3.10

Check your python version by entering:

```bash
python3 --version
```

Once you have python 3.10, install all the dependencies:
```bash
pip install -r requirements.txt
```

Copy .env.copy and populate with your mnemonic. **Don't commit this**

```bash
source .env
```

Lastly, run the bot:
```python
python main.py
```

# How the Bot Works

This example bot searches for 3-pool cyclic arbitrage opportunities
on Juno mainnet. A cylic arb route is a collection of pools and corresponding
swaps that result in receiving more of the same asset than was put in. 

An example is as follows:
```bash
Swaps:
Pool 1: A -> B
Pool 2: B -> C
Pool 3: C -> A

Transfers: 100 Token A -> 20 Token B -> 150 Token C -> 120 Token A
```

In particular, this bot reads from a contracts.json file that has contract addresses
of popular pools on JunoSwap and Loop Dex. In addition, for each pool, the file also 
has a list of 3-pool cyclic routes. Using this file, the high level steps are:

1. Continously query rpc node for current mempool txs (unconfirmed Txs)
2. Parse txs in mempool and look for swaps against JunoSwap pools
3. When a swap is found, grab the current reserve amounts for the pools we're tracking
4. Simulate the swap tx and update the reserves for the pools swapped against
5. Check if the swap created a cylic arb in any of our routes of interest
7. If an arb opportunity is created, find the optimal amount to put into the route
8. Check how profitable the cyclic arb would be after gas and bidding costs
9. If it's profitable after costs, then send a bundle to the Skip Auction

# We're Here To Help

If you have any questions, join our discord and ask in the
traders channel! Got our Skipper interns monitoring 24/7.

Discord: https://discord.gg/UgazvFgKef