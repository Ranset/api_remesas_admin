import firebase_admin
from firebase_admin import messaging, credentials
import os
from dotenv import load_dotenv

load_dotenv()

service_acount_info = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
}

cred = credentials.Certificate(service_acount_info)
firebase_admin.initialize_app(cred)

def send_push_notification(token: str, title: str, body: str, data: dict = None):
    """Sends a push notification to a device using Firebase Cloud Messaging."""

    try:
        message = messaging.Message(
            notification= messaging.Notification(
                title= title,
                body= body
            ),
            data= data,
            token= token
        )

        response = messaging.send(message)
        return ('Successfully sent push notification:', response)

    except Exception as e:
        print('Error sending push notification:', e)
        return ('Error sending push notification:', str(e))

if __name__ == "__main__":
    # Example usage
    test_token = "cf9-eV1j1vbytAy25Z16Oo:APA91bFMHi3Gl4WejglV9fNKIbYflTy_uMTDZj51KiXb32aUX1S5X53wIuziemUCbuvr3d-2IE1NMfVjhwcVY0uEkkIGYDuRohTKWKJN8sG7ucX4VZ31cpA"
    send_push_notification(test_token, "Notificación API", "Prueba desde local con Python", data={"key1": "value1", "key2": "value2"})