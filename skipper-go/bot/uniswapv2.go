package bot

import (
	"fmt"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/holiman/uint256"
	"github.com/shopspring/decimal"
	"github.com/skip-mev/skipper/uniswapv2"
	"github.com/thal0x/bn/u256"
)

func (bot *Bot) HandleUniswapV2Transaction(exchange *uniswapv2.Exchange, targetTX *types.Transaction) {
	start := time.Now()

	defer func() {
		elapsed := time.Since(start)
		fmt.Printf("%s (%s) - %s\n", targetTX.Hash(), exchange.Name, elapsed)
	}()

	data := targetTX.Data()
	if len(data) < 4 {
		return
	}

	method := exchange.GetRouterMethodFromTransactionData(data)

	pendingBalances, err := bot.getPendingBalancesFromUniswapV2Transaction(method, data, exchange, targetTX)
	if err != nil {
		fmt.Printf("(%s - %s) bot.getPendingBalancesFromUniswapV2Transaction err:\n", targetTX.Hash(), method)
		fmt.Println(err)
		return
	}

	if pendingBalances == nil {
		return
	}

	routes := make([]*Route, 0)

	for pairAddress := range pendingBalances {
		pairRoutes, ok := bot.routes[pairAddress]
		if ok {
			routes = append(routes, pairRoutes...)
		}
	}

	quote := bot.FindBestQuote(routes, pendingBalances)

	if quote == nil || u256.IsLessThan(quote.Profit, bot.minProfit) {
		return
	}

	tx, err := bot.createBackrunTransactionFromQuote(quote, targetTX)
	if err != nil {
		fmt.Printf("(%s - %s) bot.createBackrunTransactionFromQuote err:\n", targetTX.Hash(), method)
		fmt.Println(err)
		return
	}

	fProfit := decimal.NewFromBigInt(quote.Profit.ToBig(), -int32(quote.Route.TokenIn().Decimals))
	bid := decimal.NewFromFloat(bot.config.BidPercent).Mul(fProfit).Shift(int32(quote.Route.TokenIn().Decimals)).BigInt().Int64()

	bundleResponse, err := bot.skipClient.CreateAndSendBundle(bid, types.Transactions{targetTX, tx})
	if err != nil {
		fmt.Printf("(%s - %s) bot.skipClient.CreateAndSendBundle err:\n", targetTX.Hash(), method)
		fmt.Println(err)
		return
	}

	fmt.Println("-----")
	fmt.Println("-----")
	fmt.Println("Arbitrage opportunity found:")
	fmt.Println(quote.Route)
	fmt.Printf("Amount In: %v %s\n", decimal.NewFromBigInt(quote.AmountIn.ToBig(), -int32(quote.Route.TokenIn().Decimals)), quote.Route.TokenIn().Symbol)
	fmt.Printf("Amount Out: %v %s\n", decimal.NewFromBigInt(quote.AmountOut.ToBig(), -int32(quote.Route.TokenOut().Decimals)), quote.Route.TokenOut().Symbol)
	fmt.Printf("Profit: %v %s\n", decimal.NewFromBigInt(quote.Profit.ToBig(), -int32(quote.Route.TokenIn().Decimals)), quote.Route.TokenIn().Symbol)
	fmt.Printf("Bid: %v\n", bid)
	fmt.Printf("Bundle Status Code: %d\n", bundleResponse.Code)
	if bundleResponse.Code != 0 {
		fmt.Println(bundleResponse)
	}
	fmt.Printf("Target TX: https://escan.live/tx/%s\n", targetTX.Hash())
	fmt.Println("-----")
	fmt.Println("-----")
}

func (bot *Bot) getPendingBalancesFromUniswapV2Transaction(
	method uniswapv2.RouterMethod,
	data []byte,
	exchange *uniswapv2.Exchange,
	tx *types.Transaction,
) (map[common.Address]map[common.Address]*uint256.Int, error) {
	switch method {
	case uniswapv2.ADD_LIQUIDITY:
		args, err := exchange.ParseAddLiquidityData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterAddLiquidity(args)
	case uniswapv2.SWAP_EXACT_TOKENS_FOR_TOKENS:
		args, err := exchange.ParseSwapExactTokensForTokensData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapExactTokensForTokens(args)
	case uniswapv2.SWAP_TOKENS_FOR_EXACT_TOKENS:
		args, err := exchange.ParseSwapTokensForExactTokensData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapTokensForExactTokens(args)
	case uniswapv2.SWAP_EXACT_ETH_FOR_TOKENS:
		args, err := exchange.ParseSwapExactETHForTokensData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapExactETHForTokens(u256.FromBig(tx.Value()), args)
	case uniswapv2.SWAP_TOKENS_FOR_EXACT_ETH:
		args, err := exchange.ParseSwapTokensForExactETHData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapTokensForExactETH(args)
	case uniswapv2.SWAP_EXACT_TOKENS_FOR_ETH:
		args, err := exchange.ParseSwapExactTokensForETHData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapExactTokensForETH(args)
	case uniswapv2.SWAP_ETH_FOR_EXACT_TOKENS:
		args, err := exchange.ParseSwapETHForExactTokensData(data)
		if err != nil {
			return nil, err
		}

		return exchange.GetBalancesAfterSwapETHForExactTokens(u256.FromBig(tx.Value()), args)
	default:
		return nil, nil
	}
}
