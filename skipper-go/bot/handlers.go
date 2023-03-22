package bot

import (
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"

	"github.com/skip-mev/skipper/uniswapv2"
)

type HandlerFunc func(tx *types.Transaction)

func (bot *Bot) addHandler(address common.Address, handler HandlerFunc) {
	bot.handlers[address] = handler
}

func (bot *Bot) addUniswapV2RouterHandler(
	exchange *uniswapv2.Exchange,
	addHandler func(address common.Address, handler HandlerFunc),
) {
	addHandler(exchange.RouterAddress, func(tx *types.Transaction) {
		bot.HandleUniswapV2Transaction(exchange, tx)
	})
}
