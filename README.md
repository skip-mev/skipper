# Skip Searchers

Example MEV searching bots for the Cosmos ecosystem, using Skip.

``` python
"""
||====================================================================||
||//$\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//$\\||
||(100)==================|  SKIP MONEY PRINTER  |================(100)||
||\\$//        ~         '------========--------'                \\$//||
||<< /        /$\              // ____ \\                         \ >>||
||>>|  12    //L\\            // ///..) \\         L38036133B   12 |<<||
||<<|        \\ //           || <||  >\  ||                        |>>||
||>>|         \$/            ||  $$ --/  ||        One Hundred     |<<||
||<<|      L38036133B        *\\  |\_/  //* series                 |>>||
||>>|  12                     *\\/___\_//*   1989                  |<<||
||<<\      Treasurer     ______/MEV BOTS\________     Secretary 12 />>||
||//$\                 ~| TO SKIP OR NOT TO SKIP |~               /$\\||
||(100)===================  BRRRRRRRRRRRRRRRRRR =================(100)||
||\\$//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\$//||
||====================================================================||
"""
```

# Overview

This repository contains example MEV bots that search for and executes on
profitable MEV opportunities throughout the Interchain, starting with Juno.

Each subdirectory corresponds to a different bot. The README in each subdirectory 
contains more information about the bot and a quickstart guide for using it. 

* If you're new to MEV or searching, use this repo as an educational tool to 
help you learn the what and how of searching. 

* If you're already an experienced searcher, use this repo as an example on how 
to easily sign and send bundles to Skip on our supported chains. 

For more searcher documentation, please see: https://skip-protocol.notion.site/Skip-Searcher-Documentation-0af486e8dccb4081bdb0451fe9538c99

For an overview of Skip, please see: https://woolen-background-b64.notion.site/Skip-What-it-is-How-it-Works-af39cd3eb5334920b41b16cf65665601

# About our bots

* `juno-arb`: A Python bot for JUNO that captures cyclic arbitrage opportunities across
JUNO's two major DEXes--JunoSwap and Loop DEX--by backrunning transactions 
that trade against particular pools. You can read more about JUNO, Loop DEX, and JunoSwap 
in our [state of JUNO MEV report](https://medium.com/@skip_protocol/skips-state-of-mev-juno-667a51a17b70)


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

Then, edit the global variables in the main.py file to 
your liking. The most important being your mnemonic.
```python
MNEMONIC = "<your mnemonic>"
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