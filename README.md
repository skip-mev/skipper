# Skipper

Example MEV searching bots for the Cosmos ecosystem, using Skip.

![Skipper](skipper-image.jpeg "Shout out Stable Diffusion")

# Overview

This repository contains example MEV bots that search for and executes on
profitable MEV opportunities throughout the Interchain, starting with Juno, Terra, and Evmos.

* If you're new to MEV or searching, use this repo as an educational tool to 
help you learn the what and how of searching. 

* If you're already an experienced searcher, use this repo as an example on how 
to easily sign and send bundles to Skip on our supported chains. 

For more searcher documentation, please see: https://docs.skip.money/searcher

For an overview of Skip Select, please see: https://docs.skip.money/how-skip-works

# About our bots

There are two bots in the skipper repo, skipper-py and skipper-go:

**skipper-py**: A Python-based bot for CosmWasm-based Cosmos chains that captures cyclic arbitrage opportunities across all major DEXs on Juno and Terra by backrunning transactions that trade against particular pools. You can read more about JUNO, Loop DEX, and JunoSwap in our [state of JUNO MEV report](https://medium.com/@skip_protocol/skips-state-of-mev-juno-667a51a17b70)

**skipper-go**: A Golang-based bot for EVM-based Cosmos chains that captures cyclic arbitrage opportunities across all major DEXs on Evmos (Diffusion, EvmoSwap, Cronus) by backrunning transactions that trade against particular pools. Execution is carried out by an on-chain smart contract written in Solidity (also included in the repo for your own deployment / learning purposes).