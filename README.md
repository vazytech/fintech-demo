# 💳 Campus Merch Checkout: M-Pesa Daraja API Workshop

Welcome! In this hands-on session, we are building **TechSwag Checkout**—a lightweight Python web application that triggers a real **M-Pesa STK Push (Lipa na M-Pesa Online)** prompt on your phone and listens for Safaricom's live payment confirmation webhook.

---

## 🧠 1. Quick Jargon Buster (Read This First!)

Before writing code, here is what Safaricom's terminology actually means in plain English:

| Term | What It Means |
| :--- | :--- |
| **Daraja API** | Swahili for *"Bridge"*. Safaricom's gateway that lets your code talk to M-Pesa. |
| **STK Push** | *SIM ToolKit Push*. The automatic pop-up on your phone screen asking for your M-Pesa PIN. |
| **Consumer Key & Secret** | Your app's username and password on the Daraja portal. Used to request a temporary login token. |
| **Access Token (OAuth)** | A temporary passkey (valid for 1 hour) that proves to Safaricom your request is authorized. |
| **Shortcode & Passkey** | The Paybill/Till number (`174379` in Sandbox) and a secret string combined with a timestamp to create your request password. |
| **Callback URL (Webhook)** | A public URL where Safaricom sends the final receipt (Success or Cancelled) after the user enters their PIN. |

---

## 🛠️ 2. Prerequisites & Setup

Make sure you have the following installed and ready:
1. **Python 3.8+** and **VS Code**
2. A Safaricom Daraja Sandbox account
3. **Pinggy** for exposing the local callback endpoint

### Configure credentials

Set your Daraja Sandbox credentials in `.env`:

```env
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-sandbox-passkey
MPESA_CALLBACK_URL=https://your-pinggy-url/callback
```

Keep these values private. They are read by the backend and are never sent to
the browser.

### Start the application

Run Flask in the first terminal:

```bash
python app.py
```

The checkout page is available locally at `http://localhost:5000`.

In a second terminal, start Pinggy:

```bash
ssh -p 443 -R0:localhost:5000 a.pinggy.io
```

Pinggy will display a public HTTPS URL, for example:

```text
https://abc123.a.pinggy.link
```

Set `MPESA_CALLBACK_URL` in `.env` to that address followed by `/callback`:

```env
MPESA_CALLBACK_URL=https://abc123.a.pinggy.link/callback
```

Open the Pinggy URL in your browser and submit a Sandbox phone number in the
format `2547XXXXXXXX`. The request flow is:

1. The frontend sends the phone number to Flask at `POST /pay`.
2. Flask requests an access token and sends the STK Push request to Safaricom.
3. Safaricom sends the payment result to the Pinggy callback URL.
4. Pinggy forwards the result to Flask at `POST /callback`.

Keep both Flask and Pinggy running while testing. A new Pinggy URL may be
generated after restarting Pinggy, so update `CALLBACK_URL` when that happens.
