// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";

import "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "uniswap-v2-periphery/interfaces/IUniswapV2Router02.sol";
import "uniswap-v2-core/interfaces/IUniswapV2Factory.sol";
import "uniswap-v2-core/interfaces/IUniswapV2Pair.sol";

import "../src/Multihop.sol";

contract MultihopTest is Test {
    using stdStorage for StdStorage;

    uint256 evmosFork;

    receive() external payable {}

    /*//////////////////////////////////////////////////////////////
                                  DEXES
    //////////////////////////////////////////////////////////////*/

    IUniswapV2Factory diffusionFactory =
        IUniswapV2Factory(0x6aBdDa34Fb225be4610a2d153845e09429523Cd2);
    IUniswapV2Router02 diffusionRouter =
        IUniswapV2Router02(0xFCd2Ce20ef8ed3D43Ab4f8C2dA13bbF1C6d9512F);

    IUniswapV2Factory evmoSwapFactory =
        IUniswapV2Factory(0xF24E36e53628C3086493B9EfA785ab9DD85232EB);
    IUniswapV2Router02 evmoSwapRouter =
        IUniswapV2Router02(0x64C3b10636baBb3Ef46a7E2E5248b0dE43198fCB);

    IERC20 atom = IERC20(0xC5e00D3b04563950941f7137B5AfA3a534F0D6d6);
    IERC20 osmo = IERC20(0xFA3C22C069B9556A4B2f7EcE1Ee3B467909f4864);
    IERC20 diff = IERC20(0x3f75ceabCDfed1aCa03257Dc6Bdc0408E2b4b026);
    IERC20 wevmos = IERC20(0xD4949664cD82660AaE99bEdc034a0deA8A0bd517);
    IERC20 grav = IERC20(0x80b5a32E4F032B2a058b4F29EC95EEfEEB87aDcd);

    function setUp() public {
        evmosFork = vm.createFork("https://eth.bd.evmos.org:8545");
    }

    /**
     * @dev Tests that the Multihop contract can successfully perform an arbitrage
     * from WEVMOS -> ATOM -> OSMO -> WEVMOS on the Diffusion dex.
     */
    function testItWorks() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        shiftUniswapV2Price(
            address(diffusionRouter),
            diffusionFactory.getPair(address(atom), address(osmo)),
            address(osmo),
            50
        );

        uint256 amountIn = 20 ether;

        address[] memory path = new address[](4);
        path[0] = address(wevmos);
        path[1] = address(atom);
        path[2] = address(osmo);
        path[3] = address(wevmos);

        uint[] memory amounts = diffusionRouter.getAmountsOut(amountIn, path);

        uint256 amountOut = amounts[3];

        // ensure arbitrage opportunity exists
        assertGt(amountOut, amountIn);

        Multihop multiHop = new Multihop();

        writeTokenBalance(address(multiHop), address(wevmos), amountIn);

        Multihop.DexHop memory hopA = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(
                address(wevmos),
                address(atom)
            ),
            zeroToOne: false,
            fee: 3
        });

        Multihop.DexHop memory hopB = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(address(atom), address(osmo)),
            zeroToOne: true,
            fee: 3
        });

        Multihop.DexHop memory hopC = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(
                address(osmo),
                address(wevmos)
            ),
            zeroToOne: false,
            fee: 3
        });

        Multihop.DexHop[] memory hops = new Multihop.DexHop[](3);
        hops[0] = hopA;
        hops[1] = hopB;
        hops[2] = hopC;

        uint256 balanceBefore = wevmos.balanceOf(address(multiHop));

        multiHop.swapMultihop(address(wevmos), amountIn, hops);

        uint256 balanceAfter = wevmos.balanceOf(address(multiHop));

        assertGt(balanceAfter, balanceBefore);
    }

    /**
     * @dev Tests that the Multihop contract reverts when the provided hops
     * doesn't result in a profitable arbitrage trade.
     */
    function testFailIfArbitrageIsntProfitable() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        uint256 amountIn = 20 ether;

        Multihop multiHop = new Multihop();

        writeTokenBalance(address(multiHop), address(wevmos), amountIn);

        Multihop.DexHop memory hopA = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(
                address(wevmos),
                address(atom)
            ),
            zeroToOne: false,
            fee: 3
        });

        Multihop.DexHop memory hopB = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(address(atom), address(osmo)),
            zeroToOne: true,
            fee: 3
        });

        Multihop.DexHop memory hopC = Multihop.DexHop({
            pairAddress: diffusionFactory.getPair(
                address(osmo),
                address(wevmos)
            ),
            zeroToOne: false,
            fee: 3
        });

        Multihop.DexHop[] memory hops = new Multihop.DexHop[](3);
        hops[0] = hopA;
        hops[1] = hopB;
        hops[2] = hopC;

        multiHop.swapMultihop(address(wevmos), amountIn, hops);
    }

    /**
     * @dev Tests that ERC20 assets can be withdrawn from the multihop contract
     * when called by the contract owner.
     */
    function testWithdrawWorksWhenCalledByOwner() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        uint256 amount = 20 ether;

        Multihop multiHop = new Multihop();

        writeTokenBalance(address(multiHop), address(wevmos), amount);

        // Ensure multiHop contract has a balance of 20 WEVMOS
        // and the contract owner has a balance of 0 WEVMOS.
        assertEq(amount, wevmos.balanceOf(address(multiHop)));
        assertEq(0, wevmos.balanceOf(address(this)));

        // Perform the withdrawal
        multiHop.withdraw(address(wevmos));

        // The multihop contract should now have 0 WEVMOS
        // The contract owner should have a balance of 20 WEVMOS.
        assertEq(0, wevmos.balanceOf(address(multiHop)));
        assertEq(amount, wevmos.balanceOf(address(this)));
    }

    /**
     * @dev Tests that withdraw reverts when called by an
     * address that is not the contract owner.
     */
    function testFailWithdrawWhenCalledByNonOwner() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        address alice = address(0xA);

        uint256 amount = 20 ether;

        Multihop multiHop = new Multihop();

        writeTokenBalance(address(multiHop), address(wevmos), amount);

        // Ensure multiHop contract has a balance of 20 WEVMOS
        // and the contract owner has a balance of 0 WEVMOS.
        assertEq(amount, wevmos.balanceOf(address(multiHop)));
        assertEq(0, wevmos.balanceOf(address(this)));

        vm.prank(alice);

        // Perform the withdrawal
        multiHop.withdraw(address(wevmos));
    }

    /**
     * @dev Tests that the native asset can be withdrawn from the multihop contract
     * when called by the contract owner.
     */
    function testWithdrawNativeBalanceWorksWhenCalledByOwner() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        uint256 amount = 20 ether;

        Multihop multiHop = new Multihop();

        vm.deal(address(multiHop), amount);

        uint256 ownerBalanceBefore = address(this).balance;

        multiHop.withdrawNativeBalance();

        uint256 ownerBalanceAfter = address(this).balance;

        uint256 balanceChange = ownerBalanceAfter - ownerBalanceBefore;

        // Multihop balance should now be 0
        assertEq(0, address(multiHop).balance);
        // The account owners balance should have changed by the same
        // amount as the contracts previous balance.
        assertEq(amount, balanceChange);
    }

    /**
     * @dev Tests that withdrawNativeBalance reverts when called by an
     * address that is not the contract owner.
     */
    function testFailWithdrawNativeBalanceWhenCalledByNonOwner() public {
        vm.selectFork(evmosFork);
        vm.rollFork(10033656);

        address alice = address(0xA);

        uint256 amount = 20 ether;

        Multihop multiHop = new Multihop();

        vm.deal(address(multiHop), amount);

        vm.prank(alice);

        // Perform the withdrawal
        multiHop.withdrawNativeBalance();
    }

    /*//////////////////////////////////////////////////////////////
                                 HELPERS
    //////////////////////////////////////////////////////////////*/

    /**
     * @dev Shifts the exchange rate of a specified uniswap v2 pool.
     * @param router The router address of the dex that owns the pool
     * @param poolAddress The address of the pool you would like to change the exchange rate of
     * @param tokenIn Address of the token you would like to make more expensive (in terms of the other token in the pool)
     * @param percentChange Percent in tenths (10 = 1%) you would like the shift the pool by
     */
    function shiftUniswapV2Price(
        address router,
        address poolAddress,
        address tokenIn,
        uint256 percentChange
    ) internal {
        (uint256 r0, uint256 r1, ) = IUniswapV2Pair(poolAddress).getReserves();

        (uint256 reservesIn, uint256 reservesOut) = IUniswapV2Pair(poolAddress)
            .token0() == tokenIn
            ? (r0, r1)
            : (r1, r0);

        uint256 amountIn = (reservesIn * percentChange) / 1000;

        uint256 amountOut = IUniswapV2Router02(router).getAmountOut(
            amountIn,
            reservesIn,
            reservesOut
        );

        writeTokenBalance(address(this), tokenIn, amountIn);

        IERC20(tokenIn).transfer(poolAddress, amountIn);

        if (IUniswapV2Pair(poolAddress).token0() == tokenIn) {
            IUniswapV2Pair(poolAddress).swap(0, amountOut, address(this), "");
        } else {
            IUniswapV2Pair(poolAddress).swap(amountOut, 0, address(this), "");
        }
    }

    /**
     * @dev Changes the specified accounts token balance
     * @param account Address of the account you'd like to change
     * @param token Address of the token you are changing the accounts balance of
     * @param amount Amount (in wei) you would like to set the token balance to
     */
    function writeTokenBalance(
        address account,
        address token,
        uint256 amount
    ) internal {
        stdstore
            .target(token)
            .sig(IERC20(token).balanceOf.selector)
            .with_key(account)
            .checked_write(amount);
    }
}
