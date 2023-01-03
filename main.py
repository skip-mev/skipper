import asyncio

from src import Bot, Transaction 

async def main():
    # Create bot with the appropriate settings
    bot: Bot = Bot()
    # Run bot in an infinite loop
    while True:
        # Update the account balance
        bot.querier.update_account_balance(bot=bot) 
        # Query the mempool for new transactions, returns once new txs are found
        backrun_list = bot.querier.query_node_for_new_mempool_txs()
        # Update the reserves of all pools when a new txs are found
        await bot.state.update_all(jobs=bot.state.update_all_reserves_jobs)
        # Iterate through each tx and assess for profitable opportunities
        for tx_str in backrun_list:
            # Create a transaction object
            transaction: Transaction = Transaction(contracts=bot.state.contracts, 
                                                   tx_str=tx_str, 
                                                   decoder=bot.decoder,
                                                   arb_denom=bot.arb_denom)
            # Simulate the transaction on a copy of contract state 
            # and return the copied state post-transaction simulation
            contracts_copy = bot.state.simulate_transaction(transaction=transaction)
            # Build the most profitable bundle from 
            bundle: list = bot.build_most_profitable_bundle(transactions=transaction,
                                                            contracts=contracts_copy)
            # If there is a profitable bundle, fire away!
            if bundle:
                bot.fire(bundle=bundle)

# Printer go brrr
if __name__ == "__main__":
    asyncio.run(main())