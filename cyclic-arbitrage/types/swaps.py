class Swap:
    def __init__(self, contract_address, input_denom, input_amount, output_denom):
        self.contract_address = contract_address
        self.input_denom = input_denom
        self.input_amount = input_amount
        self.output_denom = output_denom


class JunoSwap(Swap):
    def __init__(self, contracts, contract_address, input_amount, input_token, min_output = None):
        self.input_token = input_token
        self.output_token = "Token2" if input_token == "Token1" else "Token1"
        self.min_output = min_output

        if input_token == "Token1":
            self.input_denom = contracts[contract_address]["info"]["token1_denom"]
            self.output_denom = contracts[contract_address]["info"]["token2_denom"]
        else:
            self.input_denom = contracts[contract_address]["info"]["token2_denom"]
            self.output_denom = contracts[contract_address]["info"]["token1_denom"]

        Swap.__init__(self, contract_address, self.input_denom, input_amount, self.output_denom)