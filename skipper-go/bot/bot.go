package bot

import (
	"context"
	"crypto/ecdsa"
	"fmt"
	"math/big"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/holiman/uint256"
	"github.com/shopspring/decimal"
	"github.com/thal0x/bn/u256"

	"github.com/skip-mev/skipper/bindings"
	"github.com/skip-mev/skipper/erc20"
	"github.com/skip-mev/skipper/skip"
	"github.com/skip-mev/skipper/uniswapv2"
)

type Bot struct {
	baseToken   *erc20.Token
	chainID     *big.Int
	config      *BotConfig
	ethClient   *ethclient.Client
	handlers    map[common.Address]HandlerFunc
	routes      map[common.Address][]*Route
	tokenCache  *erc20.TokenCache
	tokenPrices map[common.Address]*uint256.Int
	minProfit   *uint256.Int
	privateKey  *ecdsa.PrivateKey
	skipClient  *skip.SkipClient

	// exchanges
	uniswapV2Exchanges map[common.Address]*uniswapv2.Exchange

	// multihop contract
	multihop        *bindings.Multihop
	multihopAddress common.Address
	multihopBalance *uint256.Int
}

func NewBot(config *BotConfig, multihopAddress common.Address, privateKey *ecdsa.PrivateKey) (*Bot, error) {
	ethClient, err := ethclient.Dial(config.EthRPC)
	if err != nil {
		return nil, err
	}

	chainID, err := ethClient.ChainID(context.Background())
	if err != nil {
		return nil, err
	}

	multihop, err := bindings.NewMultihop(multihopAddress, ethClient)
	if err != nil {
		return nil, err
	}

	skipClient, err := skip.NewSkipClient(
		privateKey,
		config.CosmosRest,
		config.SkipSentinalURL,
		config.AuctionHouseAddress,
	)
	if err != nil {
		return nil, err
	}

	bot := &Bot{
		config:      config,
		chainID:     chainID,
		ethClient:   ethClient,
		handlers:    make(map[common.Address]HandlerFunc),
		routes:      make(map[common.Address][]*Route),
		tokenCache:  erc20.NewTokenCache(ethClient),
		tokenPrices: make(map[common.Address]*uint256.Int),
		minProfit:   u256.ZERO,
		privateKey:  privateKey,
		skipClient:  skipClient,

		// exchanges
		uniswapV2Exchanges: make(map[common.Address]*uniswapv2.Exchange),

		// multihop contract
		multihop:        multihop,
		multihopAddress: multihopAddress,
		multihopBalance: u256.ZERO,
	}

	return bot, nil
}

func (bot *Bot) Start() error {
	fmt.Println("setting up backrunner...")

	fmt.Printf("signer: %s\n", bot.skipClient.SignerAddress)

	baseToken, err := bot.tokenCache.Get(bot.config.BaseToken)
	if err != nil {
		return err
	}
	bot.baseToken = baseToken

	fmt.Println("base token:", bot.baseToken.Symbol)

	// watch Multihop balance
	go func() {
		baseTokenContract, err := bindings.NewERC20(bot.baseToken.Address, bot.ethClient)
		if err != nil {
			panic(err)
		}

		for {
			balance, err := baseTokenContract.BalanceOf(nil, bot.multihopAddress)
			if err != nil {
				fmt.Println("error getting Multihop balance:")
				fmt.Println(err)

				time.Sleep(5 * time.Second)

				continue
			}

			bot.multihopBalance = u256.FromBig(balance)

			time.Sleep(5 * time.Second)
		}
	}()

	bot.minProfit = u256.FromString(bot.config.MinProfit)

	fmt.Printf("min profit: %v %s\n", decimal.NewFromBigInt(bot.minProfit.ToBig(), -int32(bot.baseToken.Decimals)), baseToken.Symbol)

	if err := bot.loadExchanges(); err != nil {
		return err
	}

	bot.getTokenPrices()

	bot.updateRoutes()

	return nil
}

func (bot *Bot) OnTransaction(tx *types.Transaction) {
	to := tx.To()

	if to == nil {
		return
	}

	handler, ok := bot.handlers[*to]
	if !ok {
		return
	}

	handler(tx)
}
