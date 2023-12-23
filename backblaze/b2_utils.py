from b2sdk.v1 import B2Api, InMemoryAccountInfo
import os


# Initialize B2 API

def initialize_b2api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    application_key_id = os.getenv('APPLICATION_KEY_ID')
    application_key = os.getenv('APPLICATION_KEY')
    b2_api.authorize_account(
        "production", application_key_id, application_key)
    return b2_api


# def get_bucket(b2_api):
#     bucket_name = os.getenv('BUCKET_NAME')
#     bucket = b2_api.get_bucket_by_name(bucket_name)
#     return bucket
