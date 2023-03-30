# Changelog

All notable changes to this project will be documented in this file.

## Alpha Left For Searchers
- n-pool cyclic arbitrage routes, n != 3
- parsing / backrunning dex aggregator txs
- parallelizing bot for faster optimal route choosing
- searching non x*y=k pools
- searching long-tail opportunities
- searching cross-chain opportunities
- searching cex/dex opportunities
- Juno:
    - Support for WYND DEX (juno_contracts.json includes JunoSwap pools pre-migration)

## Work-In-Progress
- EVM/CW Contract Execution (Multi-messages cannot be used for EVM chains)
- EVMOS Support
- Testing Suite
- Batch Tendermint RPC Queries
- Mempool Parsing for DEX Router Txs

## v2 - 2023-01-12
- General
    - Refactored codebase for easier extendability to more chains, protocols, and searching strategies
    - Added support for Terra 2
    - Added support for bids as a percentage of profit (configurable in .env files)
    - Added support to derive pools and routes from factory contracts (hardcoding still necessary for non-factory dexes)
    - Moved all config variables from main.py to .env files in envs/
    - Added a switch in main.py to choose network
- Networks:
    - Terra 2:
        - Added support for Astroport, Phoenix, TerraSwap, and WhiteWhale pools
        - Currently must be run on a local node to avoid rate limiting on public Terra 2 nodes
    - Juno:
        - Added support for parsing Loop and White Whale pool swaps from the mempool
- Cyclic Arbitrage
    - Added support for different fees across pools
    - Added support for pool fees coming out of input and/or output denoms

## v1 - 2022-11-15
- Skipper is born!
- Networks:
    - Juno:
        - Added support for arbing across JunoSwap and Loop pools
        - Added support for parsing JunoSwap swaps from mempool
- MEV Opportunities Supported:
    - 3-Pool Cyclic Arbitrage (single fee across all pools)
        - Optimal Amount In Algo: https://arxiv.org/abs/2105.02784