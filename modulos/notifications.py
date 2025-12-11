import firebase_admin
from firebase_admin import messaging, credentials

cred = credentials.Certificate("modulos/remesa-admin-firebase-adminsdk-fbsvc-5b120ea7c6.json")
firebase_admin.initialize_app(cred)

def send_push_notification(token: str, title: str, body: str):
    """Sends a push notification to a device using Firebase Cloud Messaging."""

    try:
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
        return ('Successfully sent push notification:', response)

    except Exception as e:
        print('Error sending push notification:', e)
        return ('Error sending push notification:', str(e))

if __name__ == "__main__":
    # Example usage
    test_token = "eKtGywUORbOvW3rD9nQG2D:APA91bEPG26Q4EWtM3tJmz_4mDmsd2y1GoOABnyu1JmwyufDRAeuZMXTtoiEcZxSU2I54eC5k4v4r5K5FBjlm_FU_y9vKGyPV-_Mrc7TWskJOBIeCcCvxQg"
    send_push_notification(test_token, "Notificación API", "Prueba desde local con Python")