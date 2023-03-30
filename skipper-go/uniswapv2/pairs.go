package uniswapv2

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/thal0x/bn/bigint"

	"github.com/skip-mev/skipper/bindings"
	"github.com/skip-mev/skipper/util"
)

func (exchange *Exchange) GetPairByAddress(address common.Address) (*Pair, error) {
	pair, ok := exchange.PairCache.GetByAddress(address)
	if ok {
		return pair, nil
	}

	pair, err := NewPair(address, exchange)
	if err != nil {
		return nil, err
	}

	exchange.PairCache.Set(pair)

	return pair, nil
}

func (exchange *Exchange) GetPairByTokens(tokenA common.Address, tokenB common.Address) (*Pair, error) {
	pair, ok := exchange.PairCache.GetByTokens(tokenA, tokenB)
	if ok {
		return pair, nil
	}

	pairAddress, err := exchange.Factory.GetPair(nil, tokenA, tokenB)
	if err != nil {
		return nil, err
	}

	pair, err = NewPair(pairAddress, exchange)
	if err != nil {
		return nil, err
	}

	exchange.PairCache.Set(pair)

	return pair, nil
}

func (exchange *Exchange) LoadAllPairs() error {
	allPairsLength, err := exchange.Factory.AllPairsLength(nil)
	if err != nil {
		fmt.Println("AllPairsLength err:")
		fmt.Println(exchange.Name)
		fmt.Println(exchange.FactoryAddress)
		fmt.Println(exchange)
		fmt.Println(err)
		// return err

		allPairsLength, err = exchange.Factory.TotalPairs(nil)
		if err != nil {
			fmt.Println("TotalPairs err:")
			fmt.Println(exchange.Name)
			fmt.Println(exchange.FactoryAddress)
			fmt.Println(exchange)
			fmt.Println(err)
			return err
		}
	}

	iAllPairsLength := int(allPairsLength.Int64())

	batchSize := 500

	var wg sync.WaitGroup

	semSize := 5

	sem := util.NewSemaphore(semSize)

	for i := 0; i < iAllPairsLength; i += batchSize {
		end := i + batchSize
		if end >= iAllPairsLength {
			end = iAllPairsLength - 1
		}

		sem.Acquire()
		wg.Add(1)

		go func(start, end int) {
			defer wg.Done()
			defer sem.Release()

			err = exchange.BatchLoadPairs(start, end)
			if err != nil {
				fmt.Println("BatchLoadPairs err:")
				fmt.Println(err)
				return
			}
		}(i, end)
	}

	wg.Wait()

	return nil
}

func (exchange *Exchange) BatchLoadPairs(start int, end int) error {
	factoryABI, err := abi.JSON(strings.NewReader(bindings.UniswapV2FactoryABI))
	if err != nil {
		return err
	}

	multicallABI, err := abi.JSON(strings.NewReader(bindings.MulticallABI))
	if err != nil {
		return err
	}

	calls := make([]bindings.Multicall3Call3, 0)

	for i := start; i < end; i++ {
		data, err := factoryABI.Pack("allPairs", bigint.New(int64(i)))
		if err != nil {
			return err
		}

		calls = append(calls, bindings.Multicall3Call3{
			Target:       exchange.FactoryAddress,
			CallData:     data,
			AllowFailure: true,
		})
	}

	multicallData, err := multicallABI.Pack("aggregate3", calls)
	if err != nil {
		return err
	}

	multicallAddress := common.HexToAddress("0xcA11bde05977b3631167028862bE2a173976CA11")

	result, err := exchange.client.CallContract(context.Background(), ethereum.CallMsg{
		To:   &multicallAddress,
		Data: multicallData,
	}, nil)
	if err != nil {
		return err
	}

	parsedResult, err := multicallABI.Unpack("aggregate3", result)
	if err != nil {
		return err
	}

	var wg sync.WaitGroup

	for _, callResult := range parsedResult[0].([]struct {
		Success    bool   "json:\"success\""
		ReturnData []byte "json:\"returnData\""
	}) {

		if !callResult.Success {
			continue
		}

		wg.Add(1)

		go func(address common.Address) {
			defer wg.Done()
			exchange.GetPairByAddress(address)
		}(common.BytesToAddress(callResult.ReturnData))

	}

	wg.Wait()

	return nil
}
