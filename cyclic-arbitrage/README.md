# Quick Start

This bot requires:

- Python 3.10

### **Install Python 3.10** ###
```
sudo apt update && sudo apt upgrade -y
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10 python3-pip python3-virtualenv python3.10-distutils 
```

Check your Python 3.10 is functioning:

```
python3.10 --version
```

Create a virtual environment
```
python3.10 -m virtualenv venv
```
Activate virtual Environment, (venv) will show on left-hand side of shell

```
source venv/bin/activate
```

Once you have python 3.10, install all the dependencies:
```
cd cyclic-arbitrage
pip install -r requirements.txt
```

Rename `example_juno.env` i.e. `juno.env` and edit to your liking.
```
cd cyclic-arbitrage
cp envs/example_juno.env envs/juno.env
```
The most important being your mnemonic, creating a new wallet is highly suggested for security, and for this wallet to only be used for this bot, as your mnemonic must be entered. 
```
MNEMONIC = "<your mnemonic>"
```
Also make sure your .env file from the previous command (`juno.env`, or whatever you named it) matches the call back field in `main.py`
```
# Load environment variables
load_dotenv('envs/juno.env')
#load_dotenv('envs/terra.env')
```

Lastly, run the bot:
```python
python main.py
```
To leave the virtual environment use command
```
deactivate
```

# Run bot with docker

### **Install pre-requisites** ###

```
sudo apt update -y && apt upgrade -y && apt autoremove -y
sudo apt install docker.io docker-compose -y
```
Rename `example_juno.env` i.e. `juno.env` and edit to your liking.
```
cd cyclic-arbitrage
cp envs/example_juno.env envs/juno.env
```
"The most important being your mnemonic, creating a new wallet is highly suggested for security, and for this wallet to only be used for this bot, as your mnemonic must be entered." 
```
MNEMONIC = "<your mnemonic>"
```
Also make sure your .env file from the previous command (`juno.env`, or whatever you named it) matches the call back field in `main.py`
```
# Load environment variables
load_dotenv('envs/juno.env')
#load_dotenv('envs/terra.env')
```

Build the docker image
``` 
docker build -t mevbot
```

Run the docker image
```
docker run -d --name mevbot mevbot:latest
```

Shell into container & check logs
```
docker exec -it mevbot cat logs/juno.log
```

Change env variables after image is built
```
docker exec -it mevbot /bin/sh
```
```
cd envs && nano juno.env -> edit to your liking
```
```
exit
```
```
docker restart mevbot
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
