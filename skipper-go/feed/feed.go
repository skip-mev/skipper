package feed

import (
	"encoding/base64"
	"fmt"
	"reflect"
	"time"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/lrita/cmap"

	"github.com/cosmos/cosmos-sdk/client"
	codectypes "github.com/cosmos/cosmos-sdk/codec/types"

	evm "github.com/evmos/ethermint/x/evm/types"
)

type TransactionFeed struct {
	knownTxs *cmap.Cmap
	url      string
	txConfig client.TxConfig
	pollMs   int
}

func NewTransactionFeed(url string, pollMs int, reg codectypes.InterfaceRegistry, txConfig client.TxConfig) *TransactionFeed {
	return &TransactionFeed{
		knownTxs: &cmap.Cmap{},
		url:      url,
		txConfig: txConfig,
		pollMs:   pollMs,
	}
}

func (feed *TransactionFeed) SubscribeNewTransactions() chan *types.Transaction {
	ch := make(chan *types.Transaction)

	go func() {
		for {
			txHashes, err := feed.getUnconfirmedTransactions()
			if err != nil {
				fmt.Println(err)
				continue
			}

			for _, txHash := range txHashes {
				_, known := feed.knownTxs.LoadOrStore(txHash, true)
				if !known {
					txs, err := feed.getEthereumTransactions(txHash)
					if err != nil {
						continue
					}

					for _, tx := range txs {
						ch <- tx
					}
				}
			}

			time.Sleep(time.Duration(feed.pollMs) * time.Millisecond)
		}
	}()

	return ch
}

func (feed *TransactionFeed) getEthereumTransactions(txString string) (types.Transactions, error) {
	tx64, _ := base64.StdEncoding.DecodeString(txString)

	tx, err := feed.txConfig.TxDecoder()(tx64)
	if err != nil {
		return nil, err
	}

	transactions := make([]*types.Transaction, 0)

	for _, msg := range tx.GetMsgs() {
		if reflect.TypeOf(msg).String() == "*types.MsgEthereumTx" {
			ethMsg := msg.(*evm.MsgEthereumTx)
			transactions = append(transactions, ethMsg.AsTransaction())
		}
	}

	return transactions, nil
}
