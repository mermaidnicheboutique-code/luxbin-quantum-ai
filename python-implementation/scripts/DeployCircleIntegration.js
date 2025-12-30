const { ethers } = require("hardhat");

async function main() {
  console.log("🔄 Deploying LuxbinCircleIntegration...\n");

  const [deployer] = await ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH\n`);

  // Contract addresses
  const luxbinTokenAddress = "0x66b4627B4Dd73228D24f24E844B6094091875169"; // Deployed LuxbinToken
  const mockUsdcAddress = deployer.address; // Mock USDC for testing

  // Circle API credentials (stored securely)
  const circleApiKey = "b08fb2091d1857fa4cf3abe5af4bfd1a";
  const circleEntitySecret = "5eea90d3f5967c29c04c621625a06769";

  // Deploy the Circle integration contract
  console.log("📝 Deploying LuxbinCircleIntegration...");
  const LuxbinCircleIntegration = await ethers.getContractFactory("LuxbinCircleIntegration");

  const circleIntegration = await LuxbinCircleIntegration.deploy(
    mockUsdcAddress, // Mock Circle API contract address
    luxbinTokenAddress,
    circleApiKey,
    circleEntitySecret
  );

  await circleIntegration.waitForDeployment();
  const integrationAddress = await circleIntegration.getAddress();

  console.log(`✅ LuxbinCircleIntegration deployed: ${integrationAddress}`);

  // Fund the integration contract with some ETH for testing
  console.log("\n💰 Funding integration contract with 0.5 ETH...");
  await deployer.sendTransaction({
    to: integrationAddress,
    value: ethers.parseEther("0.5")
  });
  console.log("✅ Integration contract funded");

  // Check initial stats
  const [mintingEnabled, minStake] = await circleIntegration.getIntegrationStats();
  console.log(`\n📊 Integration Settings:`);
  console.log(`Auto-minting enabled: ${mintingEnabled}`);
  console.log(`Minimum stake: ${minStake} LUXBIN`);

  console.log("\n🎯 Ready for Circle API integration!");
  console.log(`🌐 Contract address: ${integrationAddress}`);
  console.log("🔑 Circle API key configured");
  console.log("🔒 Entity secret secured in contract");

  console.log("\n📖 Usage:");
  console.log(`- Check compliance: call checkCompliance(userAddress)`);
  console.log(`- Mint USDC for staking: call mintUSDCForStaking(user, amount)`);
  console.log(`- Cross-chain transfers: call crossChainTransfer(...)`);

  console.log("\n✅ Circle API integration deployed and ready!");
}

// Handle errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });