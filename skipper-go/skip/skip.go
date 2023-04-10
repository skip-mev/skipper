package skip

import (
	"bytes"
	"crypto/ecdsa"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/cosmos/cosmos-sdk/client"
	clientTx "github.com/cosmos/cosmos-sdk/client/tx"
	"github.com/cosmos/cosmos-sdk/codec"
	ctypes "github.com/cosmos/cosmos-sdk/codec/types"
	"github.com/cosmos/cosmos-sdk/crypto/keys/secp256k1"
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/cosmos/cosmos-sdk/types/tx/signing"
	xauthsigning "github.com/cosmos/cosmos-sdk/x/auth/signing"
	"github.com/cosmos/cosmos-sdk/x/auth/tx"
	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	evmosEthsecp256k1 "github.com/evmos/ethermint/crypto/ethsecp256k1"
)

type SkipClient struct {
	SignerAddress string

	account             *Account
	restURL             string
	privateKey          *evmosEthsecp256k1.PrivKey
	txConfig            client.TxConfig
	auctionHouseAddress string
	sentinelURL         string
}

func NewSkipClient(
	key *ecdsa.PrivateKey,
	restURL string,
	sentinelURL string,
	auctionHouseAddress string,
) (*SkipClient, error) {
	ecp256k1k1Key := &evmosEthsecp256k1.PrivKey{}
	err := ecp256k1k1Key.UnmarshalAmino(crypto.FromECDSA(key))
	if err != nil {
		return nil, err
	}

	bech32Address, err := sdk.Bech32ifyAddressBytes("evmos", ecp256k1k1Key.PubKey().Address().Bytes())
	if err != nil {
		panic(err)
	}

	client := &SkipClient{
		SignerAddress: bech32Address,

		restURL:             restURL,
		privateKey:          ecp256k1k1Key,
		txConfig:            tx.NewTxConfig(codec.NewProtoCodec(ctypes.NewInterfaceRegistry()), tx.DefaultSignModes),
		auctionHouseAddress: auctionHouseAddress,
		sentinelURL:         sentinelURL,
	}

	go func() {
		for {
			account, err := client.getAccount(bech32Address)
			if err != nil {
				fmt.Println(err)
				time.Sleep(5 * time.Second)
			}

			client.account = account

			time.Sleep(5 * time.Second)
		}
	}()

	return client, nil
}

func (client *SkipClient) CreateAndSendBundle(bid int64, txs types.Transactions) (*SendBundleResult, error) {
	txBuilder := client.txConfig.NewTxBuilder()

	sendMsg, err := client.generatePaymentMessage(bid, "aevmos")
	if err != nil {
		return nil, err
	}

	err = txBuilder.SetMsgs(sendMsg)
	if err != nil {
		return nil, err
	}

	txBuilder.SetGasLimit(5000000)
	txBuilder.SetFeeAmount(sdk.NewCoins(sdk.NewCoin("aevmos", sdk.NewInt(200000000000000000))))

	seqNum, _ := strconv.Atoi(client.account.Sequence)
	accNum, _ := strconv.Atoi(client.account.AccountNumber)

	uSeqNum := uint64(seqNum + 1)
	uAccNum := uint64(accNum)

	var sigsV2 []signing.SignatureV2

	sigV2 := signing.SignatureV2{
		PubKey: client.privateKey.PubKey(),
		Data: &signing.SingleSignatureData{
			SignMode:  client.txConfig.SignModeHandler().DefaultMode(),
			Signature: nil,
		},
		Sequence: uSeqNum,
	}

	sigsV2 = append(sigsV2, sigV2)

	err = txBuilder.SetSignatures(sigsV2...)
	if err != nil {
		return nil, err
	}

	sigsV2 = []signing.SignatureV2{}
	signerData := xauthsigning.SignerData{
		ChainID:       "evmos_9001-2",
		AccountNumber: uAccNum,
		Sequence:      uSeqNum,
	}

	sigV2, err = clientTx.SignWithPrivKey(client.txConfig.SignModeHandler().DefaultMode(), signerData, txBuilder, client.privateKey, client.txConfig, uSeqNum)
	if err != nil {
		return nil, err
	}

	sigsV2 = append(sigsV2, sigV2)

	err = txBuilder.SetSignatures(sigsV2...)
	if err != nil {
		return nil, err
	}

	bz, err := client.txConfig.TxEncoder()(txBuilder.GetTx())
	if err != nil {
		return nil, err
	}

	rawTransactions := make([][]byte, 0)
	for _, tx := range txs {
		txData, err := tx.MarshalBinary()
		if err != nil {
			return nil, err
		}

		rawTransactions = append(rawTransactions, txData)
	}

	rawTransactions = append(rawTransactions, bz)

	resp, err := SignAndSendBundle(
		rawTransactions,
		client.privateKey.Bytes(),
		base64.StdEncoding.EncodeToString(client.privateKey.PubKey().Bytes()), // public key
		client.sentinelURL,
		"0",
		true,
	)
	if err != nil {
		return nil, err
	}

	// Print result
	var result SendBundleResponse
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	if result.Result.Code == 0 {
		return nil, err
	}

	return &result.Result, nil
}

func (client *SkipClient) generatePaymentMessage(amount int64, denom string) (*banktypes.MsgSend, error) {
	coins := sdk.NewCoins(sdk.NewCoin(denom, sdk.NewInt(amount)))

	msg := &banktypes.MsgSend{
		FromAddress: client.SignerAddress,
		ToAddress:   client.auctionHouseAddress,
		Amount:      coins,
	}

	return msg, nil
}

type Account struct {
	AccountNumber string `json:"account_number"`
	CosmosAddress string
	Sequence      string
}

func (client *SkipClient) getAccount(accountAddress string) (*Account, error) {
	type responseType struct {
		Account struct {
			Type        string `json:"@type"`
			BaseAccount struct {
				Address string `json:"address"`
				PubKey  struct {
					Type string `json:"@type"`
					Key  string `json:"key"`
				} `json:"pub_key"`
				AccountNumber string `json:"account_number"`
				Sequence      string `json:"sequence"`
			} `json:"base_account"`
			CodeHash string `json:"code_hash"`
		} `json:"account"`
	}

	// https://rest.bd.evmos.org:1317/cosmos/auth/v1beta1/accounts/evmos1z92qlcv6242k6p0c4dqr5ce7rkta5ky9qmakwq"

	resp, err := http.Get(fmt.Sprintf("%s/cosmos/auth/v1beta1/accounts/%s", client.restURL, accountAddress))
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()

	result := responseType{}

	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, err
	}

	account := &Account{
		AccountNumber: result.Account.BaseAccount.AccountNumber,
		Sequence:      result.Account.BaseAccount.Sequence,
		CosmosAddress: result.Account.BaseAccount.Address,
	}

	fmt.Println(account)

	return account, nil
}

type SendBundleResult struct {
	AuctionFee                 string      `json:"auction_fee"`
	Code                       int         `json:"code"`
	BundleSize                 string      `json:"bundle_size"`
	DesiredHeight              string      `json:"desired_height"`
	Error                      string      `json:"error"`
	ResultCheckTxs             interface{} `json:"result_check_txs"`
	ResultDeliverTxs           interface{} `json:"result_deliver_txs"`
	SimulationSuccess          bool        `json:"simulation_success"`
	Txs                        interface{} `json:"txs"`
	WaitedForSimulationResults bool        `json:"waited_for_simulation_results"`
}

type SendBundleResponse struct {
	ID     int
	Result SendBundleResult
}

func SignBundle(bundle [][]byte, privateKeyBytes []byte) ([]string, []byte) {
	// Append list of bytes to a single byte slice
	var bundleBytes []byte
	for _, tx := range bundle {
		bundleBytes = append(bundleBytes, tx...)
	}

	// Create private key object to sign
	privKey := secp256k1.PrivKey{Key: privateKeyBytes}

	// Sign digest of bundleBytes, digest is created by
	// hashing the bundleBytes within the Sign method
	bundleSignature, err := privKey.Sign(bundleBytes)

	// Check for errors
	if err != nil {
		panic(err)
	}

	// Create b64 encoded bundle
	base64EncodedBundle := []string{}
	for _, tx := range bundle {
		base64EncodedBundle = append(base64EncodedBundle, base64.StdEncoding.EncodeToString(tx))
	}

	return base64EncodedBundle, bundleSignature
}

func SendBundle(b64EncodedSignedBundle []string, bundleSignature []byte, publicKey string, rpcURL string, desiredHeight string, sync bool) (*http.Response, error) {
	// Send signed bundle to RPC
	var method string
	if sync {
		method = "broadcast_bundle_sync"
	} else {
		method = "broadcast_bundle_async"
	}

	data := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  method,
		"params": []interface{}{
			b64EncodedSignedBundle,
			desiredHeight,
			publicKey,
			bundleSignature,
		},
		"id": 1,
	}

	json_data, err := json.Marshal(data)

	if err != nil {
		panic(err)
	}

	response, err := http.Post(rpcURL, "application/json", bytes.NewBuffer(json_data))
	if err != nil {
		return nil, err
	}
	return response, nil
}

func SignAndSendBundle(bundle [][]byte, privateKeyBytes []byte, publicKey string, rpcURL string, desiredHeight string, sync bool) (*http.Response, error) {
	b64EncodedSignedBundle, bundleSignature := SignBundle(bundle, privateKeyBytes)
	response, err := SendBundle(b64EncodedSignedBundle, bundleSignature, publicKey, rpcURL, desiredHeight, sync)
	if err != nil {
		return nil, err
	}
	return response, nil
}
