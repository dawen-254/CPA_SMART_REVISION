import base64
import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MpesaService:
    """Service class for M-Pesa integration."""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.env = settings.MPESA_ENVIRONMENT
        
        if self.env == "sandbox":
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"

    def get_access_token(self):
        """Get access token from Safaricom."""
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        try:
            response = requests.get(
                api_url, 
                auth=(self.consumer_key, self.consumer_secret),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("access_token")
            logger.error(f"M-Pesa Token Error: {response.text}")
        except Exception as e:
            logger.error(f"M-Pesa Token Exception: {str(e)}")
        return None

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate M-Pesa STK Push."""
        access_token = self.get_access_token()
        if not access_token:
            return None, "Failed to get access token"
            
        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode()
        
        # Normalize phone number to 254XXXXXXXXX
        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]
        elif phone_number.startswith("+"):
            phone_number = phone_number[1:]
            
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get("ResponseCode") == "0":
                return res_json, None
            
            logger.error(f"M-Pesa STK Push Error: {response.text}")
            return None, res_json.get("errorMessage", "STK Push failed")
            
        except Exception as e:
            logger.error(f"M-Pesa STK Push Exception: {str(e)}")
            return None, str(e)
