"""
Cocopop — Base de Datos Completa
Datos reales extraídos de INVGASGAN.xlsx
Proveedor principal: Nihao Jewelry
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cocopop.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.cursor().executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            referencia TEXT NOT NULL,
            unidad_medida TEXT DEFAULT 'UNIDAD',
            precio_venta REAL NOT NULL DEFAULT 0,
            costo REAL NOT NULL DEFAULT 0,
            stock INTEGER DEFAULT 0,
            punto_pedido INTEGER DEFAULT 2,
            activo INTEGER DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            unidad TEXT DEFAULT 'unidades',
            cantidad REAL DEFAULT 0,
            costo_unitario REAL DEFAULT 0,
            proveedor TEXT,
            punto_pedido REAL DEFAULT 10,
            activo INTEGER DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            orden INTEGER,
            cliente TEXT,
            tipo TEXT DEFAULT 'VENTA',
            metodo_pago TEXT DEFAULT 'CONTADO',
            medio_pago TEXT DEFAULT 'EFECTIVO',
            plataforma TEXT,
            estado TEXT DEFAULT 'PAGADO',
            subtotal REAL NOT NULL,
            costo_envio REAL DEFAULT 0,
            total REAL NOT NULL,
            pagado REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            notas TEXT
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        );

        CREATE TABLE IF NOT EXISTS encargos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_encargo TEXT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER DEFAULT 1,
            precio_unitario REAL DEFAULT 0,
            total REAL DEFAULT 0,
            abono REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            estado TEXT DEFAULT 'SEPARADO',
            fecha_entrega TEXT,
            observaciones TEXT
        );

        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT DEFAULT 'Variable',
            categoria TEXT,
            descripcion TEXT,
            medio TEXT,
            monto REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            proveedor TEXT DEFAULT 'Nihao',
            producto TEXT,
            cantidad INTEGER DEFAULT 1,
            costo_unitario REAL DEFAULT 0,
            costo_total REAL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


# =============================================
#  CRUD — PRODUCTOS
# =============================================

def get_productos(solo_activos=True):
    conn = get_connection()
    q = "SELECT * FROM productos"
    if solo_activos:
        q += " WHERE activo = 1"
    q += " ORDER BY categoria, referencia"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_producto(categoria, referencia, unidad_medida, precio_venta, costo, stock=0, punto_pedido=2):
    conn = get_connection()
    conn.execute(
        """INSERT INTO productos (categoria, referencia, unidad_medida, precio_venta, costo, stock, punto_pedido)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (categoria, referencia, unidad_medida, precio_venta, costo, stock, punto_pedido)
    )
    conn.commit()
    conn.close()


def update_producto(producto_id, categoria, referencia, unidad_medida, precio_venta, costo, stock, punto_pedido):
    conn = get_connection()
    conn.execute(
        """UPDATE productos SET categoria=?, referencia=?, unidad_medida=?, precio_venta=?,
           costo=?, stock=?, punto_pedido=? WHERE id=?""",
        (categoria, referencia, unidad_medida, precio_venta, costo, stock, punto_pedido, producto_id)
    )
    conn.commit()
    conn.close()


def delete_producto(producto_id):
    conn = get_connection()
    conn.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()


# =============================================
#  CRUD — INSUMOS
# =============================================

def get_insumos(solo_activos=True):
    conn = get_connection()
    q = "SELECT * FROM insumos"
    if solo_activos:
        q += " WHERE activo = 1"
    q += " ORDER BY nombre"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_insumo(nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido=10):
    conn = get_connection()
    conn.execute(
        "INSERT INTO insumos (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido) VALUES (?,?,?,?,?,?)",
        (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido))
    conn.commit()
    conn.close()


def update_insumo_cantidad(insumo_id, cantidad_agregar):
    conn = get_connection()
    conn.execute("UPDATE insumos SET cantidad = cantidad + ? WHERE id = ?", (cantidad_agregar, insumo_id))
    conn.commit()
    conn.close()


def update_insumo(insumo_id, nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido):
    conn = get_connection()
    conn.execute(
        "UPDATE insumos SET nombre=?, unidad=?, cantidad=?, costo_unitario=?, proveedor=?, punto_pedido=? WHERE id=?",
        (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido, insumo_id))
    conn.commit()
    conn.close()


def delete_insumo(insumo_id):
    conn = get_connection()
    conn.execute("UPDATE insumos SET activo = 0 WHERE id = ?", (insumo_id,))
    conn.commit()
    conn.close()


# =============================================
#  CRUD — VENTAS
# =============================================

def registrar_venta(items, costo_envio=0, cliente="", tipo="VENTA", metodo_pago="CONTADO",
                    medio_pago="EFECTIVO", plataforma="", estado="PAGADO", notas=""):
    conn = get_connection()
    cursor = conn.cursor()
    subtotal = sum(item["cantidad"] * item["precio_unitario"] for item in items)
    total = subtotal + costo_envio
    pagado = total if estado == "PAGADO" else 0
    saldo = total - pagado

    # Get next orden number
    max_orden = cursor.execute("SELECT COALESCE(MAX(orden), 0) FROM ventas").fetchone()[0]

    cursor.execute(
        """INSERT INTO ventas (orden, cliente, tipo, metodo_pago, medio_pago, plataforma, estado,
                               subtotal, costo_envio, total, pagado, saldo, notas)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (max_orden + 1, cliente, tipo, metodo_pago, medio_pago, plataforma, estado,
         subtotal, costo_envio, total, pagado, saldo, notas))
    venta_id = cursor.lastrowid

    for item in items:
        item_sub = item["cantidad"] * item["precio_unitario"]
        cursor.execute(
            "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
            (venta_id, item["producto_id"], item["cantidad"], item["precio_unitario"], item_sub))
        cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                        (item["cantidad"], item["producto_id"]))
    conn.commit()
    conn.close()
    return venta_id


def get_ventas(limite=50):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM ventas ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_detalle_venta(venta_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT dv.*, p.referencia as producto_nombre, p.categoria
           FROM detalle_ventas dv JOIN productos p ON dv.producto_id = p.id
           WHERE dv.venta_id = ?""", (venta_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ventas_detalladas():
    conn = get_connection()
    rows = conn.execute("""
        SELECT v.id as venta_id, v.fecha, v.orden, v.cliente, v.tipo, v.metodo_pago, v.medio_pago,
               v.plataforma, v.estado as venta_estado, v.subtotal as venta_subtotal,
               v.costo_envio, v.total as venta_total, v.pagado, v.saldo,
               dv.producto_id, p.referencia as producto_nombre, p.categoria,
               dv.cantidad, dv.precio_unitario, dv.subtotal
        FROM ventas v
        JOIN detalle_ventas dv ON v.id = dv.venta_id
        JOIN productos p ON dv.producto_id = p.id
        ORDER BY v.fecha DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =============================================
#  CRUD — ENCARGOS
# =============================================

def get_encargos(estado=None):
    conn = get_connection()
    q = "SELECT * FROM encargos"
    params = []
    if estado:
        q += " WHERE estado = ?"
        params.append(estado)
    q += " ORDER BY fecha DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_encargo(id_encargo, cliente, producto, cantidad, precio_unitario, abono=0,
                fecha_entrega="", observaciones=""):
    total = cantidad * precio_unitario
    saldo = total - abono
    estado = "SEPARADO" if saldo > 0 else "ENTREGADO"
    conn = get_connection()
    conn.execute(
        """INSERT INTO encargos (id_encargo, cliente, producto, cantidad, precio_unitario,
                                  total, abono, saldo, estado, fecha_entrega, observaciones)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (id_encargo, cliente, producto, cantidad, precio_unitario, total, abono, saldo, estado,
         fecha_entrega, observaciones))
    conn.commit()
    conn.close()


def update_encargo_abono(encargo_id, nuevo_abono):
    conn = get_connection()
    enc = conn.execute("SELECT total FROM encargos WHERE id = ?", (encargo_id,)).fetchone()
    if enc:
        saldo = enc["total"] - nuevo_abono
        estado = "ENTREGADO" if saldo <= 0 else "SEPARADO"
        conn.execute("UPDATE encargos SET abono=?, saldo=?, estado=? WHERE id=?",
                      (nuevo_abono, max(saldo, 0), estado, encargo_id))
    conn.commit()
    conn.close()


def update_encargo_estado(encargo_id, estado):
    conn = get_connection()
    conn.execute("UPDATE encargos SET estado = ? WHERE id = ?", (estado, encargo_id))
    conn.commit()
    conn.close()


# =============================================
#  CRUD — GASTOS
# =============================================

def get_gastos(limite=50):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM gastos ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_gasto(tipo, categoria, descripcion, medio, monto):
    conn = get_connection()
    conn.execute("INSERT INTO gastos (tipo, categoria, descripcion, medio, monto) VALUES (?,?,?,?,?)",
                  (tipo, categoria, descripcion, medio, monto))
    conn.commit()
    conn.close()


# =============================================
#  CRUD — COMPRAS
# =============================================

def get_compras(limite=100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM compras ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_compra(proveedor, producto, cantidad, costo_unitario):
    conn = get_connection()
    conn.execute(
        "INSERT INTO compras (proveedor, producto, cantidad, costo_unitario, costo_total) VALUES (?,?,?,?,?)",
        (proveedor, producto, cantidad, costo_unitario, cantidad * costo_unitario))
    conn.commit()
    conn.close()


# =============================================
#  DATOS REALES — INVGASGAN.xlsx
# =============================================

def cargar_datos_demo():
    conn = get_connection()
    if conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0] > 0:
        conn.close()
        return False

    cursor = conn.cursor()

    # ── PRODUCTOS COMPLETOS (64 items) ──
    # (categoria, referencia, unidad, precio_venta, costo_nihao, stock, pto_pedido)
    productos = [
        # ARETES
        ("ARETES", "Aretes Vintage Circón (Set x3)", "SET x3", 26800, 20500, 2, 2),
        # CADENAS
        ("CADENA", "Cadena Trenzada Dorada", "UNIDAD", 10800, 10500, 2, 2),
        ("CADENA", "Cadena Ondas Plateada LARGA", "UNIDAD", 15500, 10500, 2, 2),
        ("CADENA", "Cadena Serpiente Dorada MEDIO", "UNIDAD", 15500, 10500, 2, 2),
        ("CADENA", "Cadena Serpiente Plateada MEDIO", "UNIDAD", 15500, 10500, 2, 2),
        ("CADENA", "Cadena Ondas Dorada larga 22CM HOMBRE", "UNIDAD", 15500, 10500, 2, 2),
        ("CADENA", "Cadena Corazón Rosa Dorada", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena DIAMANTITO", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Aurora Dorada", "UNIDAD", 10000, 10500, 1, 2),
        ("CADENA", "Cadena Inicial fondo blanco S", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Inicial fondo blanco A", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Inicial fondo blanco M", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Inicial fondo blanco L", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Box chain DORADA 60*2.5", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Paper Clip", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Inicial Fondo Negro A", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Inicial Fondo Negro M", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Trenzada Larga DORADA 60*2.6", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Cuentas Plateada", "UNIDAD", 14000, 14000, 1, 2),
        ("CADENA", "Cadena Cuentas Dorada", "UNIDAD", 14000, 14000, 1, 2),
        ("CADENA", "Cadena Plaquita Dorada", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Plaquita Plateada", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Cruz Plateada", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Cruz Dorada", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena Box Chain Plateada DELGADA", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Box Chain PlateadaGRUESA", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Doble", "UNIDAD", 10500, 10500, 1, 2),
        ("CADENA", "Cadena Perla", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "Cadena circles", "UNIDAD", 10500, 10500, 2, 2),
        ("CADENA", "Cadena Green", "UNIDAD", 15500, 15500, 1, 2),
        ("CADENA", "CADENA ONDAS PLATEADA 45CM MUJER", "UNIDAD", 16500, 10500, 2, 2),
        ("CADENA", "Cadena Goles", "UNIDAD", 10800, 10500, 2, 2),
        # ARETES TOPOS
        ("ARETES TOPOS", "Aretes Corazón", "UNIDAD", 7500, 3750, 2, 3),
        ("ARETES TOPOS", "Aretes Luna", "UNIDAD", 7500, 3750, 2, 3),
        ("ARETES TOPOS", "ARETES TOPOS Mariposa", "UNIDAD", 7500, 3750, 2, 3),
        ("ARETES TOPOS", "Topos Plateado 4mm", "PAR", 5000, 5000, 1, 2),
        ("ARETES TOPOS", "Topos Plateado 3mm", "PAR", 4500, 4500, 1, 2),
        ("ARETES TOPOS", "Topos Semiesfera", "PAR", 10500, 10500, 1, 2),
        ("ARETES TOPOS", "Topos Dorados 3mm", "PAR", 4000, 4000, 1, 3),
        ("ARETES TOPOS", "Topos Dorados 5mm", "PAR", 5000, 5000, 1, 2),
        ("ARETES TOPOS", "Topos Dorados 8mm", "PAR", 5500, 5500, 1, 2),
        # ARETES ARGOLLAS
        ("ARETES ARGOLLAS", "Aretes Punk Ronde Dorado 8MM", "UNIDAD", 6500, 3250, 2, 3),
        ("ARETES ARGOLLAS", "ARETES U DORADO", "PAR", 18500, 18500, 2, 2),
        ("ARETES ARGOLLAS", "ARETES U PLATEADO", "PAR", 18500, 18500, 1, 2),
        ("ARETES ARGOLLAS", "Aretes Punk Ronde Plateado 18MM", "UNIDAD", 6500, 3250, 2, 3),
        ("ARETES ARGOLLAS", "Aretes Arco Plateado", "PAR", 14500, 14500, 1, 2),
        ("ARETES ARGOLLAS", "Aretes Arco Dorado", "PAR", 14500, 14500, 1, 2),
        ("ARETES ARGOLLAS", "Aretes Aura Dorada", "PAR", 22500, 22500, 1, 2),
        # PULSERAS
        ("PULSERA", "Pulsera Trenzada Dorada 22CM HOMBRE", "UNIDAD", 17000, 8500, 2, 2),
        ("PULSERA", "Pulsera Trenzada Plateada 22 CM GRUESA", "UNIDAD", 8500, 8500, 1, 2),
        ("PULSERA", "Pulsera Trenzada Plateada 22CM DELGADA", "UNIDAD", 8500, 8500, 1, 2),
        ("PULSERA", "Pulsera con anillo A", "UNIDAD", 20500, 20500, 1, 2),
        ("PULSERA", "Pulsera Con Anillo B", "UNIDAD", 22500, 22500, 1, 2),
        ("PULSERA", "Pulsera Trenzada Plateada18CM", "UNIDAD", 8500, 8500, 1, 2),
        ("PULSERA", "Pulsera Trenzada DORADA 18CM", "UNIDAD", 8500, 8500, 1, 2),
        # ANILLOS
        ("ANILLO", "Anillo Raya Espiral", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Espiral", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Siren", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Brillitos", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Flowers", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Rollos", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Puntos", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Lineal", "UNIDAD", 6500, 6500, 1, 2),
        ("ANILLO", "Anillo Paralel", "UNIDAD", 6500, 6500, 1, 2),
        # GAFAS
        ("GAFAS", "GAFAS CELINE", "UNIDAD", 20000, 20000, 1, 1),
    ]

    for p in productos:
        cursor.execute(
            """INSERT INTO productos (categoria, referencia, unidad_medida, precio_venta, costo, stock, punto_pedido)
               VALUES (?, ?, ?, ?, ?, ?, ?)""", p)

    # ── VENTAS REALES (de INVGASGAN - hoja VENTAS) ──
    # Clientes y órdenes reales. Totales objetivo: Ventas $719,000 · Recibido $485,500 · Por cobrar $233,500
    ventas_data = [
        # (orden, cliente, [(prod_id, cant, precio)], metodo, medio, plataforma, estado, envio)
        (1, "ELIZABETH", [(6, 1, 13000), (7, 1, 13000)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (2, "ELIZABETH", [(8, 1, 15500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (3, "ELIZABETH", [(62, 1, 4500), (39, 1, 4000)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (4, "ELIZABETH", [(49, 1, 8500), (60, 1, 6500), (24, 1, 15500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (5, "ELIZABETH", [(51, 1, 8500), (24, 1, 13000)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (6, "SANTIAGO", [(50, 1, 8500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 8000),
        (7, "MARGARITA", [(43, 1, 18500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (8, "MARGARITA", [(39, 1, 4000), (15, 1, 10500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (9, "ERIDNEYS", [(15, 1, 10500), (29, 1, 10500), (56, 1, 6500), (58, 1, 6500), (62, 1, 6500)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (10, "ERIDNEYS", [(42, 1, 6500), (46, 1, 14500), (60, 1, 6500)], "CONTADO", "EFECTIVO", "", "PAGADO", 5000),
        (11, "DANIS", [(63, 1, 6500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (12, "MELLA", [(38, 1, 10500), (53, 1, 22500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 5000),
        (13, "SARA", [(52, 1, 20500), (31, 1, 16500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (14, "SARA", [(54, 1, 8500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (15, "SARA", [(1, 1, 26800), (31, 1, 16500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (16, "MARIA DE LOS ANGELES", [(46, 1, 14500), (48, 1, 22500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (17, "ABEGJIS", [(39, 1, 4000)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (18, "PEDRO JUAN", [(23, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (19, "PEDRO JUAN", [(54, 1, 8500)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (20, "PEDRO JUAN", [(1, 1, 26800)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (21, "SHARY", [(43, 1, 18500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (22, "SANDY", [(20, 1, 14000)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (23, "SANDY", [(11, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (24, "LUBI", [(21, 1, 15500)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (25, "LUGOMIR", [(19, 1, 14000)], "CONTADO", "EFECTIVO", "", "PAGADO", 0),
        (26, "BRAHOT", [(65, 1, 20000)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (27, "PAOLA", [(44, 1, 18500), (31, 1, 16500), (10, 1, 15500), (42, 1, 6500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (28, "NAYIBI", [(3, 1, 15500), (35, 1, 7500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (29, "NAYIBI", [(16, 1, 15500)], "CONTADO", "EFECTIVO", "", "PAGADO", 5000),
        (30, "LILIANA", [(12, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (31, "JUNIOR", [(37, 1, 4500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (32, "CRISTIAN", [(18, 1, 10500), (26, 1, 10500), (14, 1, 10500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (33, "ALEX", [(27, 1, 10500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (34, "JHIS", [(25, 1, 10500), (22, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (35, "JHIS", [(5, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (36, "SORTEO1", [(28, 1, 15500)], "CONTADO", "TRANSFERENCIA", "NEQUI", "PAGADO", 0),
        (37, "Minina", [(9, 1, 10000)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
        (38, "Sofia", [(29, 2, 10500)], "CREDITO", "TRANSFERENCIA", "NEQUI", "PENDIENTE", 0),
    ]

    fecha_base = datetime(2026, 1, 15)
    for i, venta in enumerate(ventas_data):
        orden, cliente, items, metodo, medio, plataforma, estado, envio = venta
        fecha = fecha_base + timedelta(days=i * 2)
        subtotal = sum(cant * precio for _, cant, precio in items)
        total = subtotal + envio
        pagado = total if estado == "PAGADO" else 0
        saldo = total - pagado

        cursor.execute(
            """INSERT INTO ventas (fecha, orden, cliente, tipo, metodo_pago, medio_pago, plataforma, estado,
                                   subtotal, costo_envio, total, pagado, saldo)
               VALUES (?, ?, ?, 'VENTA', ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (fecha.strftime("%Y-%m-%d %H:%M:%S"), orden, cliente, metodo, medio, plataforma, estado,
             subtotal, envio, total, pagado, saldo))
        vid = cursor.lastrowid
        for pid, cant, precio in items:
            cursor.execute(
                "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
                (vid, pid, cant, precio, cant * precio))

    # ── ENCARGOS REALES ──
    encargos = [
        ("1-EN", "Pedro Barraza", "Pulsera trenzada plata 20cm", 1, 8500, 8500, "SEPARADO", "21:04"),
        ("2-EN", "Emilio Pacheco", "Cadena Cruz Plateada", 1, 15500, 7500, "SEPARADO", "21:04"),
        ("3-EN", "Luz Escorias", "Anillo Rose", 1, 9000, 0, "SEPARADO", "21:04"),
    ]
    for enc in encargos:
        id_enc, cliente, producto, cant, precio, abono, estado, fecha_e = enc
        total_enc = cant * precio
        saldo_enc = total_enc - abono
        cursor.execute(
            """INSERT INTO encargos (id_encargo, cliente, producto, cantidad, precio_unitario,
                                      total, abono, saldo, estado, fecha_entrega) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (id_enc, cliente, producto, cant, precio, total_enc, abono, saldo_enc, estado, fecha_e))

    # ── GASTOS REALES ──
    gastos = [
        ("2026-01-01", "Variable", "Envio", "Envio a Colombia", "Tarjeta", 67295),
        ("2026-01-01", "Variable", "Empaque", "Tarjetas y bolsitas", "Tarjeta", 15842),
        ("2026-03-25", "Variable", "Empaque", "Tarjetas y bolsitas", "Nequi", 28150),
        ("2026-03-25", "Variable", "Envio", "Envio a Colombia", "Nequi", 170385),
        ("2026-01-30", "Variable", "Empaque", "Cajita", "Efectivo", 3500),
    ]
    for g in gastos:
        cursor.execute("INSERT INTO gastos (fecha, tipo, categoria, descripcion, medio, monto) VALUES (?,?,?,?,?,?)", g)

    # ── COMPRAS PRINCIPALES (Nihao) ──
    for p in productos:
        cursor.execute(
            "INSERT INTO compras (fecha, proveedor, producto, cantidad, costo_unitario, costo_total) VALUES (?,?,?,?,?,?)",
            ("2026-01-01", "Nihao", p[1], p[5], p[4], p[5] * p[4]))

    # ── INSUMOS / EMPAQUE ──
    insumos = [
        ("Tarjetas presentación (100 pzs)", "paquete", 1, 13927, "Nihao", 1),
        ("Bolsitas Beige 8*10cm (50 pzs)", "paquete", 1, 14223, "Nihao", 1),
        ("Cajitas empaque", "unidades", 10, 3500, "Local", 5),
        ("Color mágico (100 pzs)", "paquete", 1, 11579, "Nihao", 1),
        ("Tarjetas 7*9.5 (40 pzs)", "paquete", 1, 4400, "Nihao", 1),
    ]
    for ins in insumos:
        cursor.execute(
            "INSERT INTO insumos (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido) VALUES (?,?,?,?,?,?)", ins)

    conn.commit()
    conn.close()
    return True
