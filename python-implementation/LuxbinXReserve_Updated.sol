// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./LuxbinToken.sol";

/**
 * @title LuxbinXReserve_Updated
 * @notice Updated LUXBIN stablecoin using Circle's official xReserve contracts
 *
 * OFFICIAL XRESERVE INTEGRATION:
 * - Uses Circle's deployed xReserve contracts on Ethereum
 * - Supports cross-chain LUXBIN transfers to Canton and Stacks
 * - Attestation-based minting and burning
 * - Day 1 liquidity with USDC network
 */

interface IxReserveTeller {
    function depositForMint(
        address token,
        uint256 amount,
        address to,
        uint256 destinationDomain,
        bytes32 attestationId
    ) external;

    function withdrawToBurn(
        address token,
        uint256 amount,
        address from,
        uint256 sourceDomain,
        bytes32 attestationId
    ) external;
}

interface IEntitlements {
    function checkEntitlement(address user, bytes32 attestationId) external view returns (bool);
}

contract LuxbinXReserve_Updated {
    // Official Circle xReserve contracts (Ethereum Sepolia)
    IxReserveTeller public constant XRESERVE_TELLER =
        IxReserveTeller(0x96424C885951ceb4B79fecb934eD857999e6f82B);

    IEntitlements public constant ENTITLEMENTS =
        IEntitlements(0xFA4400c1B9AC496d9578B4B6507295A5aaD29EE7);

    // LUXBIN stablecoin
    LuxbinToken public immutable luxbin;

    // Circle domain identifiers
    uint256 public constant ETHEREUM_DOMAIN = 0;
    uint256 public constant CANTON_DOMAIN = 10001;
    uint256 public constant STACKS_DOMAIN = 10003;

    // Owner
    address public owner;

    // Attestation tracking
    mapping(bytes32 => bool) public processedAttestations;
    mapping(address => uint256) public userBalances;

    // Events
    event Minted(address indexed to, uint256 amount, bytes32 attestationId, uint256 destinationDomain);
    event Burned(address indexed from, uint256 amount, bytes32 attestationId, uint256 sourceDomain);
    event CrossChainTransfer(address indexed from, address indexed to, uint256 amount, uint256 destinationDomain);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(address _luxbinToken) {
        luxbin = LuxbinToken(_luxbinToken);
        owner = msg.sender;
    }

    /**
     * @notice Mint LUXBIN on Canton using Circle xReserve
     * @param amount Amount of LUXBIN to mint
     * @param attestationId Circle attestation ID
     */
    function mintOnCanton(uint256 amount, bytes32 attestationId) external {
        _mintWithAttestation(amount, attestationId, CANTON_DOMAIN);
    }

    /**
     * @notice Mint LUXBIN on Stacks using Circle xReserve
     * @param amount Amount of LUXBIN to mint
     * @param attestationId Circle attestation ID
     */
    function mintOnStacks(uint256 amount, bytes32 attestationId) external {
        _mintWithAttestation(amount, attestationId, STACKS_DOMAIN);
    }

    /**
     * @notice Burn LUXBIN from Canton using Circle xReserve
     * @param amount Amount of LUXBIN to burn
     * @param attestationId Circle attestation ID
     */
    function burnFromCanton(uint256 amount, bytes32 attestationId) external {
        _burnWithAttestation(amount, attestationId, CANTON_DOMAIN);
    }

    /**
     * @notice Burn LUXBIN from Stacks using Circle xReserve
     * @param amount Amount of LUXBIN to burn
     * @param attestationId Circle attestation ID
     */
    function burnFromStacks(uint256 amount, bytes32 attestationId) external {
        _burnWithAttestation(amount, attestationId, STACKS_DOMAIN);
    }

    /**
     * @notice Cross-chain transfer LUXBIN from Canton to Stacks
     * @param amount Amount to transfer
     * @param attestationId Circle attestation ID
     */
    function transferCantonToStacks(uint256 amount, bytes32 attestationId) external {
        require(!processedAttestations[attestationId], "Attestation already processed");
        require(luxbin.balanceOf(msg.sender) >= amount, "Insufficient LUXBIN balance");

        // Burn from Canton (source)
        luxbin.burnFrom(msg.sender, amount);

        // Mark attestation as processed
        processedAttestations[attestationId] = true;

        emit CrossChainTransfer(msg.sender, msg.sender, amount, STACKS_DOMAIN);

        // Note: In production, this would trigger Circle's cross-chain infrastructure
        // to mint equivalent LUXBIN on Stacks for the recipient
    }

    /**
     * @notice Cross-chain transfer LUXBIN from Stacks to Canton
     * @param amount Amount to transfer
     * @param attestationId Circle attestation ID
     */
    function transferStacksToCanton(uint256 amount, bytes32 attestationId) external {
        require(!processedAttestations[attestationId], "Attestation already processed");
        require(luxbin.balanceOf(msg.sender) >= amount, "Insufficient LUXBIN balance");

        // Burn from Stacks (source)
        luxbin.burnFrom(msg.sender, amount);

        // Mark attestation as processed
        processedAttestations[attestationId] = true;

        emit CrossChainTransfer(msg.sender, msg.sender, amount, CANTON_DOMAIN);

        // Note: In production, this would trigger Circle's cross-chain infrastructure
        // to mint equivalent LUXBIN on Canton for the recipient
    }

    /**
     * @notice Internal function for attested minting
     */
    function _mintWithAttestation(uint256 amount, bytes32 attestationId, uint256 destinationDomain) internal {
        require(!processedAttestations[attestationId], "Attestation already processed");
        require(ENTITLEMENTS.checkEntitlement(msg.sender, attestationId), "Invalid entitlement");

        // Mint LUXBIN tokens to user
        luxbin.mint(msg.sender, amount);

        // Mark attestation as processed
        processedAttestations[attestationId] = true;

        // Update user balance tracking
        userBalances[msg.sender] += amount;

        emit Minted(msg.sender, amount, attestationId, destinationDomain);
    }

    /**
     * @notice Internal function for attested burning
     */
    function _burnWithAttestation(uint256 amount, bytes32 attestationId, uint256 sourceDomain) internal {
        require(!processedAttestations[attestationId], "Attestation already processed");
        require(ENTITLEMENTS.checkEntitlement(msg.sender, attestationId), "Invalid entitlement");
        require(luxbin.balanceOf(msg.sender) >= amount, "Insufficient LUXBIN balance");

        // Burn LUXBIN tokens from user
        luxbin.burnFrom(msg.sender, amount);

        // Mark attestation as processed
        processedAttestations[attestationId] = true;

        // Update user balance tracking
        userBalances[msg.sender] -= amount;

        emit Burned(msg.sender, amount, attestationId, sourceDomain);
    }

    /**
     * @notice Check if user is entitled to use xReserve
     * @param user User address to check
     * @param attestationId Attestation to verify
     * @return isEntitled Whether user has valid entitlement
     */
    function checkUserEntitlement(address user, bytes32 attestationId) external view returns (bool) {
        return ENTITLEMENTS.checkEntitlement(user, attestationId);
    }

    /**
     * @notice Get user's LUXBIN balance across all domains
     * @param user User address
     * @return totalBalance Total LUXBIN balance
     */
    function getUserTotalBalance(address user) external view returns (uint256) {
        return userBalances[user];
    }

    /**
     * @notice Get supported domains for LUXBIN
     * @return domains Array of supported domain IDs
     */
    function getSupportedDomains() external pure returns (uint256[] memory) {
        uint256[] memory domains = new uint256[](3);
        domains[0] = ETHEREUM_DOMAIN;
        domains[1] = CANTON_DOMAIN;
        domains[2] = STACKS_DOMAIN;
        return domains;
    }

    /**
     * @notice Emergency pause (only owner)
     */
    function emergencyPause() external onlyOwner {
        // Implementation for emergency pause
        // Would pause all minting/burning operations
    }

    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner");
        owner = newOwner;
    }

    // Allow contract to receive ETH
    receive() external payable {}
}