package bot

import (
	"fmt"

	"github.com/skip-mev/skipper/uniswapv2"
	"github.com/thal0x/bn/u256"
)

func (bot *Bot) loadExchanges() error {
	fmt.Println("loading exchanges...")
	for _, exchangeConfig := range bot.config.Exchanges.UniswapV2Exchanges {
		exchange, err := uniswapv2.NewExchange(
			exchangeConfig.Name,
			exchangeConfig.Router,
			exchangeConfig.Factory,
			u256.New(exchangeConfig.Fee),
			u256.New(exchangeConfig.FeeBase),
			bot.tokenCache,
			bot.ethClient,
		)
		if err != nil {
			return err
		}

		err = exchange.LoadAllPairs()
		if err != nil {
			return err
		}

		bot.addUniswapV2RouterHandler(exchange, bot.addHandler)

		bot.uniswapV2Exchanges[exchangeConfig.Router] = exchange

		fmt.Printf("\t loaded %s (%d pairs)\n", exchange.Name, len(exchange.PairCache.All()))
	}

	return nil
}
