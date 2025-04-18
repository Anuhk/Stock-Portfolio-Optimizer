
import mysql.connector 
from django.conf import settings

def get_db_connection():
    return mysql.connector.connect(
        host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        database=settings.DATABASES['default']['NAME'],
        port=settings.DATABASES['default'].get('PORT', '3306')
    )