import requests
import json
from google.oauth2 import service_account
import google.auth.transport.requests

def get_fcm_access_token(service_account_file: str) -> str:
    """
    Obtiene un access_token válido para la API HTTP v1 de FCM usando una cuenta de servicio.
    :param service_account_file: Ruta al archivo JSON de la cuenta de servicio de Firebase.
    :return: access_token (str)
    """
    SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    print("Access token:", credentials.token)
    return credentials.token

def send_push_notification_fcm(token: str, title: str, body: str, data: dict = None, server_key: str = ""):
    """
    Envía una notificación push a través de Firebase Cloud Messaging (FCM).
    :param token: Token del dispositivo destino.
    :param title: Título de la notificación.
    :param body: Cuerpo de la notificación.
    :param data: Diccionario de datos adicionales (opcional).
    :param server_key: Clave del servidor FCM.
    :return: Respuesta de FCM.
    """
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body
        },
        "data": data or {}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


def send_push_notification_fcm_v1(token: str, title: str, body: str, data: dict = None, project_id: str = ""):
    """
    Envía una notificación push usando la API HTTP v1 de Firebase Cloud Messaging.
    :param token: Token del dispositivo destino.
    :param title: Título de la notificación.
    :param body: Cuerpo de la notificación.
    :param data: Diccionario de datos adicionales (opcional).
    :param access_token: OAuth2 access token con permisos para FCM.
    :param project_id: ID del proyecto de Firebase.
    :return: Respuesta de FCM.
    """
    access_token = get_fcm_access_token("modulos/remesa-admin-firebase-adminsdk-fbsvc-911952730b.json")

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

if __name__ == "__main__":
    token = "eKtGywUORbOvW3rD9nQG2D:APA91bGJ5eBkrGkHDStqAJC2gl2o7lv5CFGuICvRwBhwtVvMF4w0iHmtcHzRiWGtCj5vHt1L5Kl4sNrcozNeQU6SEEe2HVZFSiK6KZ7w8q2p0ezavwZ-Uu4"
    title = "Notificación API"
    body = "Esta es una notificación desde la api de remesas."
    project_id = "remesa-admin"
    response = send_push_notification_fcm_v1(token, title, body, project_id=project_id)
    print("Response from FCM:", response)