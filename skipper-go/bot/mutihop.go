package bot

import (
	"context"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/skip-mev/skipper/bindings"
	"github.com/thal0x/bn/bigint"
)

func (bot *Bot) createBackrunTransactionFromQuote(quote *Quote, targetTx *types.Transaction) (*types.Transaction, error) {
	hops := make([]bindings.MultihopDexHop, 0)
	for _, swap := range quote.Route.Path {
		hops = append(hops, bindings.MultihopDexHop{
			PairAddress: swap.Pair.Address,
			ZeroToOne:   swap.ZeroToOne,
			Fee:         swap.Pair.Exchange.Fee.ToBig(),
		})
	}

	opts, err := bind.NewKeyedTransactorWithChainID(bot.privateKey, bot.chainID)
	if err != nil {
		return nil, err
	}

	opts.GasLimit = 400000
	opts.NoSend = true
	opts.Signer = func(a common.Address, t *types.Transaction) (*types.Transaction, error) {
		return types.SignTx(t, types.NewLondonSigner(bot.chainID), bot.privateKey)
	}

	if targetTx.Type() == 2 {
		opts.GasFeeCap = targetTx.GasFeeCap()
		opts.GasTipCap = targetTx.GasTipCap()
	} else {
		opts.GasPrice = targetTx.GasPrice()
	}

	nonce, err := bot.ethClient.NonceAt(context.Background(), opts.From, nil)
	if err != nil {
		return nil, err
	}
	opts.Nonce = bigint.New(int64(nonce))

	return bot.multihop.SwapMultihop(opts, quote.Route.TokenIn().Address, quote.AmountIn.ToBig(), hops)
}
