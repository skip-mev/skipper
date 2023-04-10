package feed

import (
	"encoding/base64"
	"fmt"
	"reflect"
	"time"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/lrita/cmap"

	"github.com/cosmos/cosmos-sdk/client"
	"github.com/cosmos/cosmos-sdk/codec"
	codectypes "github.com/cosmos/cosmos-sdk/codec/types"
	authtx "github.com/cosmos/cosmos-sdk/x/auth/tx"

	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
	distributiontypes "github.com/cosmos/cosmos-sdk/x/distribution/types"
	govtypes "github.com/cosmos/cosmos-sdk/x/gov/types/v1"
	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
	ethsecp256k1 "github.com/evmos/ethermint/crypto/codec"
	etherminttypes "github.com/evmos/ethermint/types"
	evm "github.com/evmos/ethermint/x/evm/types"
)

type TransactionFeed struct {
	knownTxs *cmap.Cmap
	url      string
	txConfig client.TxConfig
	pollMs   int
}

func NewTransactionFeed(url string, pollMs int) *TransactionFeed {
	reg := codectypes.NewInterfaceRegistry()

	authtypes.RegisterInterfaces(reg)
	banktypes.RegisterInterfaces(reg)
	govtypes.RegisterInterfaces(reg)
	distributiontypes.RegisterInterfaces(reg)
	evm.RegisterInterfaces(reg)
	stakingtypes.RegisterInterfaces(reg)
	ethsecp256k1.RegisterInterfaces(reg)
	etherminttypes.RegisterInterfaces(reg)

	cdc := codec.NewProtoCodec(reg)

	txConfig := authtx.NewTxConfig(cdc, authtx.DefaultSignModes)

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
				fmt.Println(feed.url)
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
