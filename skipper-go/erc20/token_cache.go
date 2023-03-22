package erc20

import (
	"sync"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
)

type TokenCache struct {
	client *ethclient.Client
	tokens map[common.Address]*Token
	mu     sync.Mutex
}

func NewTokenCache(client *ethclient.Client) *TokenCache {
	return &TokenCache{
		client: client,
		tokens: make(map[common.Address]*Token),
		mu:     sync.Mutex{},
	}
}

func (c *TokenCache) Get(address common.Address) (*Token, error) {
	c.mu.Lock()
	token, found := c.tokens[address]
	c.mu.Unlock()

	if found {
		return token, nil
	}

	token, err := NewToken(address, c.client)
	if err != nil {
		return nil, err
	}

	c.Set(token)

	return token, nil
}

func (c *TokenCache) Set(token *Token) {
	c.mu.Lock()
	c.tokens[token.Address] = token
	c.mu.Unlock()
}

func (c *TokenCache) All() []*Token {
	tokens := make([]*Token, 0)

	c.mu.Lock()
	tokenMap := c.tokens
	c.mu.Unlock()

	for _, token := range tokenMap {
		tokens = append(tokens, token)
	}

	return tokens
}
