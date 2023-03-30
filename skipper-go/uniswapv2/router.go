package uniswapv2

import (
	"bytes"
	"errors"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/thal0x/bn/u256"
)

type RouterMethod int64

const (
	ADD_LIQUIDITY RouterMethod = iota
	SWAP_EXACT_TOKENS_FOR_TOKENS
	SWAP_TOKENS_FOR_EXACT_TOKENS
	SWAP_EXACT_ETH_FOR_TOKENS
	SWAP_TOKENS_FOR_EXACT_ETH
	SWAP_EXACT_TOKENS_FOR_ETH
	SWAP_ETH_FOR_EXACT_TOKENS
	UNKNOWN
)

func (r RouterMethod) String() string {
	if r == ADD_LIQUIDITY {
		return "addLiquidity"
	}

	if r == SWAP_EXACT_TOKENS_FOR_TOKENS {
		return "swapExactTokensForTokens"
	}

	if r == SWAP_TOKENS_FOR_EXACT_TOKENS {
		return "swapTokensForExactTokens"
	}

	if r == SWAP_EXACT_ETH_FOR_TOKENS {
		return "swapExactETHForTokens"
	}

	if r == SWAP_TOKENS_FOR_EXACT_ETH {
		return "swapTokensForExactETH"
	}

	if r == SWAP_EXACT_TOKENS_FOR_ETH {
		return "swapExactTokensForETH"
	}

	if r == SWAP_ETH_FOR_EXACT_TOKENS {
		return "swapETHForExactTokens"
	}

	return "UNKNOWN"
}

func (exchange *Exchange) GetRouterMethodFromTransactionData(data []byte) RouterMethod {
	if bytes.Equal([]byte{232, 227, 55, 0}, data[0:4]) {
		return ADD_LIQUIDITY
	}
	if bytes.Equal([]byte{56, 237, 23, 57}, data[0:4]) {
		return SWAP_EXACT_TOKENS_FOR_TOKENS
	}
	if bytes.Equal([]byte{136, 3, 219, 238}, data[0:4]) {
		return SWAP_TOKENS_FOR_EXACT_TOKENS
	}
	if bytes.Equal([]byte{127, 243, 106, 181}, data[0:4]) {
		return SWAP_EXACT_ETH_FOR_TOKENS
	}
	if bytes.Equal([]byte{74, 37, 217, 74}, data[0:4]) {
		return SWAP_TOKENS_FOR_EXACT_ETH
	}
	if bytes.Equal([]byte{24, 203, 175, 229}, data[0:4]) {
		return SWAP_EXACT_TOKENS_FOR_ETH
	}
	if bytes.Equal([]byte{251, 59, 219, 65}, data[0:4]) {
		return SWAP_ETH_FOR_EXACT_TOKENS
	}
	return UNKNOWN
}

type AddLiquidityArgs struct {
	TokenA         common.Address
	TokenB         common.Address
	AmountADesired *uint256.Int
	AmountBDesired *uint256.Int
	AmountAMin     *uint256.Int
	AmountBMin     *uint256.Int
}

func (exchange *Exchange) ParseAddLiquidityData(data []byte) (*AddLiquidityArgs, error) {
	args := &AddLiquidityArgs{
		TokenA:         common.BytesToAddress(data[16:36]),
		TokenB:         common.BytesToAddress(data[48:68]),
		AmountADesired: new(uint256.Int).SetBytes32(data[68:100]),
		AmountBDesired: new(uint256.Int).SetBytes32(data[100:132]),
		AmountAMin:     new(uint256.Int).SetBytes32(data[132:164]),
		AmountBMin:     new(uint256.Int).SetBytes32(data[164:196]),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterAddLiquidity(args *AddLiquidityArgs) (map[common.Address]map[common.Address]*uint256.Int, error) {
	pair, err := exchange.GetPairByTokens(args.TokenA, args.TokenB)
	if err != nil {
		return nil, err
	}

	balances := pair.Balances(nil)

	var amountA *uint256.Int
	var amountB *uint256.Int

	if u256.IsEqual(balances[pair.Token0.Address], u256.ZERO) && u256.IsEqual(balances[pair.Token1.Address], u256.ZERO) {
		amountA = args.AmountADesired
		amountB = args.AmountBDesired
	} else {
		amountBOptimal, err := exchange.Quote(args.AmountADesired, balances[args.TokenA], balances[args.TokenB])
		if err != nil {
			return nil, err
		}

		if u256.IsLessThanOrEqual(amountBOptimal, args.AmountBDesired) {
			if !u256.IsGreaterThanOrEqual(amountBOptimal, args.AmountBMin) {
				return nil, errors.New("UniswapV2Router: INSUFFICIENT_B_AMOUNT")
			}

			amountA = args.AmountADesired
			amountB = amountBOptimal
		} else {
			amountAOptimal, err := exchange.Quote(args.AmountBDesired, balances[args.TokenB], balances[args.TokenA])
			if err != nil {
				return nil, err
			}

			if !u256.IsLessThanOrEqual(amountAOptimal, args.AmountADesired) {
				return nil, errors.New("assert(amountAOptimal <= amountADesired)")
			}

			if !u256.IsGreaterThanOrEqual(amountAOptimal, args.AmountAMin) {
				return nil, errors.New("UniswapV2Router: INSUFFICIENT_A_AMOUNT")
			}

			amountA = amountAOptimal
			amountB = args.AmountBDesired
		}
	}

	pendingBalances := map[common.Address]map[common.Address]*uint256.Int{
		pair.Address: {
			args.TokenA: u256.Add(balances[args.TokenA], amountA),
			args.TokenB: u256.Add(balances[args.TokenB], amountB),
		},
	}

	return pendingBalances, nil
}

type SwapExactTokensForTokensArgs struct {
	AmountIn     *uint256.Int
	AmountOutMin *uint256.Int
	Path         []common.Address
}

func (exchange *Exchange) ParseSwapExactTokensForTokensData(data []byte) (*SwapExactTokensForTokensArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapExactTokensForTokens"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapExactTokensForTokensArgs{
		AmountIn:     u256.FromBig(inputs[0].(*big.Int)),
		AmountOutMin: u256.FromBig(inputs[1].(*big.Int)),
		Path:         inputs[2].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapExactTokensForTokens(args *SwapExactTokensForTokensArgs) (map[common.Address]map[common.Address]*uint256.Int, error) {
	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amount := args.AmountIn

	for i := 0; i < len(args.Path)-1; i++ {
		tokenIn := args.Path[i]
		tokenOut := args.Path[i+1]

		pair, err := exchange.GetPairByTokens(tokenIn, tokenOut)
		if err != nil {
			return nil, err
		}

		pairBalances := pair.Balances(nil)

		balances[pair.Address] = map[common.Address]*uint256.Int{
			tokenIn: u256.Add(pairBalances[tokenIn], amount),
		}

		amount = exchange.GetAmountOut(amount, pairBalances[tokenIn], pairBalances[tokenOut])

		if i == len(args.Path)-1 && u256.IsGreaterThan(args.AmountOutMin, amount) {
			return nil, errors.New("UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT")
		}

		balances[pair.Address][tokenOut] = u256.Sub(pairBalances[tokenOut], amount)
	}

	return balances, nil
}

type SwapTokensForExactTokensArgs struct {
	AmountOut   *uint256.Int
	AmountInMax *uint256.Int
	Path        []common.Address
}

func (exchange *Exchange) ParseSwapTokensForExactTokensData(data []byte) (*SwapTokensForExactTokensArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapTokensForExactTokens"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapTokensForExactTokensArgs{
		AmountOut:   u256.FromBig(inputs[0].(*big.Int)),
		AmountInMax: u256.FromBig(inputs[1].(*big.Int)),
		Path:        inputs[2].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapTokensForExactTokens(
	args *SwapTokensForExactTokensArgs,
) (map[common.Address]map[common.Address]*uint256.Int, error) {
	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amounts := make([]*uint256.Int, len(args.Path))
	amounts[len(amounts)-1] = args.AmountOut

	for i := len(args.Path) - 1; i > 0; i-- {
		pair, err := exchange.GetPairByTokens(args.Path[i-1], args.Path[i])
		if err != nil {
			return nil, err
		}

		reserves := pair.Balances(nil)

		amountIn := exchange.GetAmountIn(amounts[i], reserves[args.Path[i-1]], reserves[args.Path[i]])
		if err != nil {
			return nil, err
		}

		amounts[i-1] = amountIn

		balances[pair.Address] = map[common.Address]*uint256.Int{
			args.Path[i-1]: u256.Add(reserves[args.Path[i-1]], amounts[i-1]),
			args.Path[i]:   u256.Sub(reserves[args.Path[i]], amounts[i]),
		}
	}

	if u256.IsGreaterThan(amounts[0], args.AmountInMax) {
		return nil, errors.New("UniswapV2Router: EXCESSIVE_INPUT_AMOUNT")
	}

	return balances, nil
}

type SwapExactETHForTokensArgs struct {
	AmountOutMin *uint256.Int
	Path         []common.Address
}

func (exchange *Exchange) ParseSwapExactETHForTokensData(data []byte) (*SwapExactETHForTokensArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapExactETHForTokens"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapExactETHForTokensArgs{
		AmountOutMin: u256.FromBig(inputs[0].(*big.Int)),
		Path:         inputs[1].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapExactETHForTokens(
	ethIn *uint256.Int,
	args *SwapExactETHForTokensArgs,
) (map[common.Address]map[common.Address]*uint256.Int, error) {
	if args.Path[0].String() != exchange.WETH.String() {
		return nil, errors.New("UniswapV2Router: INVALID_PATH")
	}

	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amount := ethIn

	for i := 0; i < len(args.Path)-1; i++ {
		tokenIn := args.Path[i]
		tokenOut := args.Path[i+1]

		pair, err := exchange.GetPairByTokens(tokenIn, tokenOut)
		if err != nil {
			return nil, err
		}

		pairBalances := pair.Balances(nil)

		balances[pair.Address] = map[common.Address]*uint256.Int{
			tokenIn: u256.Add(pairBalances[tokenIn], amount),
		}

		amount = exchange.GetAmountOut(amount, pairBalances[tokenIn], pairBalances[tokenOut])

		if i == len(args.Path)-1 && u256.IsGreaterThan(args.AmountOutMin, amount) {
			return nil, errors.New("UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT")
		}

		balances[pair.Address][tokenOut] = u256.Sub(pairBalances[tokenOut], amount)
	}

	return balances, nil
}

type SwapTokensForExactETHArgs struct {
	AmountOut   *uint256.Int
	AmountInMax *uint256.Int
	Path        []common.Address
}

func (exchange *Exchange) ParseSwapTokensForExactETHData(data []byte) (*SwapTokensForExactETHArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapTokensForExactETH"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapTokensForExactETHArgs{
		AmountOut:   u256.FromBig(inputs[0].(*big.Int)),
		AmountInMax: u256.FromBig(inputs[1].(*big.Int)),
		Path:        inputs[2].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapTokensForExactETH(
	args *SwapTokensForExactETHArgs,
) (map[common.Address]map[common.Address]*uint256.Int, error) {
	if args.Path[len(args.Path)-1].String() != exchange.WETH.String() {
		return nil, errors.New("UniswapV2Router: INVALID_PATH")
	}

	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amounts := make([]*uint256.Int, len(args.Path))
	amounts[len(amounts)-1] = args.AmountOut

	for i := len(args.Path) - 1; i > 0; i-- {
		pair, err := exchange.GetPairByTokens(args.Path[i-1], args.Path[i])
		if err != nil {
			return nil, err
		}

		reserves := pair.Balances(nil)

		amountIn := exchange.GetAmountIn(amounts[i], reserves[args.Path[i-1]], reserves[args.Path[i]])
		if err != nil {
			return nil, err
		}

		amounts[i-1] = amountIn

		balances[pair.Address] = map[common.Address]*uint256.Int{
			args.Path[i-1]: u256.Add(reserves[args.Path[i-1]], amounts[i-1]),
			args.Path[i]:   u256.Sub(reserves[args.Path[i]], amounts[i]),
		}
	}

	if u256.IsGreaterThan(amounts[0], args.AmountInMax) {
		return nil, errors.New("UniswapV2Router: EXCESSIVE_INPUT_AMOUNT")
	}

	return balances, nil
}

type SwapExactTokensForETHArgs struct {
	AmountIn     *uint256.Int
	AmountOutMin *uint256.Int
	Path         []common.Address
}

func (exchange *Exchange) ParseSwapExactTokensForETHData(data []byte) (*SwapExactTokensForETHArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapExactTokensForETH"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapExactTokensForETHArgs{
		AmountIn:     u256.FromBig(inputs[0].(*big.Int)),
		AmountOutMin: u256.FromBig(inputs[1].(*big.Int)),
		Path:         inputs[2].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapExactTokensForETH(
	args *SwapExactTokensForETHArgs,
) (map[common.Address]map[common.Address]*uint256.Int, error) {
	if args.Path[len(args.Path)-1].String() != exchange.WETH.String() {
		return nil, errors.New("UniswapV2Router: INVALID_PATH")
	}

	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amounts, err := exchange.GetAmountsOut(args.AmountIn, args.Path)
	if err != nil {
		return nil, err
	}

	if u256.IsLessThan(amounts[len(amounts)-1], args.AmountOutMin) {
		return nil, errors.New("UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT")
	}

	for i := 0; i < len(args.Path)-1; i++ {
		pair, err := exchange.GetPairByTokens(args.Path[i], args.Path[i+1])
		if err != nil {
			return nil, err
		}

		pairBalances := pair.Balances(nil)

		balances[pair.Address] = map[common.Address]*uint256.Int{
			args.Path[i]:   u256.Add(pairBalances[args.Path[i]], amounts[i]),
			args.Path[i+1]: u256.Sub(pairBalances[args.Path[i+1]], amounts[i+1]),
		}
	}

	return balances, nil
}

type SwapETHForExactTokensArgs struct {
	AmountOut *uint256.Int
	Path      []common.Address
}

func (exchange *Exchange) ParseSwapETHForExactTokensData(data []byte) (*SwapETHForExactTokensArgs, error) {
	inputs, err := exchange.RouterABI.Methods["swapETHForExactTokens"].Inputs.Unpack(data[4:])
	if err != nil {
		return nil, err
	}

	args := &SwapETHForExactTokensArgs{
		AmountOut: u256.FromBig(inputs[0].(*big.Int)),
		Path:      inputs[1].([]common.Address),
	}

	return args, nil
}

func (exchange *Exchange) GetBalancesAfterSwapETHForExactTokens(
	ethIn *uint256.Int,
	args *SwapETHForExactTokensArgs,
) (map[common.Address]map[common.Address]*uint256.Int, error) {

	if len(args.Path) == 0 || args.Path[0].String() != exchange.WETH.String() {
		return nil, errors.New("UniswapV2Router: INVALID_PATH")
	}

	balances := make(map[common.Address]map[common.Address]*uint256.Int)

	amounts, err := exchange.GetAmountsIn(args.AmountOut, args.Path)
	if err != nil {
		return nil, err
	}

	if u256.IsGreaterThan(amounts[0], ethIn) {
		fmt.Println(amounts[0])
		return nil, errors.New("UniswapV2Router: EXCESSIVE_INPUT_AMOUNT")
	}

	for i := len(args.Path) - 1; i > 0; i-- {
		pair, err := exchange.GetPairByTokens(args.Path[i-1], args.Path[i])
		if err != nil {
			return nil, err
		}

		pairBalances := pair.Balances(nil)

		balances[pair.Address] = map[common.Address]*uint256.Int{
			args.Path[i]:   u256.Sub(pairBalances[args.Path[i]], amounts[i]),
			args.Path[i-1]: u256.Add(pairBalances[args.Path[i-1]], amounts[i-1]),
		}
	}

	return balances, nil
}
