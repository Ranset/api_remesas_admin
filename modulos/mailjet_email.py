import os
from dotenv import load_dotenv

class MailjetEmail:
    def __init__(self):
        load_dotenv()

        self.api_key = os.environ.get('MJ_APIKEY_PUBLIC')
        self.api_secret = os.environ.get('MJ_APIKEY_PRIVATE')
        self.sender_mail = "remesas.aplication@gmail.com"

    def send_email_verify(self, code, client_email, client_name):
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

        if not self.api_key or not self.api_secret:
            raise RuntimeError("Faltan variables de entorno MJ_APIKEY_PUBLIC/MJ_APIKEY_PRIVATE")

        mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender_mail, 
                        "Name": "Remesas Admin"
                        },
                    "To": [
                        {
                            "Email": f"{client_email}", 
                            "Name": f"{client_name}"
                        }
                        ],
                    "Subject": "Registro en Remesas Admin - Verificación de correo",
                    "TextPart": "Gracias por registrarte en Remesas Admin. Por favor, verifica tu correo con el siguiente código en la aplicación: " + code,
                    "HTMLPart": f'<h4>&iexcl;Hola!</h4> <p>Gracias por registrarte en Remesas Admin. Por favor, <span class="il">verifica</span> tu correo con el siguiente c&oacute;digo en la aplicaci&oacute;n:</p><h1 style="text-align: center;"><strong>{code}</strong></h1><p>Si usted no ha solicitado crearse una cuenta, ignore este correo.</p><p>Saludos,<br />Equipo de Remesas Admin</p>'
                }
            ]
        }
        result = mailjet.send.create(data=data)
        print(result.status_code)
        print(result.json())

    def send_email_welcome(self, client_email, client_name):
        """
        This call sends a welcome message to one recipient.
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

        if not self.api_key or not self.api_secret:
            raise RuntimeError("Faltan variables de entorno MJ_APIKEY_PUBLIC/MJ_APIKEY_PRIVATE")

        mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender_mail, 
                        "Name": "Remesas Admin"
                        },
                    "To": [
                        {
                            "Email": f"{client_email}", 
                            "Name": f"{client_name}"
                        }
                        ],
                    "Subject": "Bienvenido a Remesas Admin",
                    "TextPart": "Gracias por crear una cuenta en Remesas. Ya tu correo ha sido confirmado y tu usuario activado.",
                    "HTMLPart": f'''<table id="m_6254617341495231568template_container" style="width: 100.411%;" border="0" width="100%" cellspacing="0" cellpadding="0" bgcolor="#fff">
                        <tbody>
                        <tr>
                        <td style="width: 100%;" align="center" valign="top">
                        <table id="m_6254617341495231568template_header" border="0" width="100%" cellspacing="0" cellpadding="0" bgcolor="#fff">
                        <tbody>
                        <tr>
                        <td id="m_6254617341495231568header_wrapper">
                        <h1>Bienvenido a Remesas Aadmin</h1>
                        </td>
                        </tr>
                        </tbody>
                        </table>
                        </td>
                        </tr>
                        <tr>
                        <td style="width: 100%;" align="center" valign="top">
                        <table id="m_6254617341495231568template_body" border="0" width="100%" cellspacing="0" cellpadding="0">
                        <tbody>
                        <tr>
                        <td id="m_6254617341495231568body_content" valign="top" bgcolor="#fff">
                        <table border="0" width="100%" cellspacing="0" cellpadding="20">
                        <tbody>
                        <tr>
                        <td id="m_6254617341495231568body_content_inner_cell" valign="top">
                        <div id="m_6254617341495231568body_content_inner" align="left">
                        <div>
                        <p>Hola {client_name},</p>
                        <p>Gracias por crear una cuenta en Remesas Admin. Ya tu correo ha sido confirmado y tu usuario activado.</p>
                        <p>Puedes acceder a tu &aacute;rea de usuario en la aplicaci&oacute;n.</p>
                        <p>&nbsp;</p>
                        <p>Equipo de</p>
                        <p><strong>Remesas Admin</strong></p>
                        </div>
                        </div>
                        </td>
                        </tr>
                        </tbody>
                        </table>
                        </td>
                        </tr>
                        </tbody>
                        </table>
                        </td>
                        </tr>
                        </tbody>
                        </table>'''
                }
            ]
        }
        result = mailjet.send.create(data=data)
        print(result.status_code)


    def send_email_password_reset(self, code,client_email, client_name):
        """
        This call sends a welcome message to one recipient.
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

        if not self.api_key or not self.api_secret:
            raise RuntimeError("Faltan variables de entorno MJ_APIKEY_PUBLIC/MJ_APIKEY_PRIVATE")

        mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender_mail, 
                        "Name": "Remesas Admin"
                        },
                    "To": [
                        {
                            "Email": f"{client_email}", 
                            "Name": f"{client_name}"
                        }
                        ],
                    "Subject": "Restablezca su contraseña",
                    "TextPart": "Gracias por crear una cuenta en Remesas. Ya tu correo ha sido confirmado y tu usuario activado.",
                    "HTMLPart": f'''<p>Estimado/a {client_name},</p>
                                    <p>Hemos recibido una solicitud para restablecer la contrase&ntilde;a de su cuenta de Remesas Admin.</p>
                                    <p>Por favor, introduzca el siguiente c&oacute;digo en su aplicaci&oacute;n.</p>
                                    <h1 style="text-align: center;"><strong>{code}</strong></h1>
                                    <p>Si no solicit&oacute; el restablecimiento de contrase&ntilde;a, puede ignorar este correo.</p>
                                    <p>Por motivos de seguridad, este c&oacute;digo expirar&aacute; en 24 horas.</p>
                                    <p>Atentamente,</p>
                                    <p>El equipo de Remesas Admin</p>'''
                }
            ]
        }
        result = mailjet.send.create(data=data)
        print(result.status_code)

    def send_email_new_password(self, client_email, client_name):
        """
        This call sends a welcome message to one recipient.
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

        if not self.api_key or not self.api_secret:
            raise RuntimeError("Faltan variables de entorno MJ_APIKEY_PUBLIC/MJ_APIKEY_PRIVATE")

        mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.sender_mail, 
                        "Name": "Remesas Admin"
                        },
                    "To": [
                        {
                            "Email": f"{client_email}", 
                            "Name": f"{client_name}"
                        }
                        ],
                    "Subject": "Contraseña restablecida",
                    "TextPart": "Gracias por crear una cuenta en Remesas. Ya tu correo ha sido confirmado y tu usuario activado.",
                    "HTMLPart": f'''<p>Estimado {client_name}</p>
                                    <p>Su contrase&ntilde;a ha sido restablecida satisfactoriamente.</p>
                                    <p>Ahora puede acceder a la aplicaci&oacute;n con sus nuevas credenciales.</p>
                                    <p>Equipo de Remesas Admin.</p>'''
                }
            ]
        }

        result = mailjet.send.create(data=data)
        print(result.status_code)