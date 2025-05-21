// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIds; // 用於追蹤已鑄造的 NFT 數量

    struct NFT {
        uint256 price;
        bool forSale;
    }

    mapping(uint256 => NFT) public nfts;

    constructor() ERC721("MyNFT", "MNFT") {}

    function mintNFT(address recipient, string memory tokenURI, uint256 price) public onlyOwner returns (uint256) {
        require(price > 0, "Price must be greater than zero");

        uint256 newItemId = _tokenIds;
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);

        // 手動觸發 Transfer 事件
        emit Transfer(address(0), recipient, newItemId);

        nfts[newItemId] = NFT(price, false);
        _tokenIds++;

        return newItemId;
    }

    function totalSupply() public view returns (uint256) {
        return _tokenIds;
    }
    function setForSale(uint256 tokenId, uint256 price) public {
        require(ownerOf(tokenId) == msg.sender, "You are not the owner");
        require(price > 0, "Price must be greater than zero");

        nfts[tokenId].price = price;
        nfts[tokenId].forSale = true;
    }

    function getPrice(uint256 tokenId) public view returns (uint256) {
        require(_exists(tokenId), "Token ID does not exist");
        return nfts[tokenId].price;
    }
    function buyNFT(uint256 tokenId) public payable {
        require(nfts[tokenId].forSale, "This NFT is not for sale");
        require(msg.value >= nfts[tokenId].price, "Insufficient funds");

        address seller = ownerOf(tokenId);
        require(seller != msg.sender, "You cannot buy your own NFT");

        nfts[tokenId].forSale = false;

        _transfer(seller, msg.sender, tokenId);

        payable(seller).transfer(nfts[tokenId].price);

        if (msg.value > nfts[tokenId].price) {
            payable(msg.sender).transfer(msg.value - nfts[tokenId].price);
        }
    }
}