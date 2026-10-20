import os
import base64
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- 1. CONFIGURATION (Sandbox Defaults) ---
CONSUMER_KEY = os.getenv("Xh2mV3wgH59DNmQjJZHRvqDTb2Ho4vOLZzl1GPErOXXK1ORO", "YOUR_SANDBOX_KEY")
CONSUMER_SECRET = os.getenv("QRgpRkZciSEpFZToV23TBJAdhpz12TG4SwJ8GKbo8AoIqONEZkzzvGT7IZ43QdGt", "YOUR_SANDBOX_SECRET")
SHORTCODE = "174379"  # Standard Daraja Sandbox Shortcode
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" # Standard Sandbox Passkey
CALLBACK_URL = "https://elvxb-102-0-31-118.run.pinggy-free.link/" # Replace with live ngrok URL


# --- HELPER: STEP 1 - GET OAUTH ACCESS TOKEN ---
def get_access_token():
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")


# --- ROUTE 1: THE MINI WEBSITE (FRONTEND) ---
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Campus Merch Checkout</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center; padding-top: 60px; background: #f4f4f9; }
            .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 320px; }
            input, button { width: 100%; padding: 10px; margin-top: 10px; box-sizing: border-box; border-radius: 6px; border: 1px solid #ccc; }
            button { background: #2e7d32; color: white; border: none; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h3>Dev Hoodie - KES 1</h3>
            <form action="/pay" method="POST">
                <label>M-Pesa Number (2547...):</label>
                <input type="text" name="phone" placeholder="254712345678" required />
                <button type="submit">Pay with M-Pesa</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


# --- ROUTE 2: STEP 2 - TRIGGER THE STK PUSH ---
@app.route("/pay", methods=["POST"])
def initiate_stk_push():
    phone = request.form.get("phone")
    
    # 1. Generate Timestamp (YYYYMMDDHHmmss) & Base64 Password
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_password = SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(raw_password.encode()).decode("utf-8")

    # 2. Fetch Token
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Build STK Push Payload
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phone,            # Number sending money
        "PartyB": SHORTCODE,        # Organization receiving money
        "PhoneNumber": phone,       # Number to receive the STK pop-up
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "GDGMerch",
        "TransactionDesc": "Hoodie Purchase"
    }

    response = requests.post(stk_url, json=payload, headers=headers)
    return jsonify(response.json())


# --- ROUTE 3: STEP 3 - RECEIVE SAFARICOM'S CALLBACK ---
@app.route("/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()
    print("\n--- M-PESA CALLBACK RECEIVED ---")
    print(data)
    
    # Extract ResultCode (0 = Success, anything else = Cancelled/Failed)
    stk_callback = data.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")
    
    print(f"Status: {result_code} - {result_desc}\n")
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)