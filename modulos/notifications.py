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
    test_token = "dj4BHCYCTJiLnUgyEsI_px:APA91bGBZaHNynVkDxfS0pkxl-dhjK__3rtDwvTDuPi5gfalZis-JcN6O6u23ssasO5V1Y8v7I9VraKJHfMsmGZ4oZIAQh2BGBO5GK_kOzZRNbdvJPp5GKY"
    send_push_notification(test_token, "Notificación API", "Avísame si te llega esta notificación.")