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

