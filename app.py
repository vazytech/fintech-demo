import os
import base64
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- 1. CONFIGURATION (Sandbox) ---
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "YOUR_SANDBOX_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "YOUR_SANDBOX_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
PASSKEY = os.getenv("MPESA_PASSKEY", "")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://cyyty-102-0-31-118.run.pinggy-       
│free.link")


# --- HELPER: STEP 1 - GET OAUTH ACCESS TOKEN ---
def get_access_token():
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")


# --- ROUTE 1: SERVE THE FRONTEND ---
@app.route("/")
def index():
    return render_template("index.html")


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