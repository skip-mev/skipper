package erc20

import (
	"errors"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"

	"github.com/skip-mev/skipper/bindings"
)

var (
	ErrNotFound = errors.New("TOKEN NOT FOUND")
)

type Token struct {
	Address  common.Address
	Decimals uint8
	Name     string
	Symbol   string
}

func NewToken(address common.Address, client *ethclient.Client) (*Token, error) {
	contract, err := bindings.NewERC20(address, client)
	if err != nil {
		return nil, ErrNotFound
	}

	name, err := contract.Name(nil)
	if err != nil {
		return nil, ErrNotFound
	}

	symbol, err := contract.Symbol(nil)
	if err != nil {
		return nil, ErrNotFound
	}

	decimals, err := contract.Decimals(nil)
	if err != nil {
		return nil, ErrNotFound
	}

	token := &Token{
		Address:  address,
		Decimals: decimals,
		Name:     name,
		Symbol:   symbol,
	}

	return token, nil
}
