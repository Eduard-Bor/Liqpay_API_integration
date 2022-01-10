from dotenv import load_dotenv
import os

load_dotenv()

public_key = os.getenv('liqpay_public_key')
private_key = os.getenv('liqpay_private_key')