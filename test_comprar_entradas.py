import pytest
from datetime import date, timedelta
from parque_aventura import Usuario, Compra

# Se simula un usuario con sesión iniciada y registrado


@pytest.fixture
def usuario_registrado():
    """Fixture que simula un objeto de usuario registrado y logueado."""
    return Usuario("usuario@registrado.com", registrado=True)


@pytest.fixture
def usuario_no_registrado():
    """Fixture que simula un objeto de usuario no registrado."""
    return Usuario("nadie@dominio.com", registrado=False)


# ------------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------------

def test_compra_exitosa_tarjeta(usuario_registrado):
    """Compra válida con tarjeta (Mercado Pago)"""
    fecha = date.today() + timedelta(days=3)  # Una fecha futura válida
    compra = Compra(usuario_registrado, fecha, 2, [
                    25, 30], "regular", "tarjeta")
    resultado = compra.procesar()
    assert resultado["ok"] is True
    assert "Mercado Pago" in resultado["mensaje"]


def test_compra_sin_forma_pago(usuario_registrado):
    """Falla sin forma de pago"""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 2, [25, 30], "VIP", None)
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "forma de pago" in resultado["mensaje"]


def test_compra_fecha_cerrado(usuario_registrado):
    """Falla si el parque está cerrado (domingo)"""
    hoy = date.today()
    # Calculamos cuántos días faltan para el próximo domingo (weekday() == 6)
    dias_hasta_domingo = (6 - hoy.weekday() + 7) % 7
    fecha_cerrado = hoy + timedelta(days=dias_hasta_domingo)

    compra = Compra(usuario_registrado, fecha_cerrado,
                    2, [25, 30], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "parque está cerrado" in resultado["mensaje"]


def test_compra_mas_de_10_entradas(usuario_registrado):
    """Falla si se piden más de 10 entradas"""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 11,
                    [20]*11, "regular", "tarjeta")
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "Cantidad de entradas inválida" in resultado["mensaje"]

# ------------------------------------------------------------------------
# TESTS INFERIDOS
# ------------------------------------------------------------------------


def test_compra_usuario_no_registrado(usuario_no_registrado):
    """Solo usuarios registrados pueden comprar"""
    fecha = date.today() + timedelta(days=1)
    compra = Compra(usuario_no_registrado, fecha, 2,
                    [25, 30], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "no está registrado" in resultado["mensaje"]


def test_compra_sin_edades(usuario_registrado):
    """Se deben indicar las edades"""
    fecha = date.today() + timedelta(days=1)
    compra = Compra(usuario_registrado, fecha, 3, [],
                    "regular", "tarjeta")  # Lista de edades vacía
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "edad de cada visitante" in resultado["mensaje"]


def test_compra_pago_efectivo(usuario_registrado):
    """Pago en boletería válido"""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 2, [
                    18, 22], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is True
    assert "Pago en boletería" in resultado["mensaje"]


def test_compra_tipo_vip(usuario_registrado):
    """Pase VIP válido"""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 2, [18, 22], "VIP", "tarjeta")
    resultado = compra.procesar()
    monto_esperado = 2 * 15000  # 2 entradas VIP
    assert resultado["ok"] is True
    assert "Mercado Pago" in resultado["mensaje"]
    assert str(int(monto_esperado)) in resultado["mensaje"]


def test_compra_fecha_futura_valida(usuario_registrado):
    """✅ FALTANTE: Fecha futura válida"""
    fecha_futura = date.today() + timedelta(days=10)
    # Nos aseguramos de que la fecha no caiga en domingo
    if fecha_futura.weekday() == 6:
        fecha_futura += timedelta(days=1)

    compra = Compra(usuario_registrado, fecha_futura,
                    1, [30], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is True
    assert "Compra confirmada" in resultado["mensaje"]


# ------------------------------------------------------------------------
# TESTS ADICIONALES
# ------------------------------------------------------------------------

def test_compra_fecha_hoy_es_valida(usuario_registrado):
    """Prueba que se pueda comprar para el día actual."""
    fecha_hoy = date.today()
    # Si hoy es domingo (día cerrado), el test no aplica y debe pasar.
    if fecha_hoy.weekday() == 6:
        pytest.skip("Hoy es domingo, el parque está cerrado.")

    compra = Compra(usuario_registrado, fecha_hoy,
                    1, [30], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is True
    assert "Compra confirmada" in resultado["mensaje"]


def test_compra_fecha_pasada_falla(usuario_registrado):
    """Prueba que no se pueda comprar para una fecha pasada."""
    fecha_pasada = date.today() - timedelta(days=1)
    compra = Compra(usuario_registrado, fecha_pasada,
                    1, [30], "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "La fecha no es válida" in resultado["mensaje"]


def test_compra_cantidad_limite_inferior_valida(usuario_registrado):
    """Prueba que se pueda comprar exactamente 1 entrada."""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 1, [40], "VIP", "tarjeta")
    resultado = compra.procesar()
    assert resultado["ok"] is True


def test_compra_cantidad_limite_superior_valida(usuario_registrado):
    """Prueba que se puedan comprar exactamente 10 entradas."""
    fecha = date.today() + timedelta(days=3)
    edades = [25] * 10
    compra = Compra(usuario_registrado, fecha, 10,
                    edades, "regular", "efectivo")
    resultado = compra.procesar()
    assert resultado["ok"] is True


def test_compra_cantidad_cero_falla(usuario_registrado):
    """Prueba que no se puedan comprar 0 entradas."""
    fecha = date.today() + timedelta(days=3)
    compra = Compra(usuario_registrado, fecha, 0, [], "regular", "tarjeta")
    resultado = compra.procesar()
    assert resultado["ok"] is False
    assert "Cantidad de entradas inválida" in resultado["mensaje"]
