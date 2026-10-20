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
1. **Python 3.8+** & **VS Code**
2. A# fintech-demo
