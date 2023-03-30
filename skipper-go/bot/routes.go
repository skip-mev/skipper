package bot

import (
	"fmt"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/shopspring/decimal"

	"github.com/skip-mev/skipper/erc20"
	"github.com/skip-mev/skipper/uniswapv2"
)

func (bot *Bot) updateRoutes() {
	pairs := make([]*uniswapv2.Pair, 0)

	for _, exchange := range bot.uniswapV2Exchanges {
		exchangePairs := exchange.PairCache.All()

		for _, pair := range exchangePairs {
			liq := bot.GetPairLiquidityUSD(pair)

			if liq.GreaterThan(decimal.NewFromFloat(1)) {
				pairs = append(pairs, pair)
			}
		}
	}

	routes := GetRoutesFromPairs(bot.baseToken, bot.baseToken, 2, 3, pairs)

	bot.routes = groupRoutesByPairAddress(routes)

	fmt.Printf("found %d routes\n", len(routes))
}

type Swap struct {
	Pair        *uniswapv2.Pair
	ZeroToOne   bool
	EncodedData []byte
}

func (swap *Swap) TokenIn() *erc20.Token {
	if swap.ZeroToOne {
		return swap.Pair.Token0
	}

	return swap.Pair.Token1
}

func (swap *Swap) TokenOut() *erc20.Token {
	if swap.ZeroToOne {
		return swap.Pair.Token1
	}

	return swap.Pair.Token0
}

type Route struct {
	Path []*Swap
}

func (r *Route) GetAmountOut(
	amountIn *uint256.Int,
	balanceOverrides map[common.Address]map[common.Address]*uint256.Int,
) *uint256.Int {
	amountOut := amountIn

	for _, swap := range r.Path {
		balances := swap.Pair.Balances(balanceOverrides)

		balanceIn := balances[swap.TokenIn().Address]
		balanceOut := balances[swap.TokenOut().Address]

		// if u256.IsGreaterThan(amountOut, balanceIn) {
		// 	// fmt.Println("ROUTE SWAPPING MORE THAN POOL HAS")
		// 	return u256.ZERO
		// }

		amountOut = swap.Pair.Exchange.GetAmountOut(amountOut, balanceIn, balanceOut)
	}

	return amountOut
}

func (r Route) String() string {
	routeString := ""

	for i, swap := range r.Path {
		if i != 0 {
			routeString += " / "
		}

		routeString += fmt.Sprintf("%s (%s) to %s (%s) on %s", swap.TokenIn().Symbol, swap.TokenIn().Address, swap.TokenOut().Symbol, swap.TokenOut().Address, swap.Pair.Exchange.Name)
	}

	return routeString
}

func (r *Route) TokenIn() *erc20.Token {
	return r.Path[0].TokenIn()
}

func (r *Route) TokenOut() *erc20.Token {
	return r.Path[len(r.Path)-1].TokenOut()
}

func GetRoutesFromPairs(
	tokenIn *erc20.Token,
	tokenOut *erc20.Token,
	minLength int,
	maxLength int,
	pairs []*uniswapv2.Pair,
) []*Route {
	route := Route{
		Path: make([]*Swap, 0),
	}

	routes := make([]*Route, 0)
	routes = getRoutes(tokenIn, tokenOut, minLength, maxLength, pairs, &route, routes)

	return routes
}

func getRoutes(tokenIn *erc20.Token, tokenOut *erc20.Token, minLength int, maxLength int, pairs []*uniswapv2.Pair, route *Route, routes []*Route) []*Route {
	for i, pair := range pairs {
		if len(route.Path) > 0 && route.Path[len(route.Path)-1].Pair.Address == pair.Address {
			continue
		}

		newRoute := Route{
			Path: make([]*Swap, 0),
		}
		newRoute.Path = append(newRoute.Path, route.Path...)

		if pair.Token0.Address != tokenIn.Address && pair.Token1.Address != tokenIn.Address {
			continue
		}

		tempOut := pair.Token0
		zeroToOne := false
		if tokenIn.Address == pair.Token0.Address {
			tempOut = pair.Token1
			zeroToOne = true
		}

		newSwap := Swap{
			Pair:      pair,
			ZeroToOne: zeroToOne,
		}

		newRoute.Path = append(newRoute.Path, &newSwap)

		if tempOut.Address == tokenOut.Address && len(route.Path) >= minLength-1 {
			routes = append(routes, &newRoute)
		}

		if maxLength > 1 && len(pairs) > 1 {
			pairsExcludingThisPair := make([]*uniswapv2.Pair, 0)
			pairsExcludingThisPair = append(pairsExcludingThisPair, pairs[:i]...)
			pairsExcludingThisPair = append(pairsExcludingThisPair, pairs[i+1:]...)

			routes = getRoutes(tempOut, tokenOut, minLength, maxLength-1, pairsExcludingThisPair, &newRoute, routes)
		}
	}
	return routes
}

func groupRoutesByPairAddress(routes []*Route) map[common.Address][]*Route {
	groupedRoutes := make(map[common.Address][]*Route)
	for _, route := range routes {
		for _, swap := range route.Path {
			routeGroup, found := groupedRoutes[swap.Pair.Address]
			if !found {
				routeGroup = make([]*Route, 0)
			}
			groupedRoutes[swap.Pair.Address] = append(routeGroup, route)
		}
	}

	return groupedRoutes
}
