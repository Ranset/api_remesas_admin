import firebase_admin
from firebase_admin import messaging, credentials

cred = credentials.Certificate("modulos/testpush.json")
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
    test_token = "fh28WPTfiW3LDGREIKNPKK:APA91bHNKMV5hYTFvx14Wapb7ERmNdBEL7r5a_LqV88vd4BwX3nWxaCFUZV8y1nXr-XmgQK99Pltoj38d9y5UYOfD3fo795-HhOQKkwfxMXAeECBu9teFHY"
    send_push_notification(test_token, "Notificación API", "Prueba desde local con Python")