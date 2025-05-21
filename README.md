# NFT Platform - 基於 Hardhat 的 NFT 平台

一個基於 Hardhat 的 NFT 平台專案，使用 Solidity 開發智能合約，結合 Hardhat 進行測試與部署。本專案包含一個範例智能合約、一個測試文件，以及一個用於部署合約的 Hardhat 模組。

---

## 功能特性

- **NFT 鑄造**：允許用戶鑄造新的 NFT，並設置價格與狀態。
- **NFT 購買**：用戶可以購買已設置為可出售的 NFT。
- **NFT 展示**：用戶可以查看自己持有的 NFT，並顯示圖片與相關資訊。
- **智能合約測試**：使用 Hardhat 提供的測試框架，驗證合約功能的正確性。
- **合約部署**：使用 Hardhat 部署模組，將智能合約部署到區塊鏈網絡。

---
## 安裝依賴
確保你已經安裝了 Node.js 和 npm，然後執行以下指令：
npm install

## 配置 Hardhat
在專案目錄中，修改 hardhat.config.js 文件，設置你的網絡配置（例如本地測試網或以太坊測試網）。

##　使用方法
1. 編譯智能合約
執行以下指令編譯智能合約：
npx hardhat compile

2. 測試智能合約
執行以下指令運行測試：
npx hardhat test

3. 部署智能合約
執行以下指令將智能合約部署到指定網絡：
npx hardhat run [deploy.js](http://_vscodecontentref_/1) --network <network-name>

## 專案結構
nft_platform/
│
├── app.py                        # Flask 主應用程式
├── web3_utils.py                 # 處理與智能合約互動的功能（mintNFT 等）
├── nft_upload.py                 # 處理上傳至 IPFS（Pinata）的邏輯
├── config.py                     # 存放 Ganache URL、私鑰、公鑰、合約地址等設定
├── contracts/
│   └── MyNFT_abi.json            # 智能合約編譯後的 ABI 檔案
│
├── nft_history.json              # 儲存鑄造成功的 NFT 歷史記錄（新加入）
│
├── static/
│   └── uploads/                  # 存放上傳的 NFT 圖片
│       └── xxx.jpg               # 使用者上傳的圖片
│
├── templates/
│   ├── index.html                # 首頁表單（上傳 + 鑄造 NFT）
│   ├── result.html               # 顯示鑄造成功的結果
│   └── history.html              # ✅ 新增：歷史 NFT 紀錄頁面
│
├── requirements.txt              # 相依的 Python 套件
└── README.md                     # 專案說明

Solidity：智能合約開發語言。
Hardhat：以太坊開發環境，用於編譯、測試和部署智能合約。
OpenZeppelin：安全的智能合約庫，提供 ERC721 標準實現。
Node.js：用於運行開發工具和腳本

## 聯絡方式
如果有任何問題或建議，請聯絡：

Email: wenglichen30316@gmail.com
GitHub: lisashanmsl
