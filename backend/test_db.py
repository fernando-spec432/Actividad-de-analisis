from sqlalchemy import text
from database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM roles;"))
        print("Conexión correcta a PostgreSQL")
        for row in result:
            print(row)
except Exception as e:
    print("Error al conectar con PostgreSQL:")
    print(e)