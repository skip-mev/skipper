class Swap:
    def __init__(self, tx, tx_bytes, sender, contract_address, input_token, input_amount):
        self.tx = tx
        self.tx_bytes = tx_bytes
        self.sender = sender
        self.contract_address = contract_address
        self.input_token = input_token
        self.output_token = "Token2" if input_token == "Token1" else "Token1"
        self.input_amount = input_amount


class SingleSwap(Swap):
    def __init__(self, tx, tx_bytes, sender, contract_address, input_token, input_amount, min_output = None):
        Swap.__init__(self, tx, tx_bytes, sender, contract_address, input_token, input_amount)
        self.min_output = min_output


class PassThroughSwap(Swap):
    def __init__(self, tx, tx_bytes, sender, contract_address, input_token, input_amount, output_amm_address, output_min_token_amount):
        Swap.__init__(self, tx, tx_bytes, sender, contract_address, input_token, input_amount)
        self.output_amm_address = output_amm_address
        self.output_min_token_amount = output_min_token_amount
        self.second_pool_output_token = ""