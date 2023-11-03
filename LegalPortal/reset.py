from django.db import connection

with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE your_model_id_seq RESTART WITH 1;")