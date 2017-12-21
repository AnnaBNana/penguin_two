"""
WSGI config for penguin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# My penguin API keys

os.environ["PENGUIN_S3_REGION"] = "us-west-1"
os.environ["PENGUIN_S3_KEY"] = "AKIAJKFPQ3FSCU2QAMDA"
os.environ["PENGUIN_S3_SECRET"] = "yjdWMcDocxK+jo3GrKpFIUfgNP42DoksAJZC1TxK"
os.environ["PENGUIN_S3_BUCKET"] = "penguinimages"
# all test api keys below, replace in production
#stripe
os.environ["TEST_SECRET_KEY"] = "sk_test_INk1P29HIHmug01mGlpGSWur"
os.environ["TEST_PUBLISHABLE_KEY"] = "pk_test_vDG4jh3tyP2w3gPw30eupWR2"
os.environ["PENGUIN_EASYPOST_KEY"] = "oHu9Gag6DkUFfzQEZ0baQA"
os.environ["PENGUIN_PAYPAL_ID"] = "AeCoyZ5UE9IIRs60YxlTHGP06ULpgj_XnoaZoNyVudpoED5_RmLeKlBYvDko3pvyXeKqXU78a2cGn2Ux"
os.environ["PENGUIN_PAYPAL_SECRET"] = "EPTdsKFmDBJZkZCN_ZKhXQcelTx6GRseUmlaZvPH-DnJEnox85CRV02mqw7g0miiYl4s1EUNHbw0P0BR"
os.environ["PENGUIN_MAILGUN_PUBLIC"] = "pubkey-7f1899afe4683d86ba6180c60c249fc6"
os.environ["PENGUIN_MAILGUN_PRIVATE"] = "key-7ca89f8f619f3286b7ec93cf2561237e"
# production keys
os.environ["PENGUIN_EASYPOST_PRODUCTION"] = "RO8WzSy82nLSj40aYQr95g"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguin.settings")

application = get_wsgi_application()
