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

        CREATE TABLE IF NOT EXISTS caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            origen TEXT NOT NULL,
            id_ref INTEGER,
            medio_pago TEXT,
            entrada REAL DEFAULT 0,
            salida REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            estado TEXT DEFAULT 'Confirmado'
        );
    """)
    conn.commit()
    
    # Comprobar si caja está vacía pero hay ventas
    caja_count = conn.cursor().execute("SELECT COUNT(*) FROM caja").fetchone()[0]
    ventas_count = conn.cursor().execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    if caja_count == 0 and ventas_count > 0:
        sync_historico_caja(conn)
        
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
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO insumos (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido) VALUES (?,?,?,?,?,?)",
        (nombre, unidad, cantidad, costo_unitario, proveedor, punto_pedido))
    insumo_id = cursor.lastrowid
    
    if costo_unitario > 0 and cantidad > 0:
        cursor.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('EGRESO', 'Compra inventario', 'Insumo', ?, 'Transferencia', 0, ?, 'Confirmado')",
                       (insumo_id, costo_unitario * cantidad))
    
    conn.commit()
    conn.close()
    if costo_unitario > 0 and cantidad > 0:
        recalcular_saldos_caja()


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
                    medio_pago="EFECTIVO", plataforma="", estado="PAGADO", notas="", orden=None, pagado_manual=None):
    conn = get_connection()
    cursor = conn.cursor()
    subtotal = sum(item["cantidad"] * item["precio_unitario"] for item in items)
    total = subtotal + costo_envio
    
    if pagado_manual is not None:
        pagado = pagado_manual
    else:
        pagado = total if estado == "PAGADO" else 0
    saldo = total - pagado

    if orden is None:
        orden = cursor.execute("SELECT COALESCE(MAX(orden), 0) FROM ventas").fetchone()[0] + 1
    else:
        cursor.execute("UPDATE ventas SET orden = orden + 1 WHERE orden >= ?", (orden,))

    cursor.execute(
        """INSERT INTO ventas (orden, cliente, tipo, metodo_pago, medio_pago, plataforma, estado,
                               subtotal, costo_envio, total, pagado, saldo, notas)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (orden, cliente, tipo, metodo_pago, medio_pago, plataforma, estado,
         subtotal, costo_envio, total, pagado, saldo, notas))
    venta_id = cursor.lastrowid

    for item in items:
        item_sub = item["cantidad"] * item["precio_unitario"]
        cursor.execute(
            "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
            (venta_id, item["producto_id"], item["cantidad"], item["precio_unitario"], item_sub))
        cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                        (item["cantidad"], item["producto_id"]))
                        
    if pagado > 0:
        cursor.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('INGRESO', 'Venta', 'Venta', ?, ?, ?, 0, 'Confirmado')", 
                       (venta_id, medio_pago, pagado))
                       
    conn.commit()
    conn.close()
    recalcular_saldos_caja()
    return venta_id

def update_venta_info(venta_id, cliente, metodo_pago, medio_pago, plataforma, estado, notas, items=None, costo_envio=None, orden=None):
    conn = get_connection()
    v = conn.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    if not v:
        conn.close()
        return

    cursor = conn.cursor()

    if orden is not None and orden != v["orden"]:
        exist = cursor.execute("SELECT id FROM ventas WHERE orden = ?", (orden,)).fetchone()
        if exist:
            cursor.execute("UPDATE ventas SET orden = orden + 1 WHERE orden >= ?", (orden,))
    else:
        orden = v["orden"]

    if items is not None:
        detalles_viejos = cursor.execute("SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id = ?", (venta_id,)).fetchall()
        for d in detalles_viejos:
            cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (d["cantidad"], d["producto_id"]))
        cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (venta_id,))
        
        subtotal = sum(item["cantidad"] * item["precio_unitario"] for item in items)
        for item in items:
            item_sub = item["cantidad"] * item["precio_unitario"]
            cursor.execute(
                "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
                (venta_id, item["producto_id"], item["cantidad"], item["precio_unitario"], item_sub))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item["cantidad"], item["producto_id"]))
    else:
        subtotal = v["subtotal"]

    if costo_envio is None:
        costo_envio = v["costo_envio"]

    total = subtotal + costo_envio
    pagado = total if estado == "PAGADO" else v["pagado"]
    saldo = total - pagado

    cursor.execute(
        """UPDATE ventas SET orden=?, cliente=?, metodo_pago=?, medio_pago=?, plataforma=?, estado=?, subtotal=?, costo_envio=?, total=?, pagado=?, saldo=?, notas=? WHERE id=?""",
        (orden, cliente, metodo_pago, medio_pago, plataforma, estado, subtotal, costo_envio, total, pagado, saldo, notas, venta_id)
    )

    cursor.execute("DELETE FROM caja WHERE origen = 'Venta' AND id_ref = ?", (venta_id,))
    if pagado > 0:
        cursor.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('INGRESO', 'Venta', 'Venta', ?, ?, ?, 0, 'Confirmado')", 
                       (venta_id, medio_pago, pagado))

    conn.commit()
    conn.close()
    recalcular_saldos_caja()
    
def delete_venta(venta_id):
    conn = get_connection()
    cursor = conn.cursor()
    v = cursor.execute("SELECT orden FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    orden = v["orden"] if v else None
    
    detalles = cursor.execute("SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id = ?", (venta_id,)).fetchall()
    for d in detalles:
        cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (d["cantidad"], d["producto_id"]))
    cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
    cursor.execute("DELETE FROM caja WHERE origen = 'Venta' AND id_ref = ?", (venta_id,))
    
    if orden:
        cursor.execute("UPDATE ventas SET orden = orden - 1 WHERE orden > ?", (orden,))

    conn.commit()
    conn.close()
    recalcular_saldos_caja()

def update_abono_venta(venta_id, nuevo_abono_total):
    conn = get_connection()
    v = conn.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    if not v:
        conn.close()
        return
        
    total = v["total"]
    saldo = max(0, total - nuevo_abono_total)
    estado = "PAGADO" if saldo <= 0 else v["estado"]
    diferencia = nuevo_abono_total - v["pagado"]
    
    conn.execute("UPDATE ventas SET pagado=?, saldo=?, estado=? WHERE id=?", (nuevo_abono_total, saldo, estado, venta_id))
    
    if diferencia > 0:
        conn.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, plataforma, entrada, salida, estado) VALUES ('INGRESO', 'Abono', 'Venta', ?, ?, ?, ?, 0, 'Confirmado')",
                     (venta_id, v["medio_pago"], v["plataforma"], diferencia))
                     
    conn.commit()
    conn.close()
    if diferencia > 0:
        recalcular_saldos_caja()

def descontar_insumos(insumo_nombres):
    conn = get_connection()
    for ins in insumo_nombres:
        conn.execute("UPDATE insumos SET cantidad = MAX(0, cantidad - 1) WHERE nombre = ?", (ins,))
    conn.commit()
    conn.close()


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
    enc_id = conn.cursor().lastrowid
    
    if abono > 0:
        conn.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('INGRESO', 'Abono cliente', 'Encargo', ?, 'Efectivo', ?, 0, 'Confirmado')",
                       (enc_id, abono))
                       
    conn.commit()
    conn.close()
    if abono > 0:
        recalcular_saldos_caja()


def update_encargo_abono(encargo_id, nuevo_abono):
    conn = get_connection()
    enc = conn.execute("SELECT total, abono FROM encargos WHERE id = ?", (encargo_id,)).fetchone()
    if enc:
        diferencia = nuevo_abono - enc["abono"]
        saldo = enc["total"] - nuevo_abono
        estado = "ENTREGADO" if saldo <= 0 else "SEPARADO"
        conn.execute("UPDATE encargos SET abono=?, saldo=?, estado=? WHERE id=?",
                      (nuevo_abono, max(saldo, 0), estado, encargo_id))
        if diferencia > 0:
            conn.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('INGRESO', 'Abono cliente', 'Encargo', ?, 'Efectivo', ?, 0, 'Confirmado')",
                           (encargo_id, diferencia))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


def update_encargo_estado(encargo_id, estado):
    conn = get_connection()
    conn.execute("UPDATE encargos SET estado = ? WHERE id = ?", (estado, encargo_id))
    conn.commit()
    conn.close()


def update_encargo(encargo_id, id_encargo, cliente, producto, cantidad, precio_unitario, fecha_entrega, observaciones):
    conn = get_connection()
    enc = conn.execute("SELECT abono FROM encargos WHERE id = ?", (encargo_id,)).fetchone()
    abono = enc["abono"] if enc else 0
    total = cantidad * precio_unitario
    saldo = total - abono
    estado = "SEPARADO" if saldo > 0 else "ENTREGADO"
    conn.execute(
        "UPDATE encargos SET id_encargo=?, cliente=?, producto=?, cantidad=?, precio_unitario=?, total=?, saldo=?, estado=?, fecha_entrega=?, observaciones=? WHERE id=?",
        (id_encargo, cliente, producto, cantidad, precio_unitario, total, max(saldo, 0), estado, fecha_entrega, observaciones, encargo_id))
    conn.commit()
    conn.close()


def delete_encargo(encargo_id):
    conn = get_connection()
    conn.execute("DELETE FROM encargos WHERE id = ?", (encargo_id,))
    conn.execute("DELETE FROM caja WHERE origen = 'Encargo' AND id_ref = ?", (encargo_id,))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


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
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (tipo, categoria, descripcion, medio, monto) VALUES (?,?,?,?,?)",
                  (tipo, categoria, descripcion, medio, monto))
    gasto_id = cursor.lastrowid
    
    cat_caja = "Gastos varios"
    if categoria.lower() == "envío" or categoria.lower() == "envio": cat_caja = "Envío"
    elif categoria.lower() == "empaque": cat_caja = "Empaque"
    
    cursor.execute("INSERT INTO caja (tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES ('EGRESO', ?, 'Gasto', ?, ?, 0, ?, 'Confirmado')",
                   (cat_caja, gasto_id, medio, monto))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


def update_gasto(gasto_id, tipo, categoria, descripcion, medio, monto):
    conn = get_connection()
    conn.execute("UPDATE gastos SET tipo=?, categoria=?, descripcion=?, medio=?, monto=? WHERE id=?",
                 (tipo, categoria, descripcion, medio, monto, gasto_id))
    cat_caja = "Gastos varios"
    if categoria.lower() == "envío" or categoria.lower() == "envio": cat_caja = "Envío"
    elif categoria.lower() == "empaque": cat_caja = "Empaque"
    conn.execute("UPDATE caja SET categoria=?, medio_pago=?, salida=? WHERE origen='Gasto' AND id_ref=?",
                 (cat_caja, medio, monto, gasto_id))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


def delete_gasto(gasto_id):
    conn = get_connection()
    conn.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    conn.execute("DELETE FROM caja WHERE origen = 'Gasto' AND id_ref = ?", (gasto_id,))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


# =============================================
#  CRUD — COMPRAS
# =============================================

def get_compras(limite=100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM compras ORDER BY fecha DESC LIMIT ?", (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_compra(fecha, proveedor, producto, cantidad, costo_unitario):
    conn = get_connection()
    conn.execute(
        "INSERT INTO compras (fecha, proveedor, producto, cantidad, costo_unitario, costo_total) VALUES (?,?,?,?,?,?)",
        (fecha, proveedor, producto, cantidad, costo_unitario, cantidad * costo_unitario))
    conn.commit()
    conn.close()


def update_compra(compra_id, fecha, proveedor, producto, cantidad, costo_unitario):
    conn = get_connection()
    conn.execute(
        "UPDATE compras SET fecha=?, proveedor=?, producto=?, cantidad=?, costo_unitario=?, costo_total=? WHERE id=?",
        (fecha, proveedor, producto, cantidad, costo_unitario, cantidad * costo_unitario, compra_id))
    conn.commit()
    conn.close()


def delete_compra(compra_id):
    conn = get_connection()
    conn.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
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
    
    # === SYNC CAJA HISTORICA ===
    sync_historico_caja(conn)
    
    conn.close()
    return True

    conn.close()
    return True


# =============================================
#  CRUD — CAJA
# =============================================

def get_caja():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM caja ORDER BY fecha DESC, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def recalcular_saldos_caja():
    """Recalcula el saldo acumulativo de la caja"""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, entrada, salida FROM caja ORDER BY fecha ASC, id ASC").fetchall()
    saldo = 0.0
    for r in rows:
        saldo += (r["entrada"] - r["salida"])
        cursor.execute("UPDATE caja SET saldo = ? WHERE id = ?", (saldo, r["id"]))
    conn.commit()
    conn.close()

def add_movimiento_caja(fecha, tipo, categoria, origen, medio_pago, entrada, salida, estado='Confirmado'):
    conn = get_connection()
    conn.execute(
        "INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?)",
        (fecha, tipo, categoria, origen, medio_pago, entrada, salida, estado)
    )
    conn.commit()
    conn.close()
    recalcular_saldos_caja()

def update_movimiento_caja(caja_id, fecha, tipo, categoria, medio_pago, entrada, salida, estado):
    conn = get_connection()
    conn.execute(
        "UPDATE caja SET fecha=?, tipo=?, categoria=?, medio_pago=?, entrada=?, salida=?, estado=? WHERE id=?",
        (fecha, tipo, categoria, medio_pago, entrada, salida, estado, caja_id)
    )
    conn.commit()
    conn.close()
    recalcular_saldos_caja()

def delete_movimiento_caja(caja_id):
    conn = get_connection()
    conn.execute("DELETE FROM caja WHERE id = ?", (caja_id,))
    conn.commit()
    conn.close()
    recalcular_saldos_caja()


def sync_historico_caja(conn):
    """Sincroniza todos los movimientos preexistentes a la nueva tabla de caja."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM caja")
    
    # 1. Ventas
    ventas = cursor.execute("SELECT id, fecha, medio_pago, pagado FROM ventas WHERE pagado > 0").fetchall()
    for v in ventas:
        cursor.execute("INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, 'INGRESO', 'Venta', 'Venta', ?, ?, ?, 0, 'Confirmado')", 
                       (v["fecha"], v["id"], v["medio_pago"], v["pagado"]))
        
    # 2. Encargos (Abonos)
    encargos = cursor.execute("SELECT id, fecha, abono FROM encargos WHERE abono > 0").fetchall()
    for e in encargos:
        cursor.execute("INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, 'INGRESO', 'Abono cliente', 'Encargo', ?, 'Efectivo', ?, 0, 'Confirmado')",
                       (e["fecha"], e["id"], e["abono"]))
        
    # 3. Gastos
    gastos = cursor.execute("SELECT id, fecha, categoria, medio, monto FROM gastos WHERE monto > 0").fetchall()
    for g in gastos:
        cat = "Gastos varios"
        if g["categoria"].lower() == "envio": cat = "Envío"
        elif g["categoria"].lower() == "empaque": cat = "Empaque"
        cursor.execute("INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, 'EGRESO', ?, 'Gasto', ?, ?, 0, ?, 'Confirmado')",
                       (g["fecha"], cat, g["id"], g["medio"], g["monto"]))
        
    # 4. Compras
    compras = cursor.execute("SELECT id, fecha, costo_total FROM compras WHERE costo_total > 0").fetchall()
    for c in compras:
        cursor.execute("INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, 'EGRESO', 'Compra inventario', 'Compra', ?, 'Transferencia', 0, ?, 'Confirmado')",
                       (c["fecha"], c["id"], c["costo_total"]))
        
    # 5. Insumos
    insumos = cursor.execute("SELECT id, costo_unitario, cantidad, fecha_creacion FROM insumos WHERE costo_unitario > 0 AND cantidad > 0").fetchall()
    for i in insumos:
        cursor.execute("INSERT INTO caja (fecha, tipo, categoria, origen, id_ref, medio_pago, entrada, salida, estado) VALUES (?, 'EGRESO', 'Compra inventario', 'Insumo', ?, 'Transferencia', 0, ?, 'Confirmado')",
                       (i["fecha_creacion"], i["id"], i["costo_unitario"] * i["cantidad"]))
                       
    conn.commit()
    
    # Recalcular saldos
    rows = cursor.execute("SELECT id, entrada, salida FROM caja ORDER BY fecha ASC, id ASC").fetchall()
    saldo = 0.0
    for r in rows:
        saldo += (r["entrada"] - r["salida"])
        cursor.execute("UPDATE caja SET saldo = ? WHERE id = ?", (saldo, r["id"]))
    
    conn.commit()
