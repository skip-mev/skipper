package uniswapv2

import (
	"sync"

	"github.com/ethereum/go-ethereum/common"
)

type PairCache struct {
	byAddress map[common.Address]*Pair
	byTokens  map[[2]common.Address]*Pair
	mu        sync.Mutex
}

func NewPairCache() *PairCache {
	return &PairCache{
		byAddress: make(map[common.Address]*Pair),
		byTokens:  make(map[[2]common.Address]*Pair),
		mu:        sync.Mutex{},
	}
}

func (c *PairCache) All() []*Pair {
	c.mu.Lock()
	pairsMap := c.byAddress
	c.mu.Unlock()

	pairs := make([]*Pair, 0)

	for _, pair := range pairsMap {
		pairs = append(pairs, pair)
	}

	return pairs
}

func (c *PairCache) GetByAddress(address common.Address) (*Pair, bool) {
	c.mu.Lock()
	pair, found := c.byAddress[address]
	c.mu.Unlock()

	return pair, found
}

func (c *PairCache) GetByTokens(tokenA, tokenB common.Address) (*Pair, bool) {
	c.mu.Lock()
	pair, found := c.byTokens[[2]common.Address{tokenA, tokenB}]
	c.mu.Unlock()

	return pair, found
}

func (c *PairCache) Set(pair *Pair) {
	c.mu.Lock()
	c.byAddress[pair.Address] = pair
	c.byTokens[[2]common.Address{pair.Token0.Address, pair.Token1.Address}] = pair
	c.byTokens[[2]common.Address{pair.Token1.Address, pair.Token0.Address}] = pair
	c.mu.Unlock()
}
