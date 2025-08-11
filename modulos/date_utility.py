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