import sqlite3
from database import obtener_conexion, crear_tabla_usuarios


def inicializar_bd():
    """Crea la tabla y añade usuarios de ejemplo con contraseñas hasheadas."""
    crear_tabla_usuarios()

    usuarios_ejemplo = [
        ("usuario@registrado.com", "Juan Perez",
         "pbkdf2:sha256:150000$aBcDeFg$123..."),
        ("otro@usuario.com", "Ana Lopez", "pbkdf2:sha256:150000$hIjKlMn$456..."),
        ("miligaliano@gmail.com", "Mili Galiano",
         "pbkdf2:sha256:150000$aBcDeFg$123...")
    ]
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()

            cursor.executemany(
                "INSERT OR IGNORE INTO usuarios (email, nombre, password_hash) VALUES (?, ?, ?)", usuarios_ejemplo)
            conn.commit()
            print("Base de datos inicializada correctamente.")
            print(f"Usuarios de ejemplo añadidos con contraseñas hasheadas.")
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")


if __name__ == "__main__":
    # Si ya tienes una base de datos, puedes borrar el archivo parque_aventura.db
    # antes de ejecutar este script para recrearla con la nueva estructura.
    inicializar_bd()
