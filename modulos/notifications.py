import firebase_admin
from firebase_admin import messaging, credentials

cred = credentials.Certificate("modulos/remesa-admin-firebase-adminsdk-fbsvc-911952730b.json")
firebase_admin.initialize_app(cred)

def send_push_notification(token: str, title: str, body: str):
    """Sends a push notification to a device using Firebase Cloud Messaging."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data={
            'clave1': 'valor1',
            'clave2': 'valor2'
        },
        token=token
    )

    response = messaging.send(message)
    print('Successfully sent message:', response)

if __name__ == "__main__":
    # Example usage
    test_token = "eKtGywUORbOvW3rD9nQG2D:APA91bGJ5eBkrGkHDStqAJC2gl2o7lv5CFGuICvRwBhwtVvMF4w0iHmtcHzRiWGtCj5vHt1L5Kl4sNrcozNeQU6SEEe2HVZFSiK6KZ7w8q2p0ezavwZ-Uu4"
    send_push_notification(test_token, "Notificación API", "Esta es una notificación desde la api de remesas.")