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
    print('Successfully sent push notification:', response)

if __name__ == "__main__":
    # Example usage
    test_token = "ch_IcC3dbWTtutV0HDXen6:APA91bFQUvcTO6_7MOGSQMX_yIqPCVxh9Qm1RMjoHwC2C3ghN9Vz3cFqPB759qYeVFiIaTEwgyCMevi_jwQXLjpPOdKREFYDadszZEhMA7S-dhYQam6KdSM"
    send_push_notification(test_token, "Notificación API", "Prueba desde local con Python")