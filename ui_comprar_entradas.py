"""
Wrapper para la UI. Todas las clases y lógica están en `parque_aventura.py`.
Este archivo sólo expone una entrada para ejecución directa.
"""

from parque_aventura import Usuario, ComprarEntradasUI


if __name__ == "__main__":
    email_del_usuario_en_sesion = "miligaliano@gmail.com"
    usuario_actual = Usuario.desde_la_sesion(email_del_usuario_en_sesion)

    if not usuario_actual.registrado:
        print(f"Error: El usuario {email_del_usuario_en_sesion} no se encontró en la base de datos.")
    else:
        app = ComprarEntradasUI(usuario_logueado=usuario_actual)
        app.mainloop()