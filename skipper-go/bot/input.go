package bot

import (
	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/thal0x/bn/u256"
)

func (bot *Bot) GetOptimalInputAmount(
	route *Route,
	balanceOverrides map[common.Address]map[common.Address]*uint256.Int,
) *uint256.Int {
	Ea, Eb := bot.getEaEb(route, balanceOverrides)

	if u256.IsGreaterThan(Ea, Eb) {
		return u256.ZERO
	}

	s, overflowed := new(uint256.Int).SubOverflow(
		new(uint256.Int).Sqrt(u256.Mul(u256.Mul(u256.Mul(Ea, Eb), u256.New(997)), u256.New(1000))),
		u256.Mul(Ea, u256.New(1000)),
	)

	if overflowed {
		return u256.ZERO
	}

	optimalAmount := u256.DivDown(
		s,
		u256.New(997),
	)

	return optimalAmount
}

func (bot *Bot) getEaEb(
	route *Route,
	balanceOverrides map[common.Address]map[common.Address]*uint256.Int,
) (*uint256.Int, *uint256.Int) {
	tokenIn := route.Path[0].TokenIn()
	tokenOut := route.Path[len(route.Path)-1].TokenOut()

	Ea := u256.ZERO
	Eb := u256.ZERO

	for i, swap := range route.Path {
		pair := swap.Pair

		if i == 0 {
			if tokenIn.Address == swap.Pair.Token0.Address {
				tokenOut = pair.Token1
			} else {
				tokenOut = pair.Token0
			}
		}

		if i == 1 {
			firstSwap := route.Path[0]

			var Ra *uint256.Int
			var Rb *uint256.Int

			firstSwapBalances := firstSwap.Pair.Balances(balanceOverrides)

			Ra = firstSwapBalances[tokenIn.Address]
			Rb = firstSwapBalances[tokenOut.Address]

			var Rb1 *uint256.Int
			var Rc *uint256.Int

			balances := pair.Balances(balanceOverrides)

			Rb1 = balances[pair.Token0.Address]
			Rc = balances[pair.Token1.Address]

			if tokenOut.Address == pair.Token1.Address {
				Rb1, Rc = Rc, Rb1
				tokenOut = pair.Token0
			} else {
				tokenOut = pair.Token1
			}

			b1000Rb1Product := u256.Mul(u256.New(1000), Rb1)
			b997RbProduct := u256.Mul(u256.New(997), Rb)

			sum := u256.Add(
				b1000Rb1Product,
				b997RbProduct,
			)

			Ea = u256.DivDown(
				u256.Mul(u256.Mul(u256.New(1000), Ra), Rb1),
				sum,
			)

			Eb = u256.DivDown(
				u256.Mul(u256.Mul(u256.New(997), Rb), Rc),
				sum,
			)
		}

		if i > 1 {
			Ra := Ea
			Rb := Eb

			var Rb1 *uint256.Int
			var Rc *uint256.Int

			balances := pair.Balances(balanceOverrides)

			Rb1 = balances[pair.Token0.Address]
			Rc = balances[pair.Token1.Address]

			if tokenOut.Address == pair.Token1.Address {
				Rb1, Rc = Rc, Rb1
				tokenOut = pair.Token0
			} else {
				tokenOut = pair.Token1
			}

			b1000Rb1Product := u256.Mul(u256.New(1000), Rb1)
			b997RbProduct := u256.Mul(u256.New(997), Rb)

			sum := u256.Add(
				b1000Rb1Product,
				b997RbProduct,
			)

			Ea = u256.DivDown(
				u256.Mul(u256.Mul(u256.New(1000), Ra), Rb1),
				sum,
			)

			Eb = u256.DivDown(
				u256.Mul(u256.Mul(u256.New(997), Rb), Rc),
				sum,
			)
		}
	}

	return Ea, Eb
}
