"""
Cocopop — Análisis de Datos con Ganancia Real
Datos alineados con INVGASGAN.xlsx
"""

import pandas as pd
from datetime import datetime, timedelta
import database as db


def get_dataframe_ventas():
    datos = db.get_ventas_detalladas()
    if not datos:
        return pd.DataFrame()
    df = pd.DataFrame(datos)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def get_dataframe_productos():
    productos = db.get_productos()
    if not productos:
        return pd.DataFrame()
    return pd.DataFrame(productos)


def get_dataframe_ventas_resumen():
    ventas = db.get_ventas(limite=9999)
    if not ventas:
        return pd.DataFrame()
    df = pd.DataFrame(ventas)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def get_dataframe_encargos():
    encargos = db.get_encargos()
    if not encargos:
        return pd.DataFrame()
    return pd.DataFrame(encargos)


def get_dataframe_gastos():
    gastos = db.get_gastos(limite=9999)
    if not gastos:
        return pd.DataFrame()
    return pd.DataFrame(gastos)


# =============================================
#  KPIs — Alineados con LISTAS de INVGASGAN
# =============================================

def calcular_kpis(periodo_dias=30):
    df = get_dataframe_ventas()
    df_ventas = get_dataframe_ventas_resumen()
    df_productos = get_dataframe_productos()
    df_encargos = get_dataframe_encargos()
    df_gastos = get_dataframe_gastos()

    if df_ventas.empty:
        return {
            "total_ventas": 0, "ventas_totales_monto": 0, "recibido": 0, "por_cobrar": 0,
            "ticket_promedio": 0, "costo_envio_total": 0, "productos_vendidos": 0,
            "productos_bajo_stock": 0, "ventas_periodo": 0, "ingresos_periodo": 0,
            "encargos_pendientes": 0, "total_gastos": 0, "ganancia_total": 0,
        }

    fecha_corte = datetime.now() - timedelta(days=periodo_dias)

    total_ventas = len(df_ventas)
    ventas_totales_monto = df_ventas["total"].sum()
    costo_envio_total = df_ventas["costo_envio"].sum()
    ticket_promedio = df_ventas["total"].mean()
    productos_vendidos = df["cantidad"].sum() if not df.empty else 0

    # Recibido vs Por cobrar (como en LISTAS de INVGASGAN)
    recibido = df_ventas[df_ventas["estado"] == "PAGADO"]["total"].sum()
    por_cobrar = df_ventas[df_ventas["estado"] == "PENDIENTE"]["total"].sum()

    # Stock bajo
    productos_bajo_stock = 0
    if not df_productos.empty:
        productos_bajo_stock = len(df_productos[df_productos["stock"] <= df_productos["punto_pedido"]])

    # Encargos
    encargos_pendientes = 0
    saldo_encargos = 0
    if not df_encargos.empty:
        sep = df_encargos[df_encargos["estado"] == "SEPARADO"]
        encargos_pendientes = len(sep)
        saldo_encargos = sep["saldo"].sum() if not sep.empty else 0

    # Gastos
    total_gastos = df_gastos["monto"].sum() if not df_gastos.empty else 0

    # Ganancia bruta (de productos vendidos)
    ganancia_total = 0
    if not df.empty and not df_productos.empty:
        prods = df_productos.set_index("id")
        for _, row in df.iterrows():
            pid = row["producto_id"]
            if pid in prods.index:
                costo = prods.loc[pid, "costo"]
                ganancia_total += (row["precio_unitario"] - costo) * row["cantidad"]

    # Período
    df_per = df_ventas[df_ventas["fecha"] >= fecha_corte]
    ventas_periodo = len(df_per)
    ingresos_periodo = df_per["total"].sum() if not df_per.empty else 0

    return {
        "total_ventas": int(total_ventas),
        "ventas_totales_monto": round(ventas_totales_monto, 0),
        "recibido": round(recibido, 0),
        "por_cobrar": round(por_cobrar, 0),
        "ticket_promedio": round(ticket_promedio, 0),
        "costo_envio_total": round(costo_envio_total, 0),
        "productos_vendidos": int(productos_vendidos),
        "productos_bajo_stock": int(productos_bajo_stock),
        "ventas_periodo": int(ventas_periodo),
        "ingresos_periodo": round(ingresos_periodo, 0),
        "encargos_pendientes": int(encargos_pendientes),
        "saldo_encargos": round(saldo_encargos, 0),
        "total_gastos": round(total_gastos, 0),
        "ganancia_total": round(ganancia_total, 0),
    }


# =============================================
#  GANANCIA POR PRODUCTO (como hoja GANANCIA)
# =============================================

def ganancia_por_producto():
    """Calcula ganancia por producto — replica la hoja GANANCIA de INVGASGAN."""
    df = get_dataframe_ventas()
    df_prod = get_dataframe_productos()

    if df.empty or df_prod.empty:
        return pd.DataFrame()

    prods = df_prod.set_index("id")[["costo"]].to_dict()["costo"]

    df["costo_unit"] = df["producto_id"].map(prods)
    df["ganancia_unit"] = df["precio_unitario"] - df["costo_unit"]
    df["ganancia_total"] = df["ganancia_unit"] * df["cantidad"]

    result = (
        df.groupby("producto_nombre")
        .agg(
            ganancia_unitaria=("ganancia_unit", "first"),
            cantidad_vendida=("cantidad", "sum"),
            ganancia_total=("ganancia_total", "sum"),
        )
        .reset_index()
        .sort_values("ganancia_total", ascending=False)
    )
    result.columns = ["Producto", "Ganancia/Unidad", "Cant. Vendida", "Ganancia Total"]
    return result


# =============================================
#  TOP PRODUCTOS
# =============================================

def top_productos(n=5):
    df = get_dataframe_ventas()
    if df.empty:
        return pd.DataFrame(columns=["producto_nombre", "cantidad", "ingresos"])
    return (df.groupby("producto_nombre")
            .agg(cantidad=("cantidad", "sum"), ingresos=("subtotal", "sum"))
            .reset_index().sort_values("cantidad", ascending=False).head(n))


def top_productos_por_ingresos(n=5):
    df = get_dataframe_ventas()
    if df.empty:
        return pd.DataFrame(columns=["producto_nombre", "cantidad", "ingresos"])
    return (df.groupby("producto_nombre")
            .agg(cantidad=("cantidad", "sum"), ingresos=("subtotal", "sum"))
            .reset_index().sort_values("ingresos", ascending=False).head(n))


# =============================================
#  TENDENCIAS
# =============================================

def tendencia_ingresos_mensual():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["mes", "ingresos", "num_ventas", "envios"])
    df["mes"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
    return (df.groupby("mes")
            .agg(ingresos=("total", "sum"), num_ventas=("id", "count"), envios=("costo_envio", "sum"))
            .reset_index().sort_values("mes"))


def tendencia_ingresos_semanal():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["semana", "ingresos", "num_ventas"])
    df["semana"] = df["fecha"].dt.to_period("W").apply(lambda r: r.start_time)
    return (df.groupby("semana")
            .agg(ingresos=("total", "sum"), num_ventas=("id", "count"))
            .reset_index().sort_values("semana"))


# =============================================
#  PUNTO DE PEDIDO
# =============================================

def calcular_punto_pedido(dias_analisis=28, tiempo_entrega_dias=7, factor_seguridad=0.2):
    df = get_dataframe_ventas()
    df_productos = get_dataframe_productos()
    if df_productos.empty:
        return pd.DataFrame()

    fecha_corte = datetime.now() - timedelta(days=dias_analisis)
    resultados = []
    for _, prod in df_productos.iterrows():
        pid = prod["id"]
        stock_actual = prod["stock"]
        if not df.empty:
            total_vendido = df[(df["producto_id"] == pid) & (df["fecha"] >= fecha_corte)]["cantidad"].sum()
        else:
            total_vendido = 0

        prom_diario = total_vendido / dias_analisis if dias_analisis > 0 else 0
        prom_semanal = prom_diario * 7
        stock_seg = prom_semanal * factor_seguridad
        pp = (prom_diario * tiempo_entrega_dias) + stock_seg

        if stock_actual <= 0:
            estado = "🔴 Sin Stock"
        elif stock_actual <= pp:
            estado = "🟡 Pedir Ahora"
        elif stock_actual <= pp * 1.5:
            estado = "🟠 Stock Bajo"
        else:
            estado = "🟢 OK"

        resultados.append({
            "Producto": prod["referencia"], "Categoría": prod["categoria"],
            "Stock Actual": int(stock_actual), "Venta Diaria Prom.": round(prom_diario, 1),
            "Venta Semanal Prom.": round(prom_semanal, 1),
            "Stock Seguridad": round(stock_seg, 1),
            "Punto de Pedido": round(pp, 0), "Estado": estado,
        })
    return pd.DataFrame(resultados)


# =============================================
#  AGRUPACIONES
# =============================================

def ventas_por_categoria():
    df = get_dataframe_ventas()
    if df.empty:
        return pd.DataFrame(columns=["categoria", "cantidad", "ingresos"])
    return (df.groupby("categoria")
            .agg(cantidad=("cantidad", "sum"), ingresos=("subtotal", "sum"))
            .reset_index().sort_values("ingresos", ascending=False))


def ventas_por_metodo_pago():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["medio_pago", "total", "num_ventas"])
    return (df.groupby("medio_pago")
            .agg(total=("total", "sum"), num_ventas=("id", "count"))
            .reset_index().sort_values("total", ascending=False))


def ventas_por_estado():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["estado", "total", "num_ventas"])
    return (df.groupby("estado")
            .agg(total=("total", "sum"), num_ventas=("id", "count"))
            .reset_index())


def ventas_por_tipo():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["tipo", "total", "num_ventas"])
    return (df.groupby("tipo")
            .agg(total=("total", "sum"), num_ventas=("id", "count"))
            .reset_index().sort_values("total", ascending=False))


def ventas_por_cliente():
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["cliente", "total", "num_ventas"])
    return (df.groupby("cliente")
            .agg(total=("total", "sum"), num_ventas=("id", "count"))
            .reset_index().sort_values("total", ascending=False))


def ventas_diarias(dias=30):
    df = get_dataframe_ventas_resumen()
    if df.empty:
        return pd.DataFrame(columns=["fecha", "ingresos", "num_ventas"])
    fecha_corte = datetime.now() - timedelta(days=dias)
    df = df[df["fecha"] >= fecha_corte]
    df["dia"] = df["fecha"].dt.date
    return (df.groupby("dia")
            .agg(ingresos=("total", "sum"), num_ventas=("id", "count"))
            .reset_index().sort_values("dia"))


def resumen_gastos():
    df = get_dataframe_gastos()
    if df.empty:
        return pd.DataFrame(columns=["categoria", "total"])
    return (df.groupby("categoria")
            .agg(total=("monto", "sum"), num=("id", "count"))
            .reset_index().sort_values("total", ascending=False))
