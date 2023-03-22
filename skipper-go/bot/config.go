package bot

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/ethereum/go-ethereum/common"
)

type BotConfig struct {
	AuctionHouseAddress string         `json:"auction_house_address"`
	BidPercent          float64        `json:"bid_percent"`
	BaseToken           common.Address `json:"base_token"`
	CosmosRest          string         `json:"cosmos_rest"`
	CosmosRPC           string         `json:"cosmos_rpc"`
	EthRPC              string         `json:"eth_rpc"`
	MinProfit           string         `json:"min_profit_wei"`
	PollMs              int            `json:"poll_ms"`
	SkipSentinalURL     string         `json:"skip_sentinal_url"`
	Exchanges           *ExchangesConfig
}

func LoadBotConfig(configDir string) (*BotConfig, error) {
	data, err := os.ReadFile(fmt.Sprintf("%s/config.json", configDir))
	if err != nil {
		return nil, err
	}

	var botConfig BotConfig
	err = json.Unmarshal(data, &botConfig)
	if err != nil {
		return nil, err
	}

	exchangesConfig, err := loadExchangesConfig(configDir)
	if err != nil {
		return nil, err
	}

	botConfig.Exchanges = exchangesConfig

	return &botConfig, nil
}

type UniswapV2Config struct {
	Name    string
	Router  common.Address
	Factory common.Address
	Fee     uint64
	FeeBase uint64
}

type ExchangesConfig struct {
	UniswapV2Exchanges []UniswapV2Config
}

func loadExchangesConfig(configDir string) (*ExchangesConfig, error) {
	data, err := os.ReadFile(fmt.Sprintf("%s/exchanges.json", configDir))
	if err != nil {
		return nil, err
	}

	var config ExchangesConfig
	err = json.Unmarshal(data, &config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}
