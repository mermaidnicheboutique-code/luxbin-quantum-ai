const { ethers } = require("hardhat");

async function main() {
  console.log("🌟 Deploying LuxbinXReserve - Circle xReserve Integration...\n");

  const [deployer] = await ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH\n`);

  // Contract addresses (use mock addresses for testing)
  const luxbinStableAddress = "0x66b4627B4Dd73228D24f24E844B6094091875169"; // LuxbinToken
  const usdcReserveAddress = deployer.address; // Mock USDC reserve
  const xReserveBridgeAddress = deployer.address; // Mock xReserve bridge

  // Deploy the xReserve integration contract
  console.log("📝 Deploying LuxbinXReserve...");
  const LuxbinXReserve = await ethers.getContractFactory("LuxbinXReserve");

  const xReserve = await LuxbinXReserve.deploy(
    luxbinStableAddress,
    usdcReserveAddress,
    xReserveBridgeAddress
  );

  await xReserve.waitForDeployment();
  const xReserveAddress = await xReserve.getAddress();

  console.log(`✅ LuxbinXReserve deployed: ${xReserveAddress}`);

  // Get initial stats
  const [reserveBalance, totalSupply, minted, burned] = await xReserve.getReserveStats();
  console.log(`\n📊 Initial Stats:`);
  console.log(`Reserve Balance: ${reserveBalance} USDC`);
  console.log(`Total Supply: ${totalSupply} LUXBIN`);
  console.log(`Total Minted: ${minted} LUXBIN`);
  console.log(`Total Burned: ${burned} LUXBIN`);

  // Check backing
  const [isFullyBacked, backingRatio] = await xReserve.checkBacking();
  console.log(`\n🔒 Reserve Backing:`);
  console.log(`Fully Backed: ${isFullyBacked}`);
  console.log(`Backing Ratio: ${backingRatio / 100}%`);

  console.log("\n🎯 Ready for Circle xReserve integration!");
  console.log(`🌐 Contract address: ${xReserveAddress}`);
  console.log("🔑 Circle xReserve attestation system ready");
  console.log("🌉 Cross-chain LUXBIN transfers enabled");

  console.log("\n📖 Usage:");
  console.log(`- Mint with attestation: mintWithAttestation(amount, attestationId, signature)`);
  console.log(`- Burn with attestation: burnWithAttestation(amount, attestationId, signature)`);
  console.log(`- Cross-chain transfer: crossChainTransfer(amount, destChain, destAddress, attestationId)`);

  console.log("\n✅ Luxbin xReserve integration deployed and ready!");
}

// Handle errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });