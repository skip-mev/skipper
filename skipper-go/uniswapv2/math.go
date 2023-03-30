package uniswapv2

import (
	"errors"
	"fmt"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/thal0x/bn/u256"
)

func (exchange *Exchange) GetAmountOut(amountIn *uint256.Int, reserveIn *uint256.Int, reserveOut *uint256.Int) *uint256.Int {
	amountInWithFee := u256.Mul(amountIn, u256.Sub(exchange.FeeBase, exchange.Fee))

	numerator := u256.Mul(amountInWithFee, reserveOut)
	denominator := u256.Add(u256.Mul(reserveIn, exchange.FeeBase), amountInWithFee)

	// if u256.IsGreaterThan(amountIn, reserveIn) {
	// fmt.Println("AMOUNT IN GREATER THAN BALANCE IN")
	// }

	amountOut := u256.DivDown(numerator, denominator)

	// if u256.IsGreaterThan(amountOut, reserveOut) {
	// fmt.Println("AMOUNT OUT GREATER THAN BALANCE OUT")
	// }

	return amountOut
}

func (exchange *Exchange) GetAmountIn(amountOut, balanceIn, balanceOut *uint256.Int) *uint256.Int {
	numerator := u256.Mul(u256.Mul(balanceIn, amountOut), exchange.FeeBase)
	denominator := u256.Mul(u256.Sub(balanceOut, amountOut), u256.Sub(exchange.FeeBase, exchange.Fee))

	return u256.Add(u256.DivDown(numerator, denominator), u256.ONE)
}

func (exchange *Exchange) GetAmountsOut(amountIn *uint256.Int, path []common.Address) ([]*uint256.Int, error) {
	amounts := make([]*uint256.Int, len(path))
	amounts[0] = amountIn

	for i := 0; i < len(path)-1; i++ {
		pair, err := exchange.GetPairByTokens(path[i], path[i+1])
		if err != nil {
			return nil, err
		}

		balances := pair.Balances(nil)

		amountOut := exchange.GetAmountOut(amounts[i], balances[path[i]], balances[path[i+1]])

		if u256.IsGreaterThan(amountIn, balances[path[i]]) {
			fmt.Println("AMOUNT IN GREATER THAN BALANCE IN")
		}

		if u256.IsGreaterThan(amountOut, balances[path[i+1]]) {
			fmt.Println("AMOUNT OUT GREATER THAN BALANCE OUT")
		}

		amounts[i+1] = amountOut
	}

	return amounts, nil
}

func (exchange *Exchange) GetAmountsIn(amountOut *uint256.Int, path []common.Address) ([]*uint256.Int, error) {
	amounts := make([]*uint256.Int, len(path))
	amounts[len(path)-1] = amountOut

	for i := len(path) - 1; i > 0; i-- {
		pair, err := exchange.GetPairByTokens(path[i-1], path[i])
		if err != nil {
			return nil, err
		}

		balances := pair.Balances(nil)

		in := exchange.GetAmountIn(amounts[i], balances[path[i-1]], balances[path[i]])

		amounts[i-1] = in
	}

	return amounts, nil
}

func (exchange *Exchange) Quote(amountA *uint256.Int, reserveA *uint256.Int, reserveB *uint256.Int) (*uint256.Int, error) {
	if u256.IsLessThanOrEqual(amountA, u256.ZERO) {
		return nil, errors.New("UniswapV2Library: INSUFFICIENT_AMOUNT")
	}

	if u256.IsLessThanOrEqual(reserveA, u256.ZERO) || u256.IsLessThanOrEqual(reserveB, u256.ZERO) {
		return nil, errors.New("UniswapV2Library: INSUFFICIENT_LIQUIDITY")
	}

	amountB := u256.DivDown(u256.Mul(amountA, reserveB), reserveA)

	return amountB, nil
}
