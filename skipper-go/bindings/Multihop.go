// Code generated - DO NOT EDIT.
// This file is a generated binding and any manual changes will be lost.

package bindings

import (
	"errors"
	"math/big"
	"strings"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/event"
)

// Reference imports to suppress errors if they are not otherwise used.
var (
	_ = errors.New
	_ = big.NewInt
	_ = strings.NewReader
	_ = ethereum.NotFound
	_ = bind.Bind
	_ = common.Big1
	_ = types.BloomLookup
	_ = event.NewSubscription
)

// MultihopDexHop is an auto generated low-level Go binding around an user-defined struct.
type MultihopDexHop struct {
	PairAddress common.Address
	ZeroToOne   bool
	Fee         *big.Int
}

// MultihopMetaData contains all meta data concerning the Multihop contract.
var MultihopMetaData = &bind.MetaData{
	ABI: "[{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"previousOwner\",\"type\":\"address\"},{\"indexed\":true,\"internalType\":\"address\",\"name\":\"newOwner\",\"type\":\"address\"}],\"name\":\"OwnershipTransferred\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"owner\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"renounceOwnership\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"fromToken\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"fromAmount\",\"type\":\"uint256\"},{\"components\":[{\"internalType\":\"address\",\"name\":\"pairAddress\",\"type\":\"address\"},{\"internalType\":\"bool\",\"name\":\"zeroToOne\",\"type\":\"bool\"},{\"internalType\":\"uint256\",\"name\":\"fee\",\"type\":\"uint256\"}],\"internalType\":\"structMultihop.DexHop[]\",\"name\":\"route\",\"type\":\"tuple[]\"}],\"name\":\"swapMultihop\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"newOwner\",\"type\":\"address\"}],\"name\":\"transferOwnership\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"token\",\"type\":\"address\"}],\"name\":\"withdraw\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"withdrawNativeBalance\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"stateMutability\":\"payable\",\"type\":\"receive\"}]",
}

// MultihopABI is the input ABI used to generate the binding from.
// Deprecated: Use MultihopMetaData.ABI instead.
var MultihopABI = MultihopMetaData.ABI

// Multihop is an auto generated Go binding around an Ethereum contract.
type Multihop struct {
	MultihopCaller     // Read-only binding to the contract
	MultihopTransactor // Write-only binding to the contract
	MultihopFilterer   // Log filterer for contract events
}

// MultihopCaller is an auto generated read-only Go binding around an Ethereum contract.
type MultihopCaller struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MultihopTransactor is an auto generated write-only Go binding around an Ethereum contract.
type MultihopTransactor struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MultihopFilterer is an auto generated log filtering Go binding around an Ethereum contract events.
type MultihopFilterer struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MultihopSession is an auto generated Go binding around an Ethereum contract,
// with pre-set call and transact options.
type MultihopSession struct {
	Contract     *Multihop         // Generic contract binding to set the session for
	CallOpts     bind.CallOpts     // Call options to use throughout this session
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// MultihopCallerSession is an auto generated read-only Go binding around an Ethereum contract,
// with pre-set call options.
type MultihopCallerSession struct {
	Contract *MultihopCaller // Generic contract caller binding to set the session for
	CallOpts bind.CallOpts   // Call options to use throughout this session
}

// MultihopTransactorSession is an auto generated write-only Go binding around an Ethereum contract,
// with pre-set transact options.
type MultihopTransactorSession struct {
	Contract     *MultihopTransactor // Generic contract transactor binding to set the session for
	TransactOpts bind.TransactOpts   // Transaction auth options to use throughout this session
}

// MultihopRaw is an auto generated low-level Go binding around an Ethereum contract.
type MultihopRaw struct {
	Contract *Multihop // Generic contract binding to access the raw methods on
}

// MultihopCallerRaw is an auto generated low-level read-only Go binding around an Ethereum contract.
type MultihopCallerRaw struct {
	Contract *MultihopCaller // Generic read-only contract binding to access the raw methods on
}

// MultihopTransactorRaw is an auto generated low-level write-only Go binding around an Ethereum contract.
type MultihopTransactorRaw struct {
	Contract *MultihopTransactor // Generic write-only contract binding to access the raw methods on
}

// NewMultihop creates a new instance of Multihop, bound to a specific deployed contract.
func NewMultihop(address common.Address, backend bind.ContractBackend) (*Multihop, error) {
	contract, err := bindMultihop(address, backend, backend, backend)
	if err != nil {
		return nil, err
	}
	return &Multihop{MultihopCaller: MultihopCaller{contract: contract}, MultihopTransactor: MultihopTransactor{contract: contract}, MultihopFilterer: MultihopFilterer{contract: contract}}, nil
}

// NewMultihopCaller creates a new read-only instance of Multihop, bound to a specific deployed contract.
func NewMultihopCaller(address common.Address, caller bind.ContractCaller) (*MultihopCaller, error) {
	contract, err := bindMultihop(address, caller, nil, nil)
	if err != nil {
		return nil, err
	}
	return &MultihopCaller{contract: contract}, nil
}

// NewMultihopTransactor creates a new write-only instance of Multihop, bound to a specific deployed contract.
func NewMultihopTransactor(address common.Address, transactor bind.ContractTransactor) (*MultihopTransactor, error) {
	contract, err := bindMultihop(address, nil, transactor, nil)
	if err != nil {
		return nil, err
	}
	return &MultihopTransactor{contract: contract}, nil
}

// NewMultihopFilterer creates a new log filterer instance of Multihop, bound to a specific deployed contract.
func NewMultihopFilterer(address common.Address, filterer bind.ContractFilterer) (*MultihopFilterer, error) {
	contract, err := bindMultihop(address, nil, nil, filterer)
	if err != nil {
		return nil, err
	}
	return &MultihopFilterer{contract: contract}, nil
}

// bindMultihop binds a generic wrapper to an already deployed contract.
func bindMultihop(address common.Address, caller bind.ContractCaller, transactor bind.ContractTransactor, filterer bind.ContractFilterer) (*bind.BoundContract, error) {
	parsed, err := abi.JSON(strings.NewReader(MultihopABI))
	if err != nil {
		return nil, err
	}
	return bind.NewBoundContract(address, parsed, caller, transactor, filterer), nil
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Multihop *MultihopRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _Multihop.Contract.MultihopCaller.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Multihop *MultihopRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Multihop.Contract.MultihopTransactor.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Multihop *MultihopRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Multihop.Contract.MultihopTransactor.contract.Transact(opts, method, params...)
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Multihop *MultihopCallerRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _Multihop.Contract.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Multihop *MultihopTransactorRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Multihop.Contract.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Multihop *MultihopTransactorRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Multihop.Contract.contract.Transact(opts, method, params...)
}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_Multihop *MultihopCaller) Owner(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _Multihop.contract.Call(opts, &out, "owner")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_Multihop *MultihopSession) Owner() (common.Address, error) {
	return _Multihop.Contract.Owner(&_Multihop.CallOpts)
}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_Multihop *MultihopCallerSession) Owner() (common.Address, error) {
	return _Multihop.Contract.Owner(&_Multihop.CallOpts)
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_Multihop *MultihopTransactor) RenounceOwnership(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Multihop.contract.Transact(opts, "renounceOwnership")
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_Multihop *MultihopSession) RenounceOwnership() (*types.Transaction, error) {
	return _Multihop.Contract.RenounceOwnership(&_Multihop.TransactOpts)
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_Multihop *MultihopTransactorSession) RenounceOwnership() (*types.Transaction, error) {
	return _Multihop.Contract.RenounceOwnership(&_Multihop.TransactOpts)
}

// SwapMultihop is a paid mutator transaction binding the contract method 0x2b726de8.
//
// Solidity: function swapMultihop(address fromToken, uint256 fromAmount, (address,bool,uint256)[] route) returns()
func (_Multihop *MultihopTransactor) SwapMultihop(opts *bind.TransactOpts, fromToken common.Address, fromAmount *big.Int, route []MultihopDexHop) (*types.Transaction, error) {
	return _Multihop.contract.Transact(opts, "swapMultihop", fromToken, fromAmount, route)
}

// SwapMultihop is a paid mutator transaction binding the contract method 0x2b726de8.
//
// Solidity: function swapMultihop(address fromToken, uint256 fromAmount, (address,bool,uint256)[] route) returns()
func (_Multihop *MultihopSession) SwapMultihop(fromToken common.Address, fromAmount *big.Int, route []MultihopDexHop) (*types.Transaction, error) {
	return _Multihop.Contract.SwapMultihop(&_Multihop.TransactOpts, fromToken, fromAmount, route)
}

// SwapMultihop is a paid mutator transaction binding the contract method 0x2b726de8.
//
// Solidity: function swapMultihop(address fromToken, uint256 fromAmount, (address,bool,uint256)[] route) returns()
func (_Multihop *MultihopTransactorSession) SwapMultihop(fromToken common.Address, fromAmount *big.Int, route []MultihopDexHop) (*types.Transaction, error) {
	return _Multihop.Contract.SwapMultihop(&_Multihop.TransactOpts, fromToken, fromAmount, route)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_Multihop *MultihopTransactor) TransferOwnership(opts *bind.TransactOpts, newOwner common.Address) (*types.Transaction, error) {
	return _Multihop.contract.Transact(opts, "transferOwnership", newOwner)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_Multihop *MultihopSession) TransferOwnership(newOwner common.Address) (*types.Transaction, error) {
	return _Multihop.Contract.TransferOwnership(&_Multihop.TransactOpts, newOwner)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_Multihop *MultihopTransactorSession) TransferOwnership(newOwner common.Address) (*types.Transaction, error) {
	return _Multihop.Contract.TransferOwnership(&_Multihop.TransactOpts, newOwner)
}

// Withdraw is a paid mutator transaction binding the contract method 0x51cff8d9.
//
// Solidity: function withdraw(address token) returns(bool)
func (_Multihop *MultihopTransactor) Withdraw(opts *bind.TransactOpts, token common.Address) (*types.Transaction, error) {
	return _Multihop.contract.Transact(opts, "withdraw", token)
}

// Withdraw is a paid mutator transaction binding the contract method 0x51cff8d9.
//
// Solidity: function withdraw(address token) returns(bool)
func (_Multihop *MultihopSession) Withdraw(token common.Address) (*types.Transaction, error) {
	return _Multihop.Contract.Withdraw(&_Multihop.TransactOpts, token)
}

// Withdraw is a paid mutator transaction binding the contract method 0x51cff8d9.
//
// Solidity: function withdraw(address token) returns(bool)
func (_Multihop *MultihopTransactorSession) Withdraw(token common.Address) (*types.Transaction, error) {
	return _Multihop.Contract.Withdraw(&_Multihop.TransactOpts, token)
}

// WithdrawNativeBalance is a paid mutator transaction binding the contract method 0x6f71c0d4.
//
// Solidity: function withdrawNativeBalance() returns()
func (_Multihop *MultihopTransactor) WithdrawNativeBalance(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Multihop.contract.Transact(opts, "withdrawNativeBalance")
}

// WithdrawNativeBalance is a paid mutator transaction binding the contract method 0x6f71c0d4.
//
// Solidity: function withdrawNativeBalance() returns()
func (_Multihop *MultihopSession) WithdrawNativeBalance() (*types.Transaction, error) {
	return _Multihop.Contract.WithdrawNativeBalance(&_Multihop.TransactOpts)
}

// WithdrawNativeBalance is a paid mutator transaction binding the contract method 0x6f71c0d4.
//
// Solidity: function withdrawNativeBalance() returns()
func (_Multihop *MultihopTransactorSession) WithdrawNativeBalance() (*types.Transaction, error) {
	return _Multihop.Contract.WithdrawNativeBalance(&_Multihop.TransactOpts)
}

// Receive is a paid mutator transaction binding the contract receive function.
//
// Solidity: receive() payable returns()
func (_Multihop *MultihopTransactor) Receive(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Multihop.contract.RawTransact(opts, nil) // calldata is disallowed for receive function
}

// Receive is a paid mutator transaction binding the contract receive function.
//
// Solidity: receive() payable returns()
func (_Multihop *MultihopSession) Receive() (*types.Transaction, error) {
	return _Multihop.Contract.Receive(&_Multihop.TransactOpts)
}

// Receive is a paid mutator transaction binding the contract receive function.
//
// Solidity: receive() payable returns()
func (_Multihop *MultihopTransactorSession) Receive() (*types.Transaction, error) {
	return _Multihop.Contract.Receive(&_Multihop.TransactOpts)
}

// MultihopOwnershipTransferredIterator is returned from FilterOwnershipTransferred and is used to iterate over the raw logs and unpacked data for OwnershipTransferred events raised by the Multihop contract.
type MultihopOwnershipTransferredIterator struct {
	Event *MultihopOwnershipTransferred // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MultihopOwnershipTransferredIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MultihopOwnershipTransferred)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MultihopOwnershipTransferred)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MultihopOwnershipTransferredIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MultihopOwnershipTransferredIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MultihopOwnershipTransferred represents a OwnershipTransferred event raised by the Multihop contract.
type MultihopOwnershipTransferred struct {
	PreviousOwner common.Address
	NewOwner      common.Address
	Raw           types.Log // Blockchain specific contextual infos
}

// FilterOwnershipTransferred is a free log retrieval operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_Multihop *MultihopFilterer) FilterOwnershipTransferred(opts *bind.FilterOpts, previousOwner []common.Address, newOwner []common.Address) (*MultihopOwnershipTransferredIterator, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _Multihop.contract.FilterLogs(opts, "OwnershipTransferred", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return &MultihopOwnershipTransferredIterator{contract: _Multihop.contract, event: "OwnershipTransferred", logs: logs, sub: sub}, nil
}

// WatchOwnershipTransferred is a free log subscription operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_Multihop *MultihopFilterer) WatchOwnershipTransferred(opts *bind.WatchOpts, sink chan<- *MultihopOwnershipTransferred, previousOwner []common.Address, newOwner []common.Address) (event.Subscription, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _Multihop.contract.WatchLogs(opts, "OwnershipTransferred", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MultihopOwnershipTransferred)
				if err := _Multihop.contract.UnpackLog(event, "OwnershipTransferred", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOwnershipTransferred is a log parse operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_Multihop *MultihopFilterer) ParseOwnershipTransferred(log types.Log) (*MultihopOwnershipTransferred, error) {
	event := new(MultihopOwnershipTransferred)
	if err := _Multihop.contract.UnpackLog(event, "OwnershipTransferred", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}
