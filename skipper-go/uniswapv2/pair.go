package uniswapv2

import (
	"errors"
	"fmt"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/thal0x/bn/u256"

	"github.com/skip-mev/skipper/bindings"
	"github.com/skip-mev/skipper/erc20"
)

type Pair struct {
	Address  common.Address
	Exchange *Exchange
	Token0   *erc20.Token
	Token1   *erc20.Token

	balances map[common.Address]*uint256.Int
	contract *bindings.UniswapV2Pair
}

func NewPair(address common.Address, exchange *Exchange) (*Pair, error) {
	contract, err := bindings.NewUniswapV2Pair(address, exchange.client)
	if err != nil {
		return nil, err
	}

	factory, err := contract.Factory(nil)
	if err != nil {
		return nil, err
	}

	if factory != exchange.FactoryAddress {
		return nil, errors.New("pair does not belong to this exchange")
	}

	token0Address, err := contract.Token0(nil)
	if err != nil {
		return nil, err
	}

	token0, err := exchange.tokenCache.Get(token0Address)
	if err != nil {
		return nil, err
	}

	token1Address, err := contract.Token1(nil)
	if err != nil {
		return nil, err
	}

	token1, err := exchange.tokenCache.Get(token1Address)
	if err != nil {
		return nil, err
	}

	pair := &Pair{
		Address:  address,
		Exchange: exchange,
		Token0:   token0,
		Token1:   token1,

		balances: make(map[common.Address]*uint256.Int),
		contract: contract,
	}

	balances, err := pair.balancesFromContract()
	if err != nil {
		return nil, err
	}

	pair.balances = balances

	go pair.watchBalances()

	return pair, nil
}

func (p *Pair) Balances(balanceOverrides map[common.Address]map[common.Address]*uint256.Int) map[common.Address]*uint256.Int {
	if balanceOverrides != nil {
		balances, ok := balanceOverrides[p.Address]
		if ok {
			return balances
		}
	}

	return p.balances
}

func (p *Pair) balancesFromContract() (map[common.Address]*uint256.Int, error) {
	reserves, err := p.contract.GetReserves(nil)
	if err != nil {
		return nil, err
	}

	balances := map[common.Address]*uint256.Int{
		p.Token0.Address: u256.FromBig(reserves.Reserve0),
		p.Token1.Address: u256.FromBig(reserves.Reserve1),
	}

	return balances, nil
}

func (pair *Pair) watchBalances() {
	for {
		balances, err := pair.balancesFromContract()
		if err != nil {
			fmt.Println(err)
			continue
		}

		pair.balances = balances

		time.Sleep(time.Millisecond * 100)
	}
}
