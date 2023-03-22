package bot

import (
	"sync"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/thal0x/bn/u256"
)

type Quote struct {
	AmountIn  *uint256.Int
	AmountOut *uint256.Int
	Profit    *uint256.Int
	Route     *Route
}

func (bot *Bot) FindBestQuote(routes []*Route, balanceOverrides map[common.Address]map[common.Address]*uint256.Int) *Quote {
	var bestQuote *Quote

	var wg sync.WaitGroup
	mu := sync.Mutex{}

	for _, route := range routes {
		wg.Add(1)

		go func(route *Route) {
			defer wg.Done()

			amountIn := bot.GetOptimalInputAmount(route, balanceOverrides)
			if u256.IsEqual(amountIn, u256.ZERO) {
				return
			}

			if u256.IsGreaterThan(amountIn, bot.multihopBalance) {
				amountIn = bot.multihopBalance
			}

			amountOut := route.GetAmountOut(amountIn, balanceOverrides)

			if u256.IsGreaterThan(amountOut, amountIn) {
				profit := u256.Sub(amountOut, amountIn)
				mu.Lock()
				if bestQuote == nil || u256.IsGreaterThan(profit, bestQuote.Profit) {
					bestQuote = &Quote{
						AmountIn:  amountIn,
						AmountOut: amountOut,
						Profit:    profit,
						Route:     route,
					}
				}
				mu.Unlock()
			}

		}(route)
	}

	wg.Wait()

	return bestQuote
}
