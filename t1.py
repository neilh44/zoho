from dotenv import load_dotenv
import os
from zohocrmsdk.src.com.zoho.api.authenticator.oauth_token import OAuthToken
from zohocrmsdk.src.com.zoho.crm.api.initializer import Initializer
from zohocrmsdk.src.com.zoho.crm.api.dc import INDataCenter
from zohocrmsdk.src.com.zoho.crm.api.sdk_config import SDKConfig

def initialize_zoho():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from .env file
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    # Create an instance of Token
    token = OAuthToken(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token
    )

    # Create an instance of SDKConfig
    sdk_config = SDKConfig(
        auto_refresh_fields=True,
        pick_list_validation=False
    )

    # The path containing the absolute directory path to store user specific JSON files
    resource_path = os.path.join(os.getcwd(), 'resources')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(resource_path):
        os.makedirs(resource_path)

    # Initialize the SDK
    try:
        Initializer.initialize(
            environment=INDataCenter.PRODUCTION(),
            token=token,
            sdk_config=sdk_config,
            resource_path=resource_path
        )
        print("Zoho CRM SDK initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing Zoho CRM SDK: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_zoho()