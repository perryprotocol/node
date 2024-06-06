from flask import Flask, jsonify, request
from flask_cors import CORS
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.rpc.responses import GetBalanceResp
import qrcode
import pymongo
from PIL import Image
import base64
import io,os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Solana client
solana_client = Client("https://api.devnet.solana.com")

# Initialize MongoDB client
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URI"))

db = mongo_client["wallet_db"]
collection = db["wallets"]

@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    keypair = Keypair()
    public_key = keypair.pubkey()
    private_key = keypair.secret()

    print("Public Key:", public_key)
    print("Private Key:", private_key.hex())

    collection.insert_one({"public_key": str(public_key), "private_key": private_key.hex()})

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(public_key))
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    balance_response = solana_client.get_balance(public_key)
    balance = balance_response.value if isinstance(balance_response, GetBalanceResp) else 0

    return jsonify({
        "public_key": str(public_key),
        "qr_code": img_str,
        "balance": balance
    })

if __name__ == "__main__":
    app.run()
