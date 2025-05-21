const { formatEther } = require("ethers");
const hre = require("hardhat");
const { ethers } = require("hardhat"); // ✅ 加這行！


async function main() {
    const [deployer] = await hre.ethers.getSigners();

    console.log("Deploying contract with account:", deployer.address);

    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("Account balance:", formatEther(balance), "ETH");


    const MyNFT = await hre.ethers.getContractFactory("MyNFT");
    const myNFT = await MyNFT.deploy();

    await myNFT.waitForDeployment();

    const contractAddress = await myNFT.getAddress();
    console.log("Contract deployed to:", contractAddress);

    console.log("Deployment complete!");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
