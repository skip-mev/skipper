package bot

import (
	"fmt"
	"sync"

	"github.com/ethereum/go-ethereum/common"
	"github.com/holiman/uint256"
	"github.com/shopspring/decimal"
	"github.com/thal0x/bn/u256"

	"github.com/skip-mev/skipper/defillama"
	"github.com/skip-mev/skipper/uniswapv2"
)

func (bot *Bot) getTokenPrices() {
	batchSize := 100

	tokens := bot.tokenCache.All()

	batches := make([][]common.Address, 0)
	batches = append(batches, make([]common.Address, 0))

	for _, token := range tokens {
		batches[len(batches)-1] = append(batches[len(batches)-1], token.Address)

		if len(batches[len(batches)-1]) == batchSize {
			batches = append(batches, make([]common.Address, 0))
		}
	}

	var wg sync.WaitGroup
	mu := sync.Mutex{}

	allPrices := make(map[common.Address]*uint256.Int)

	for _, batch := range batches {
		wg.Add(1)

		go func(batch []common.Address) {
			defer wg.Done()

			prices, err := defillama.GetTokenPrices(batch)
			if err != nil {
				fmt.Println(err)
				return
			}

			mu.Lock()
			for tokenAddress, coin := range prices {
				price256 := u256.FromBig(decimal.NewFromFloat(coin.Price).Shift(18).BigInt())
				allPrices[tokenAddress] = price256
			}
			mu.Unlock()
		}(batch)
	}

	wg.Wait()

	bot.tokenPrices = allPrices
}

func (bot *Bot) GetPairLiquidityUSD(pair *uniswapv2.Pair) decimal.Decimal {
	priceToken0, ok := bot.tokenPrices[pair.Token0.Address]
	if !ok {
		priceToken0 = u256.ZERO
	}
	fPriceToken0 := decimal.NewFromBigInt(priceToken0.ToBig(), -18)

	priceToken1, ok := bot.tokenPrices[pair.Token1.Address]
	if !ok {
		priceToken1 = u256.ZERO
	}
	fPriceToken1 := decimal.NewFromBigInt(priceToken1.ToBig(), -18)

	balances := pair.Balances(nil)

	if fPriceToken0.IsPositive() && fPriceToken1.IsPositive() {
		balanceToken0 := decimal.NewFromBigInt(balances[pair.Token0.Address].ToBig(), -int32(pair.Token0.Decimals))
		valueToken0 := fPriceToken0.Mul(balanceToken0)

		balanceToken1 := decimal.NewFromBigInt(balances[pair.Token1.Address].ToBig(), -int32(pair.Token1.Decimals))
		valueToken1 := fPriceToken1.Mul(balanceToken1)

		return valueToken0.Add(valueToken1)
	}

	if fPriceToken0.IsPositive() && fPriceToken1.IsZero() {
		balanceToken0 := decimal.NewFromBigInt(balances[pair.Token0.Address].ToBig(), -int32(pair.Token0.Decimals))
		valueToken0 := fPriceToken0.Mul(balanceToken0)

		return valueToken0.Mul(decimal.NewFromFloat(2))
	}

	if fPriceToken0.IsZero() && fPriceToken1.IsPositive() {
		balanceToken1 := decimal.NewFromBigInt(balances[pair.Token1.Address].ToBig(), -int32(pair.Token1.Decimals))
		valueToken1 := fPriceToken1.Mul(balanceToken1)

		return valueToken1.Mul(decimal.NewFromFloat(2))
	}

	return decimal.NewFromFloat(0)
}
