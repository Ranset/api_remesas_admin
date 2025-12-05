from datetime import datetime
import random

class DateUtlility:
    def __init__(self):
        pass

    def translate_month(self, month: str) -> str:
        """Translates a month name from English to Spanish."""
        months = {
            "January": "Enero",
            "February": "Febrero",
            "March": "Marzo",
            "April": "Abril",
            "May": "Mayo",
            "June": "Junio",
            "July": "Julio",
            "August": "Agosto",
            "September": "Septiembre",
            "October": "Octubre",
            "November": "Noviembre",
            "December": "Diciembre"
        }
        return months.get(month, month)
    
    def generar_codigo(self):
        """Generates a unique code based on the current 
        date and time plus 4 random digits at the end."""
        
        # Fecha y hora actual en formato YYYYMMDDHHMMSS
        fecha_hora = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Cuatro dígitos aleatorios
        aleatorio = f"{random.randint(0, 9999):04d}"
        
        # Concatenar todo
        return fecha_hora + aleatorio