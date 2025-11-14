import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('MJ_APIKEY_PUBLIC')
api_secret = os.environ.get('MJ_APIKEY_PRIVATE')

print("Api Key:", api_secret)

def send_email():
    """
    This call sends a message to one recipient.
    """
    try:
        from mailjet_rest import Client
    except Exception as e:
        raise ImportError(
            "No se pudo importar mailjet_rest.Client. "
            "Verifica que el paquete 'mailjet-rest' esté instalado y que no haya "
            "archivos locales llamados 'mailjet_rest.py' que provoquen conflicto. "
            f"Import error: {e}"
        )

    if not api_key or not api_secret:
        raise RuntimeError("Faltan variables de entorno MJ_APIKEY_PUBLIC/MJ_APIKEY_PRIVATE")

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ransetfleites0@gmail.com", 
                    "Name": "Ranset"
                    },
                "To": [
                    {
                        "Email": "ranset1983@gmail.com", 
                        "Name": "Client 1"
                    }
                    ],
                "Subject": "Your email flight plan!",
                "TextPart": "Dear Client 1, welcome to Mailjet! May the delivery force be with you!",
                "HTMLPart": "<h3>Dear Client 1, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!</h3><br />May the delivery force be with you!"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())

if __name__ == "__main__":
    send_email()