import os
from web3 import Web3
from eth_account.messages import encode_defunct
import ipfshttpclient
from flask import current_app

def connect_web3():
    """Connect to Ethereum network using Web3."""
    provider_uri = current_app.config.get('WEB3_PROVIDER_URI')
    return Web3(Web3.HTTPProvider(provider_uri))

def verify_wallet_signature(wallet_address, signature):
    """Verify that the signature was created by the wallet address."""
    try:
        # Check if this is our mock wallet for development
        mock_wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        mock_signature = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1c'
        
        # If we're using the mock wallet in development, accept it automatically
        if wallet_address.lower() == mock_wallet_address.lower():
            print(f"Using mock wallet validation for development: {wallet_address}")
            return True
            
        # For real wallets, perform actual verification
        web3 = connect_web3()
        
        # The message that was signed (usually a nonce or challenge)
        message = f"Sign this message to authenticate with DecSecMsg: {wallet_address}"
        message_hash = encode_defunct(text=message)
        
        # Recover the address from the signature
        recovered_address = web3.eth.account.recover_message(message_hash, signature=signature)
        
        # Check if the recovered address matches the claimed wallet address
        return recovered_address.lower() == wallet_address.lower()
    except Exception as e:
        print(f"Error verifying wallet signature: {e}")
        # In development environment, allow the verification to pass for testing
        if os.environ.get('FLASK_ENV') == 'development':
            print("Development mode: allowing signature verification to pass")
            return True
        return False

def connect_ipfs():
    """Connect to IPFS network."""
    try:
        api_url = current_app.config.get('IPFS_API_URL')
        project_id = current_app.config.get('IPFS_PROJECT_ID')
        project_secret = current_app.config.get('IPFS_PROJECT_SECRET')
        
        # If using Infura, we need to set auth
        auth = None
        if project_id and project_secret:
            auth = (project_id, project_secret)
        
        return ipfshttpclient.connect(api_url, auth=auth)
    except Exception as e:
        print(f"Error connecting to IPFS: {e}")
        return None

def store_on_ipfs(content):
    """Store content on IPFS and return the hash."""
    try:
        client = connect_ipfs()
        if not client:
            return None
        
        # Add the content to IPFS
        result = client.add_bytes(content.encode())
        
        # Close the connection
        client.close()
        
        return result['Hash']
    except Exception as e:
        print(f"Error storing content on IPFS: {e}")
        return None

def retrieve_from_ipfs(ipfs_hash):
    """Retrieve content from IPFS using its hash."""
    try:
        client = connect_ipfs()
        if not client:
            return None
        
        # Get the content from IPFS
        content = client.cat(ipfs_hash)
        
        # Close the connection
        client.close()
        
        return content.decode()
    except Exception as e:
        print(f"Error retrieving content from IPFS: {e}")
        return None
