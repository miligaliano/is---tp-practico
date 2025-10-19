import customtkinter as ctk
from datetime import date
from calendar import monthrange
from parque_aventura import Usuario, Compra, ConfiguracionParque


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ComprarEntradasUI(ctk.CTk):
    def __init__(self, usuario_logueado: Usuario):
        super().__init__()
        self.usuario_logueado = usuario_logueado

        self.title("🎟️ Compra de Entradas - EcoHarmony Park")
        self.geometry("600x600")

        ctk.CTkLabel(self, text=f"Bienvenido, {self.usuario_logueado.email}", font=(
            "Arial", 16)).pack(pady=10)

        ctk.CTkLabel(self, text="Seleccione la fecha de visita:").pack(
            pady=(10, 5))
        self.fecha_frame = ctk.CTkFrame(self)
        self.fecha_frame.pack()
        today = date.today()
        self.anio_var = ctk.StringVar(value=str(today.year))
        self.mes_var = ctk.StringVar(value=str(today.month))
        self.dia_var = ctk.StringVar(value=str(today.day))
        self.om_anio = ctk.CTkOptionMenu(self.fecha_frame, variable=self.anio_var, values=[
                                         str(today.year), str(today.year + 1)], command=self.actualizar_dias)
        self.om_mes = ctk.CTkOptionMenu(self.fecha_frame, variable=self.mes_var, values=[
                                        str(m) for m in range(1, 13)], command=self.actualizar_dias)
        self.om_dia = ctk.CTkOptionMenu(
            self.fecha_frame, variable=self.dia_var, command=self.actualizar_dias)
        self.om_anio.grid(row=0, column=0, padx=5, pady=5)
        self.om_mes.grid(row=0, column=1, padx=5, pady=5)
        self.om_dia.grid(row=0, column=2, padx=5, pady=5)
        self.label_feedback_fecha = ctk.CTkLabel(
            self, text="", font=("Arial", 12))
        self.label_feedback_fecha.pack(pady=(5, 10))

        ctk.CTkLabel(self, text="Cantidad de entradas:").pack(pady=(15, 5))
        self.cantidad_frame = ctk.CTkFrame(self)
        self.cantidad_frame.pack()

        self.cantidad_var = ctk.StringVar(value="2")

        self.btn_menos = ctk.CTkButton(
            self.cantidad_frame, text="-", width=40, command=lambda: self.ajustar_cantidad(-1))
        self.btn_menos.grid(row=0, column=0, padx=(0, 5))

        self.entry_cantidad = ctk.CTkEntry(
            self.cantidad_frame, textvariable=self.cantidad_var, width=60, justify="center")
        self.entry_cantidad.grid(row=0, column=1)

        self.btn_mas = ctk.CTkButton(
            self.cantidad_frame, text="+", width=40, command=lambda: self.ajustar_cantidad(1))
        self.btn_mas.grid(row=0, column=2, padx=(5, 0))

        ctk.CTkLabel(self, text="Tipo de pase:").pack(pady=(15, 5))
        self.tipo_pase = ctk.CTkOptionMenu(self, values=["regular", "VIP"])
        self.tipo_pase.set("regular")
        self.tipo_pase.pack()

        ctk.CTkLabel(self, text="Forma de pago:").pack(pady=5)
        self.forma_pago = ctk.CTkOptionMenu(
            self, values=["efectivo", "tarjeta"])
        self.forma_pago.set("efectivo")
        self.forma_pago.pack()

        self.btn_comprar = ctk.CTkButton(
            self, text="Comprar entradas", command=self.realizar_compra)
        self.btn_comprar.pack(pady=20)

        self.text_resultado = ctk.CTkTextbox(self, width=500, height=120)
        self.text_resultado.pack(pady=10)

        self.actualizar_dias()

    def ajustar_cantidad(self, cambio):
        """Ajusta la cantidad de entradas, respetando los límites."""
        try:
            cantidad_actual = int(self.cantidad_var.get())
            nueva_cantidad = cantidad_actual + cambio

            min_entradas = ConfiguracionParque.CANTIDAD_MIN_ENTRADAS
            max_entradas = ConfiguracionParque.CANTIDAD_MAX_ENTRADAS

            if min_entradas <= nueva_cantidad <= max_entradas:
                self.cantidad_var.set(str(nueva_cantidad))
        except ValueError:
            self.cantidad_var.set(
                str(ConfiguracionParque.CANTIDAD_MIN_ENTRADAS))

    def actualizar_dias(self, *args):
        """Actualiza el menú de días y proporciona feedback visual sobre la fecha."""
        try:
            year = int(self.anio_var.get())
            month = int(self.mes_var.get())

            _, num_dias = monthrange(year, month)
            dias_disponibles = [str(d) for d in range(1, num_dias + 1)]
            self.om_dia.configure(values=dias_disponibles)

            if int(self.dia_var.get()) > num_dias:
                self.dia_var.set(str(num_dias))

            fecha_seleccionada = date(year, month, int(self.dia_var.get()))

            if fecha_seleccionada < date.today():
                self.label_feedback_fecha.configure(
                    text="⚠️ La fecha no puede ser anterior a hoy.", text_color="red")
            elif fecha_seleccionada.weekday() not in ConfiguracionParque.DIAS_ABIERTOS:
                self.label_feedback_fecha.configure(
                    text="🚫 El parque está cerrado ese día.", text_color="orange")
            else:
                self.label_feedback_fecha.configure(
                    text="✅ Fecha de visita válida.", text_color="green")

        except (ValueError, TypeError):
            self.label_feedback_fecha.configure(text="")

    def realizar_compra(self):
        """Obtiene los datos de la UI, crea los objetos y procesa la compra."""
        try:
            fecha_visita = date(
                int(self.anio_var.get()),
                int(self.mes_var.get()),
                int(self.dia_var.get())
            )
            cantidad = int(self.cantidad_var.get())
        except ValueError:
            self.text_resultado.delete("1.0", "end")
            self.text_resultado.insert(
                "end", "⚠️ Datos inválidos. Por favor, revise su selección.")
            return

        edades = [25] * cantidad
        tipo = self.tipo_pase.get()
        forma = self.forma_pago.get()

        compra = Compra(self.usuario_logueado, fecha_visita,
                        cantidad, edades, tipo, forma)
        resultado = compra.procesar()

        self.text_resultado.delete("1.0", "end")
        self.text_resultado.insert("end", resultado["mensaje"])


if __name__ == "__main__":
    email_del_usuario_en_sesion = "usuario@registrado.com"
    usuario_actual = Usuario.desde_la_sesion(email_del_usuario_en_sesion)

    if not usuario_actual.registrado:
        print(
            f"Error: El usuario {email_del_usuario_en_sesion} no se encontró en la base de datos.")
    else:
        app = ComprarEntradasUI(usuario_logueado=usuario_actual)
        app.mainloop()
