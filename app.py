# app.py
from web3 import Web3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import json
from nft_upload import upload_to_pinata
from web3_utils import (
    contract,
    mint_nft,
    get_owned_nfts,
    get_nft_price,
    buy_nft_by_token_id,
    set_nft_for_sale,
    update_nft_for_sale,
    save_history
)
from config import GANACHE_URL, PRIVATE_KEY, PUBLIC_ADDRESS # 確保你有一個配置文件提供區塊鏈節點的 URL

# 初始化 Web3 實例
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# 確保連接成功
if not web3.is_connected():
    raise ConnectionError("無法連接到區塊鏈節點")
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
HISTORY_FILE = 'nft_history.json'  # 歷史紀錄檔案路徑

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/mint', methods=['POST'])
def mint():
    """鑄造 NFT"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    name = request.form.get('name')
    description = request.form.get('description')
    address = request.form.get('address')
    price = request.form.get('price')  # 獲取價格

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not price:
        return jsonify({'error': 'Price is required'}), 400

    try:
        # 儲存圖片
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 上傳 IPFS 並取得 metadata URI
        metadata_uri = upload_to_pinata(filepath, name, description)

        # 將價格從 ETH 轉換為 Wei
        price_in_wei = float(price) * (10 ** 18)

        # 鑄造 NFT 並獲取交易哈希
        tx_hash = mint_nft(address, metadata_uri, int(price_in_wei))

        # 從智能合約中獲取最新的 token_id
        token_id = contract.functions.totalSupply().call() - 1  # 獲取最新的 token_id

        # 儲存歷史紀錄
        save_history({
            'name': name,
            'description': description,
            'image_path': filepath,
            'metadata_uri': metadata_uri,
            'tx_hash': tx_hash,
            'token_id': token_id,
            'price': price
        })

        # 設置 NFT 為可出售
        contract.functions.setForSale(token_id, int(price_in_wei)).transact({
            'from': Web3.to_checksum_address(address)
        })

        # 渲染成功畫面
        return render_template('result.html', 
                               name=name, 
                               description=description, 
                               image_path=filepath, 
                               metadata_uri=metadata_uri, 
                               tx_hash=tx_hash), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/history', methods=['GET'])
def history():
    """返回 NFT 歷史紀錄"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return render_template('history.html', history=history)
    else:
        return render_template('history.html', history=[])
    
@app.route('/buy', methods=['POST'])
def buy():
    """購買 NFT"""
    try:
        data = request.get_json()
        buyer_address = data.get('buyer_address')
        token_id = int(data.get('token_id'))

        if not buyer_address or token_id is None:
            return jsonify({'error': 'Buyer address and Token ID are required'}), 400

        # 檢查 NFT 是否可出售
        is_for_sale = contract.functions.nfts(token_id).call()[1]  # 第二個返回值是 forSale
        if not is_for_sale:
            return jsonify({'error': f'Token ID {token_id} is not for sale'}), 400

        # 獲取 NFT 的價格
        price = contract.functions.getPrice(token_id).call()

        # 獲取 nonce
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(buyer_address))

        # 建立交易
        txn = contract.functions.buyNFT(token_id).build_transaction({
            'from': Web3.to_checksum_address(buyer_address),
            'value': price,
            'gas': 300000,
            'gasPrice': web3.to_wei('10', 'gwei'),
            'nonce': nonce
        })

        return jsonify(txn), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_price', methods=['GET'])
def get_price():
    """從智能合約中獲取 NFT 的價格"""
    token_id = request.args.get('token_id')

    if not token_id:
        return jsonify({'error': 'Token ID is required'}), 400

    try:
        # 從智能合約中獲取價格
        price = get_nft_price(int(token_id))
        return jsonify({'price': price}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/my_nfts', methods=['GET'])
def my_nfts():
    """顯示用戶的 NFT 收藏"""
    owner_address = request.args.get('owner')  # 從查詢參數獲取持有者地址

    if not owner_address:
        return render_template('error.html', error_message='請提供持有者地址'), 400

    if not Web3.is_address(owner_address):
        return render_template('error.html', error_message='無效的以太坊地址'), 400

    try:
        # 獲取用戶持有的 NFT
        total_supply = contract.functions.totalSupply().call()
        owned_nfts = []

        for token_id in range(total_supply):
            if contract.functions.ownerOf(token_id).call() == Web3.to_checksum_address(owner_address):
                nft_data = contract.functions.nfts(token_id).call()
                token_uri = contract.functions.tokenURI(token_id).call()
                print(f"Token ID {token_id} URI: {token_uri}")  # 調試用
                owned_nfts.append({
                    'id': token_id,
                    'price': Web3.from_wei(nft_data[0], 'ether'),
                    'for_sale': nft_data[1],
                    'uri': token_uri
                })

        return render_template('my_nfts.html', owner=owner_address, nfts=owned_nfts)
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500
if __name__ == "__main__":
    # 啟動 Flask 應用
    app.run(debug=True)