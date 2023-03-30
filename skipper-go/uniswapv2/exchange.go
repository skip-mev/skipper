package uniswapv2

import (
	"strings"

	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/holiman/uint256"
	"github.com/skip-mev/skipper/bindings"
	"github.com/skip-mev/skipper/erc20"
)

type Exchange struct {
	Factory        *bindings.UniswapV2Factory
	FactoryAddress common.Address
	Fee            *uint256.Int
	FeeBase        *uint256.Int
	Name           string
	PairCache      *PairCache
	Router         *bindings.UniswapV2Router
	RouterABI      abi.ABI
	RouterAddress  common.Address
	WETH           common.Address

	client     *ethclient.Client
	tokenCache *erc20.TokenCache
}

func NewExchange(
	name string,
	routerAddress common.Address,
	factoryAddress common.Address,
	fee *uint256.Int,
	feeBase *uint256.Int,
	tokenCache *erc20.TokenCache,
	client *ethclient.Client,
) (*Exchange, error) {
	factory, err := bindings.NewUniswapV2Factory(factoryAddress, client)
	if err != nil {
		return nil, err
	}

	router, err := bindings.NewUniswapV2Router(routerAddress, client)
	if err != nil {
		return nil, err
	}

	routerABI, err := abi.JSON(strings.NewReader(bindings.UniswapV2RouterABI))
	if err != nil {
		return nil, err
	}

	weth, err := router.WETH(nil)
	if err != nil {
		weth = common.HexToAddress("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270")
	}

	exchange := &Exchange{
		Factory:        factory,
		FactoryAddress: factoryAddress,
		Fee:            fee,
		FeeBase:        feeBase,
		Name:           name,
		PairCache:      NewPairCache(),
		Router:         router,
		RouterABI:      routerABI,
		RouterAddress:  routerAddress,
		WETH:           weth,

		client:     client,
		tokenCache: tokenCache,
	}

	return exchange, nil
}
