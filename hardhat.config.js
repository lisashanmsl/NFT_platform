require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    ganache: {
      url: "http://127.0.0.1:7545",  // Ganache 的 RPC URL
      accounts: ["814e295f28ed17876ec3773a88d791a5bb0ff2ae8815c6392e6dd3be361d6703"] // Ganache 提供的私鑰
    }
  }
};
