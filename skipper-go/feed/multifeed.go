package feed

import (
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/lrita/cmap"
)

type MultiFeed struct {
	Feeds []*TransactionFeed

	knownTxs *cmap.Map[string, bool]
}

func NewMultiFeed(urls []string, pollMs int) *MultiFeed {
	feeds := make([]*TransactionFeed, len(urls))
	for i, url := range urls {
		feeds[i] = NewTransactionFeed(url, pollMs)
	}
	return &MultiFeed{
		Feeds:    feeds,
		knownTxs: &cmap.Map[string, bool]{},
	}
}

func (feed *MultiFeed) SubscribeNewTransactions() chan *types.Transaction {
	ch := make(chan *types.Transaction)

	for _, feed := range feed.Feeds {
		go func(feed *TransactionFeed) {
			for tx := range feed.SubscribeNewTransactions() {
				ch <- tx
			}
		}(feed)
	}

	return ch
}
