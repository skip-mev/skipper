// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";

import "../src/Multihop.sol";

contract DeployScript is Script {
    function run() external {
        vm.startBroadcast();

        new Multihop();

        vm.stopBroadcast();
    }
}
