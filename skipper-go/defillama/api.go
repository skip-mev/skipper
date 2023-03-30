package defillama

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/ethereum/go-ethereum/common"
)

type Coin struct {
	Decimals   uint8
	Price      float64
	Symbol     string
	Timestamp  int64
	Confidence float64
}

type GetTokenPricesResponse struct {
	Coins map[string]Coin
}

func GetTokenPrices(tokens []common.Address) (map[common.Address]Coin, error) {
	coinParams := make([]string, 0)

	for _, token := range tokens {
		coinParams = append(coinParams, fmt.Sprintf("evmos:%s", token))
	}

	resp, err := http.Get(fmt.Sprintf("https://coins.llama.fi/prices/current/%s", strings.Join(coinParams, ",")))
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()

	var decodedBody GetTokenPricesResponse
	err = json.NewDecoder(resp.Body).Decode(&decodedBody)
	if err != nil {
		return nil, err
	}

	coinMap := make(map[common.Address]Coin)

	for coinID, coin := range decodedBody.Coins {
		coinAddress := strings.Split(coinID, ":")[1]

		coinMap[common.HexToAddress(coinAddress)] = coin
	}

	return coinMap, nil
}
