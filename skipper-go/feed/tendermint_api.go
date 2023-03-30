package feed

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type UnconfirmedTransactionsResult struct {
	Txs []string `json:"txs"`
}

type UnconfirmedTransactionsResponse struct {
	Result UnconfirmedTransactionsResult `json:"result"`
}

func (feed *TransactionFeed) getUnconfirmedTransactions() ([]string, error) {
	response, err := http.Get(fmt.Sprintf("%s/unconfirmed_txs?limit=1000", feed.url))
	if err != nil {
		panic(err)
	}

	defer response.Body.Close()

	var data UnconfirmedTransactionsResponse

	err = json.NewDecoder(response.Body).Decode(&data)
	if err != nil {
		return nil, err
	}

	return data.Result.Txs, nil
}
