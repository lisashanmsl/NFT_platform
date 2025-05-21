from web3 import Web3
import json
import os
from config import GANACHE_URL, PRIVATE_KEY, PUBLIC_ADDRESS, CONTRACT_ADDRESS

HISTORY_FILE = 'nft_history.json'  # 歷史紀錄檔案路徑

def save_history(new_entry):
    """保存 NFT 歷史紀錄，避免重複的 token_id"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    # 檢查是否已存在相同的 token_id
    for item in history:
        if item.get("token_id") == new_entry.get("token_id"):
            print(f"Token ID {new_entry['token_id']} 已存在，更新歷史紀錄")
            item.update(new_entry)  # 更新已存在的紀錄
            break
    else:
        # 如果不存在，則新增到歷史紀錄
        history.append(new_entry)

    # 寫回文件
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"歷史紀錄已更新，Token ID: {new_entry['token_id']}")
    except Exception as e:
        print(f"無法寫入歷史紀錄，錯誤: {e}")

# 建立 Web3 實例
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not web3.is_connected():
    raise Exception("無法連接到區塊鏈節點")

# 讀取 ABI
with open("contracts/MyNFT_abi.json") as f:
    abi = json.load(f)["abi"]

# 建立合約實例
contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS.strip()), abi=abi)

def mint_nft(to_address, token_uri, price):
    """鑄造 NFT 並返回交易哈希"""
    if not Web3.is_address(to_address):
        raise ValueError(f"無效的以太坊地址: {to_address}")
    to_address = Web3.to_checksum_address(to_address)

    sender_address = Web3.to_checksum_address(PUBLIC_ADDRESS)

    # 獲取 nonce
    nonce = web3.eth.get_transaction_count(sender_address)

    # 建立交易
    txn = contract.functions.mintNFT(
        to_address,
        token_uri,
        price
    ).build_transaction({
        'from': sender_address,
        'gas': 500000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': nonce
    })

    # 簽署並發送交易
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    # 等待交易完成
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # 從事件中獲取 token_id
    logs = contract.events.Transfer().process_receipt(receipt)
    if logs:
        token_id = logs[0]["args"]["tokenId"]

        # 儲存歷史紀錄
        save_history({
            'name': "NFT Name",  # 替換為實際名稱
            'description': "NFT Description",  # 替換為實際描述
            'image_path': "path/to/image",  # 替換為實際圖片路徑
            'metadata_uri': token_uri,
            'tx_hash': web3.to_hex(tx_hash),
            'token_id': token_id,
            'price': price
        })

    return web3.to_hex(tx_hash)

def update_nft_for_sale():
    """將歷史紀錄中的所有 NFT 設置為可出售"""
    with open("nft_history.json", "r", encoding="utf-8") as f:
        history = json.load(f)

    for item in history:
        token_id = item.get("token_id")
        price = web3.to_wei(1, 'ether')  # 預設價格為 1 ETH
        if token_id is not None:
            try:
                # 檢查 token_id 是否存在於智能合約中
                owner = contract.functions.ownerOf(token_id).call()
                if owner:
                    tx_hash = set_nft_for_sale(token_id, price)
                    print(f"Token ID {token_id} 已設置為可出售，交易哈希: {tx_hash}")
            except Exception as e:
                print(f"無法設置 Token ID {token_id} 為可出售，錯誤: {e}")
        else:
            print(f"跳過無效的 Token ID: {token_id}")

    print("所有歷史紀錄中的 NFT 已設置為可出售")
    
def get_owned_nfts(owner_address):
    """獲取指定地址擁有的所有 NFT"""
    if not web3.is_address(owner_address):
        raise ValueError(f"無效的以太坊地址: {owner_address}")

    owner_address = web3.to_checksum_address(owner_address)
    total_supply = contract.functions.totalSupply().call()  # 獲取 NFT 的總供應量
    owned_nfts = []

    for token_id in range(total_supply):
        try:
            # 獲取 NFT 的擁有者
            nft_owner = contract.functions.ownerOf(token_id).call()
            if nft_owner == owner_address:
                # 獲取 NFT 的詳細資訊
                nft_uri = contract.functions.tokenURI(token_id).call()
                owned_nfts.append({
                    "id": token_id,
                    "uri": nft_uri
                })
        except Exception as e:
            print(f"無法獲取 Token ID {token_id} 的擁有者，錯誤: {e}")

    return owned_nfts

def get_all_token_ids():
    """獲取智能合約中所有存在的 Token ID"""
    total_supply = contract.functions.totalSupply().call()
    token_ids = []
    for token_id in range(total_supply):
        try:
            owner = contract.functions.ownerOf(token_id).call()
            token_ids.append(token_id)
        except Exception as e:
            print(f"無法獲取 Token ID {token_id} 的擁有者，錯誤: {e}")
    return token_ids

def buy_nft_by_token_id(buyer_address, token_id):
    """購買指定 Token ID 的 NFT"""
    if not Web3.is_address(buyer_address):
        raise ValueError(f"無效的以太坊地址: {buyer_address}")
    buyer_address = Web3.to_checksum_address(buyer_address)

    # 獲取 NFT 價格
    price = contract.functions.getPrice(token_id).call()

    # 獲取 nonce
    nonce = web3.eth.get_transaction_count(buyer_address)

    # 建立交易
    txn = contract.functions.buyNFT(token_id).build_transaction({
        'from': buyer_address,
        'value': price,
        'gas': 300000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': nonce
    })

    return txn  # 返回交易數據，讓前端簽名並發送

def set_nft_for_sale(token_id, price):
    """將指定的 NFT 設置為可出售"""
    sender_address = Web3.to_checksum_address(PUBLIC_ADDRESS)

    # 獲取 nonce
    nonce = web3.eth.get_transaction_count(sender_address)

    # 建立交易
    txn = contract.functions.setForSale(token_id, price).build_transaction({
        'from': sender_address,
        'gas': 300000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': nonce
    })

    # 簽署並發送交易
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    return web3.to_hex(tx_hash)

def get_nft_price(token_id):
    """從智能合約中獲取指定 NFT 的價格"""
    try:
        price = contract.functions.getPrice(token_id).call()
        return price
    except Exception as e:
        raise ValueError(f"無法獲取 Token ID {token_id} 的價格，錯誤: {e}")