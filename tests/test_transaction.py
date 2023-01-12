import pytest
import functools

from src.bot import Bot
from src.transaction import Transaction
from src.decoder import Decoder, CosmWasmDecoder 
from src.state import State

"""
@pytest.fixture(scope="session")
def cosmwasm_decoder() -> Decoder:
    return CosmWasmDecoder()


@pytest.fixture(scope="session")
def juno_arb_denom() -> Decoder:
    return "ujuno"


@pytest.fixture(scope="session")
async def juno_state() -> dict:
    state = State()
    await state.set_all_pool_contracts(
                    init_contracts={},
                    querier="",
                    creator="",
                    factory_contracts={},
                    arb_denom="ujuno"
    )


@pytest.fixture(scope="session")
async def bot() -> Bot:
    bot = Bot()
    await bot.init()
    return bot
"""

@pytest.fixture(scope="session")
def juno_backrun_tx_0() -> str:
    tx_0 = 'CrkDCrYDCiQvY29zbXdhc20ud2FzbS52MS5Nc2dFeGVjdXRlQ29udHJhY3QSjQMKK2p1bm8xczllbWtlNjdmOHR0cG44am1obHA3ajcycHFsZDZteTh1c3h5dHMSP2p1bm8xc2c2Y2hta3R1aHlqNGxzcnhycmRmbGVtN2dzbms0ZWp2NnprY2M0ZDN2Y3F1bHpwNTV3c2Y0bDRnbBrLAXsicGFzc190aHJvdWdoX3N3YXAiOnsib3V0cHV0X21pbl90b2tlbiI6IjMxMTM1OTYyMTY3NDYzMjkwIiwiaW5wdXRfdG9rZW4iOiJUb2tlbjIiLCJpbnB1dF90b2tlbl9hbW91bnQiOiI1MzAwMDAwIiwib3V0cHV0X2FtbV9hZGRyZXNzIjoianVubzE5ODU5bTV4OGtnZXB3YWZjM2gwbjM2a3o1NDVuZ2MydmxxbnF4eDdneDN0MmtndXY2ZndzOTNjdTI1In19Kk8KRGliYy9DNENGRjQ2RkQ2REUzNUNBNENGNENFMDMxRTY0M0M4RkRDOUJBNEI5OUFFNTk4RTlCMEVEOThGRTNBMjMxOUY5Egc1MzAwMDAwEmcKUQpGCh8vY29zbW9zLmNyeXB0by5zZWNwMjU2azEuUHViS2V5EiMKIQL29Lq2zbUYMdZe1lMHOH8Q2YeGsqB6iznFKJSF2gIgIBIECgIIARiWBxISCgwKBXVqdW5vEgM0MTIQ+o0ZGkAkme4k+3EPGpTJJgtcuyaXZZzoUHC5WXRpHtKhmQDyM3lZVn7XthaxKBLevxr1Qi8Xuyv+S11c39zhumuvdOc0'
    return tx_0


class TestJunoTransaction:
    """ Tests the Transaction class."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_transaction_6481511():
        """ Tests that the Transaction class can be instantiated."""
        bot = Bot()
        await bot.init()
        
        bot.account_balance, _ = bot.querier.update_account_balance(
                                        client=bot.client,
                                        wallet=bot.wallet,
                                        denom=bot.arb_denom,
                                        network_config=bot.network_config
                                        )
                                        
        print(bot.account_balance)
        
        # Mainnet backran user tx, Juno Block: 6440035
        #tx_0 = 'CrkDCrYDCiQvY29zbXdhc20ud2FzbS52MS5Nc2dFeGVjdXRlQ29udHJhY3QSjQMKK2p1bm8xczllbWtlNjdmOHR0cG44am1obHA3ajcycHFsZDZteTh1c3h5dHMSP2p1bm8xc2c2Y2hta3R1aHlqNGxzcnhycmRmbGVtN2dzbms0ZWp2NnprY2M0ZDN2Y3F1bHpwNTV3c2Y0bDRnbBrLAXsicGFzc190aHJvdWdoX3N3YXAiOnsib3V0cHV0X21pbl90b2tlbiI6IjMxMTM1OTYyMTY3NDYzMjkwIiwiaW5wdXRfdG9rZW4iOiJUb2tlbjIiLCJpbnB1dF90b2tlbl9hbW91bnQiOiI1MzAwMDAwIiwib3V0cHV0X2FtbV9hZGRyZXNzIjoianVubzE5ODU5bTV4OGtnZXB3YWZjM2gwbjM2a3o1NDVuZ2MydmxxbnF4eDdneDN0MmtndXY2ZndzOTNjdTI1In19Kk8KRGliYy9DNENGRjQ2RkQ2REUzNUNBNENGNENFMDMxRTY0M0M4RkRDOUJBNEI5OUFFNTk4RTlCMEVEOThGRTNBMjMxOUY5Egc1MzAwMDAwEmcKUQpGCh8vY29zbW9zLmNyeXB0by5zZWNwMjU2azEuUHViS2V5EiMKIQL29Lq2zbUYMdZe1lMHOH8Q2YeGsqB6iznFKJSF2gIgIBIECgIIARiWBxISCgwKBXVqdW5vEgM0MTIQ+o0ZGkAkme4k+3EPGpTJJgtcuyaXZZzoUHC5WXRpHtKhmQDyM3lZVn7XthaxKBLevxr1Qi8Xuyv+S11c39zhumuvdOc0'
        #height: str = "6440034"
        tx_0 = 'Co0ECpYCCiQvY29zbXdhc20ud2FzbS52MS5Nc2dFeGVjdXRlQ29udHJhY3QS7QEKK2p1bm8xeG03bGF1MHZhczdlbHl4dXl4OWU2cTRwZzB1aDNmd3lkNHF5Z20SP2p1bm8xeTlyZjdxbDZmZndrdjAyaHNnZDR5cnV6MjNwbjR3OTdwNzVlMnNsc25rbTBtbmFtaHp5c3ZxbnhhcRp9eyJpbmNyZWFzZV9hbGxvd2FuY2UiOnsiYW1vdW50IjoiMTM5Njg1NjU4MzQxNCIsInNwZW5kZXIiOiJqdW5vMXhmMzJqczBsYzZ2N3F1eGo1dHd1bmE5N2h3ZmY3ZGhrejZwc3VqYXZ2a25oMnl6dHk1dXE2d3V0OGoifX0K8QEKJC9jb3Ntd2FzbS53YXNtLnYxLk1zZ0V4ZWN1dGVDb250cmFjdBLIAQoranVubzF4bTdsYXUwdmFzN2VseXh1eXg5ZTZxNHBnMHVoM2Z3eWQ0cXlnbRI/anVubzF4ZjMyanMwbGM2djdxdXhqNXR3dW5hOTdod2ZmN2Roa3o2cHN1amF2dmtuaDJ5enR5NXVxNnd1dDhqGlh7InN3YXAiOnsiaW5wdXRfdG9rZW4iOiJUb2tlbjEiLCJpbnB1dF9hbW91bnQiOiIxMzk2ODU2NTgzNDE0IiwibWluX291dHB1dCI6IjM3NTU4MDkyIn19EmcKUQpGCh8vY29zbW9zLmNyeXB0by5zZWNwMjU2azEuUHViS2V5EiMKIQLEaFyo6cN0vZoMxy7d4D88dy0RI8gXMLO2pQfykUAEHxIECgIIARjnExISCgwKBXVqdW5vEgM1MDAQoMIeGkCwGwNvFKzpM+UXuIhi+1T60KEOb4WoAvIwnzS4tNnZsDb0n8KIEZ7NqvPNQ/pAcc5gLdyrF2LYz3Sq6DvuHeu4'
        height: str = "6314039"
        
        update_all_reserves_jobs = [functools.partial(
                                                contract.update_reserves, 
                                                bot.querier,
                                                height
                                                ) 
                                            for contract 
                                            in bot.state.contracts.values()]
        
        #print("Updating reserves for single pool")
        #await update_all_reserves_jobs[0]()
        #print("Finished updating reserves for single pool")
        
        bot.rpc_url = "https://rpc-archive.junonetwork.io/"
        
        print("Updating reserves for historical block")
        await bot.state.update_all(update_all_reserves_jobs)
        print("Finished updating reserves for historical block")
        
        print(bot.state.contracts["juno1wuu8nwr37kmg0njg6p3ag7j4qcm08vs6z9e9j28aendnfnuxmd3sc4yrhm"].__dict__)
        print(bot.state.contracts["juno1dug89d22vtu7v27ee9gg4xq5seu2tu705d6eh3kmvh0uvy7depaqg45qdj"].__dict__)
        print(bot.state.contracts["juno19859m5x8kgepwafc3h0n36kz545ngc2vlqnqxx7gx3t2kguv6fws93cu25"].__dict__)
        
        transaction = Transaction(
                            contracts=bot.state.contracts,
                            tx_str=tx_0,
                            decoder=bot.decoder,
                            arb_denom=bot.arb_denom
                            )
        contracts_copy = bot.state.simulate_transaction(transaction)
        transaction.add_routes(
                        contracts=contracts_copy,
                        arb_denom=bot.arb_denom
                        )
        print(f"Number of swaps: {len(transaction.swaps)}")
        print(f"Number of routes: {len(transaction.routes)}")
        assert transaction.swaps != []
        assert transaction.routes != []
        assert isinstance(transaction, Transaction)
        
        for route in transaction.routes:
            print(f"Route: {route.pools[0].contract_address, route.pools[1].contract_address, route.pools[2].contract_address}")
            print(f"""Route Reserves: {route.pools[0].input_reserves, route.pools[0].output_reserves, 
                                       route.pools[1].input_reserves, route.pools[1].output_reserves, 
                                       route.pools[2].input_reserves, route.pools[2].output_reserves}""")
        
        bundle = bot.build_most_profitable_bundle(
                            transaction=transaction,
                            contracts=contracts_copy,
                            )
        
        print(transaction.routes[0].__dict__)
        
        assert bundle != []

    '''
    @staticmethod    
    @pytest.mark.asyncio
    async def test_transaction_6440035():
        """ Tests that the Transaction class can be instantiated."""
        bot = Bot()
        await bot.init()
        
        bot.account_balance, _ = bot.querier.update_account_balance(
                                        client=bot.client,
                                        wallet=bot.wallet,
                                        denom=bot.arb_denom,
                                        network_config=bot.network_config
                                        )
                                        
        print(bot.account_balance)
        
        # Mainnet backran user tx, Juno Block: 6440035
        tx_1 = 'CvcDCowCCiQvY29zbXdhc20ud2FzbS52MS5Nc2dFeGVjdXRlQ29udHJhY3QS4wEKK2p1bm8xeW1ldWdhcTBldnAwMnYzbWs1cmdhdXV3dTVjODZheTN5dncwdDQSP2p1bm8xZzJnN3VjdXJ1bTY2ZDQyZzhrNXR3azM0eWVnZHE4YzgyODU4Z3owdHEyZmM3NXp5N2toc3NnbmhqbBpzeyJpbmNyZWFzZV9hbGxvd2FuY2UiOnsiYW1vdW50IjoiMTY0Iiwic3BlbmRlciI6Imp1bm8xY3ZqdWM2NnJkZzM0Z3V1Z214cHo2dzU5cnc2Z2hydW41bTMzejNocHZ4NnE2MGY0MGtucWdsaHp6eCJ9fQrlAQokL2Nvc213YXNtLndhc20udjEuTXNnRXhlY3V0ZUNvbnRyYWN0ErwBCitqdW5vMXltZXVnYXEwZXZwMDJ2M21rNXJnYXV1d3U1Yzg2YXkzeXZ3MHQ0Ej9qdW5vMWN2anVjNjZyZGczNGd1dWdteHB6Nnc1OXJ3NmdocnVuNW0zM3ozaHB2eDZxNjBmNDBrbnFnbGh6engaTHsic3dhcCI6eyJpbnB1dF9hbW91bnQiOiIxNjQiLCJpbnB1dF90b2tlbiI6IlRva2VuMiIsIm1pbl9vdXRwdXQiOiIzNTQxNDQifX0SZwpRCkYKHy9jb3Ntb3MuY3J5cHRvLnNlY3AyNTZrMS5QdWJLZXkSIwohA81h8WKZ3dm80EDAbmq1YAptMa74AzofQr6VkZStQ8RlEgQKAgh/GK0CEhIKDAoFdWp1bm8SAzM5MhCK7xcaQG7o/uBGXXsKVDKmya0qp0jn4DiPGti7OCmCQC6bc73QJZsRNqJJ/0tbv7gHt0pE7u+AP3UkfvjHY5LE3Fm/rSQ='
        height: str = "6481510"
        
        update_all_reserves_jobs = [functools.partial(
                                                contract.update_reserves, 
                                                bot.querier,
                                                height
                                                ) 
                                            for contract 
                                            in bot.state.contracts.values()]
        
        #print("Updating reserves for single pool")
        #await update_all_reserves_jobs[0]()
        #print("Finished updating reserves for single pool")
        
        bot.rpc_url = "https://rpc-archive.junonetwork.io/"
        
        print("Updating reserves for historical block")
        await bot.state.update_all(update_all_reserves_jobs)
        print("Finished updating reserves for historical block")
        
        print(bot.state.contracts["juno1cvjuc66rdg34guugmxpz6w59rw6ghrun5m33z3hpvx6q60f40knqglhzzx"].__dict__)
        print(bot.state.contracts["juno180jzqh7vefwuks6eyvf0lkecdl2mp8u08d844245faunja969p3s8w3t3q"].__dict__)
        print(bot.state.contracts["juno1xf32js0lc6v7quxj5twuna97hwff7dhkz6psujavvknh2yzty5uq6wut8j"].__dict__)
        
        
        transaction = Transaction(
                            contracts=bot.state.contracts,
                            tx_str=tx_1,
                            decoder=bot.decoder,
                            arb_denom=bot.arb_denom
                            )
        contracts_copy = bot.state.simulate_transaction(transaction)
        transaction.add_routes(
                        contracts=contracts_copy,
                        arb_denom=bot.arb_denom
                        )
        print(f"Number of swaps: {len(transaction.swaps)}")
        print(f"Number of routes: {len(transaction.routes)}")
        assert transaction.swaps != []
        assert transaction.routes != []
        assert isinstance(transaction, Transaction)
        
        for route in transaction.routes:
            print(f"Route: {route.pools[0].contract_address, route.pools[1].contract_address, route.pools[2].contract_address}")
            print(f"""Route Reserves: {route.pools[0].input_reserves, route.pools[0].output_reserves, 
                                       route.pools[1].input_reserves, route.pools[1].output_reserves, 
                                       route.pools[2].input_reserves, route.pools[2].output_reserves}""")
        
        bundle = bot.build_most_profitable_bundle(
                            transaction=transaction,
                            contracts=contracts_copy,
                            )
        
        assert bundle == []
    '''