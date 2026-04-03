"""
🥥 COCOPOP — Dashboard Inteligente v3.0
Datos reales de INVGASGAN.xlsx · Proveedor Nihao
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import database as db
import analytics as an

st.set_page_config(page_title="Cocopop · Dashboard", page_icon="🥥", layout="wide",
                   initial_sidebar_state="expanded")
db.init_db()
db.cargar_datos_demo()

# ── CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #42210b 0%, #5a3015 50%, #42210b 100%) !important; }
    [data-testid="stSidebar"] * { color: #fefce9 !important; }
    [data-testid="stSidebar"] .stRadio label:hover { background-color: rgba(252,238,33,0.15) !important; border-radius: 8px; padding-left: 4px; }
    [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; z-index: 999999 !important; }
    [data-testid="collapsedControl"] button { background: rgba(219,196,160,0.8) !important; border-radius: 8px !important; border: 1px solid #dbc4a0 !important; }
    [data-testid="collapsedControl"] button:hover { background: rgba(252,238,33,0.9) !important; }
    .main-header { background: linear-gradient(135deg, #42210b 0%, #5a3015 60%, #6b3a1a 100%); padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.5rem; box-shadow: 0 8px 32px rgba(66,33,11,0.3); overflow: hidden; position: relative; }
    .main-header::before { content: ''; position: absolute; top: -50%; right: -20%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(252,238,33,0.15) 0%, transparent 70%); border-radius: 50%; }
    .main-header h1 { color: #fefce9 !important; font-size: 2.2rem !important; font-weight: 800 !important; margin: 0 !important; }
    .main-header p { color: #dbc4a0 !important; font-size: 1rem !important; margin: 0.3rem 0 0 0 !important; font-weight: 300; }
    .main-header .accent { color: #fcee21 !important; font-weight: 600; }
    .kpi-card { background: linear-gradient(145deg, #ffffff, #eff5ff); padding: 1.2rem 1.4rem; border-radius: 14px; border-left: 4px solid #fcee21; box-shadow: 0 4px 15px rgba(66,33,11,0.08); transition: transform 0.2s ease; height: 100%; }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(66,33,11,0.15); }
    .kpi-label { color: #42210b; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.2rem; opacity: 0.7; }
    .kpi-value { color: #42210b; font-size: 1.6rem; font-weight: 700; line-height: 1.2; }
    .kpi-sub { color: #5a3015; font-size: 0.72rem; margin-top: 0.15rem; opacity: 0.55; }
    .section-header { color: #42210b; font-size: 1.3rem; font-weight: 700; margin: 1.8rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #fcee21; display: inline-block; }
    .alert-card { background: linear-gradient(135deg, #fff7e6, #fefce9); border: 1px solid #dbc4a0; border-left: 4px solid #fcee21; border-radius: 12px; padding: 1rem 1.3rem; margin-bottom: 0.8rem; }
    .alert-critical { border-left-color: #e74c3c; background: linear-gradient(135deg, #fef0f0, #fff5f5); }
    .stButton > button { background: linear-gradient(135deg, #42210b, #5a3015) !important; color: #fefce9 !important; border: none !important; border-radius: 10px !important; padding: 0.6rem 2rem !important; font-weight: 600 !important; font-family: 'Outfit' !important; }
    .stButton > button:hover { background: linear-gradient(135deg, #5a3015, #6b3a1a) !important; box-shadow: 0 4px 15px rgba(66,33,11,0.3) !important; }
    [data-testid="stMetricValue"] { color: #42210b !important; font-family: 'Outfit' !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

COCOPOP_COLORS = ["#42210b", "#fcee21", "#dbc4a0", "#5a3015", "#8B6914", "#C4A265", "#6b3a1a", "#E8D44D"]
PLOTLY_LAYOUT = dict(font=dict(family="Outfit, sans-serif", color="#42210b"),
                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                     margin=dict(l=20, r=20, t=40, b=20))


def fmt(valor):
    if valor >= 1_000_000: return f"${valor/1_000_000:,.1f}M"
    elif valor >= 1000: return f"${valor:,.0f}"
    return f"${valor:.0f}"


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 1.5rem 0;">
        <div style="font-size:3rem;">🥥</div>
        <div style="font-size:1.6rem; font-weight:800; color:#fcee21 !important; letter-spacing:2px;">COCOPOP</div>
        <div style="font-size:0.75rem; font-weight:300; color:#dbc4a0 !important; letter-spacing:3px; margin-top:0.2rem;">ACCESORIOS</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    pagina = st.radio("Nav", ["📊 Dashboard", "🛒 Registrar Venta", "📋 Encargos", "📦 Insumos",
                               "💎 Productos", "💰 Gastos", "📈 Ganancia", "🧠 Análisis Inteligente"],
                       label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="text-align:center; font-size:0.7rem; opacity:0.5;">Cocopop v3.0 · 💛</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════
#  📊 DASHBOARD
# ══════════════════════════════════════════
if pagina == "📊 Dashboard":
    st.markdown("""<div class="main-header">
        <h1>🥥 Dashboard <span class="accent">Cocopop</span></h1>
        <p>Panel de control inteligente · Inventario y Ventas</p>
    </div>""", unsafe_allow_html=True)

    k = an.calcular_kpis(30)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ventas Totales</div><div class="kpi-value">{fmt(k["ventas_totales_monto"])}</div><div class="kpi-sub">{k["total_ventas"]} transacciones</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#28a745;"><div class="kpi-label">Recibido</div><div class="kpi-value" style="color:#28a745;">{fmt(k["recibido"])}</div><div class="kpi-sub">Pagado</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#e74c3c;"><div class="kpi-label">Por Cobrar</div><div class="kpi-value" style="color:#e74c3c;">{fmt(k["por_cobrar"])}</div><div class="kpi-sub">Pendiente</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#28a745;"><div class="kpi-label">Ganancia</div><div class="kpi-value" style="color:#28a745;">{fmt(k["ganancia_total"])}</div><div class="kpi-sub">Sobre productos vendidos</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ticket Promedio</div><div class="kpi-value">{fmt(k["ticket_promedio"])}</div><div class="kpi-sub">Por venta</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Costos Envío</div><div class="kpi-value">{fmt(k["costo_envio_total"])}</div><div class="kpi-sub">Acumulado</div></div>', unsafe_allow_html=True)
    with c7:
        clr = '#e74c3c' if k['productos_bajo_stock'] > 0 else '#28a745'
        st.markdown(f'<div class="kpi-card" style="border-left-color:{clr};"><div class="kpi-label">Stock Bajo</div><div class="kpi-value" style="color:{clr};">{k["productos_bajo_stock"]}</div><div class="kpi-sub">Por reabastecer</div></div>', unsafe_allow_html=True)
    with c8:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#f39c12;"><div class="kpi-label">Encargos</div><div class="kpi-value" style="color:#f39c12;">{k["encargos_pendientes"]}</div><div class="kpi-sub">Pendientes · {fmt(k["saldo_encargos"])}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([3, 2])
    with cl:
        st.markdown('<div class="section-header">📈 Tendencia de Ingresos</div>', unsafe_allow_html=True)
        t = an.tendencia_ingresos_mensual()
        if not t.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t["mes"], y=t["ingresos"], mode="lines+markers", name="Ingresos",
                line=dict(color="#42210b", width=3, shape="spline"),
                marker=dict(size=10, color="#fcee21", line=dict(color="#42210b", width=2)),
                fill="tozeroy", fillcolor="rgba(66,33,11,0.08)"))
            fig.update_layout(**PLOTLY_LAYOUT, height=380, xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(66,33,11,0.07)"), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    with cr:
        st.markdown('<div class="section-header">🏆 Top 5 Vendidos</div>', unsafe_allow_html=True)
        top5 = an.top_productos(5)
        if not top5.empty:
            fig = px.bar(top5, x="cantidad", y="producto_nombre", orientation="h", color="ingresos",
                color_continuous_scale=[[0, "#dbc4a0"], [0.5, "#8B6914"], [1, "#42210b"]],
                labels={"producto_nombre": "", "cantidad": "Uds", "ingresos": "Ingresos"})
            fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            fig.update_traces(marker_line_color="#42210b", marker_line_width=1, texttemplate="%{x}", textposition="inside",
                textfont=dict(color="white", size=13, family="Outfit"))
            st.plotly_chart(fig, use_container_width=True)

    c2l, c2r = st.columns(2)
    with c2l:
        st.markdown('<div class="section-header">🏷️ Ventas por Categoría</div>', unsafe_allow_html=True)
        cat = an.ventas_por_categoria()
        if not cat.empty:
            fig = px.pie(cat, values="ingresos", names="categoria", color_discrete_sequence=COCOPOP_COLORS, hole=0.45)
            fig.update_layout(**PLOTLY_LAYOUT, height=350, legend=dict(orientation="h", yanchor="top", y=-0.05))
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=11),
                marker=dict(line=dict(color="#fefce9", width=2)))
            st.plotly_chart(fig, use_container_width=True)
    with c2r:
        st.markdown('<div class="section-header">📊 Estado de Pagos</div>', unsafe_allow_html=True)
        est = an.ventas_por_estado()
        if not est.empty:
            fig = px.pie(est, values="total", names="estado", color="estado",
                color_discrete_map={"PAGADO": "#28a745", "PENDIENTE": "#e74c3c"}, hole=0.5)
            fig.update_layout(**PLOTLY_LAYOUT, height=350)
            fig.update_traces(textposition="inside", textinfo="percent+label+value", textfont=dict(size=12))
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
#  🛒 REGISTRAR VENTA
# ══════════════════════════════════════════
elif pagina == "🛒 Registrar Venta":
    st.markdown("""<div class="main-header"><h1>🛒 Registrar <span class="accent">Venta</span></h1>
        <p>Formulario alineado con estructura INVGASGAN</p></div>""", unsafe_allow_html=True)

    productos = db.get_productos()
    if not productos:
        st.warning("⚠️ Sin productos.")
    else:
        with st.form("form_venta", clear_on_submit=True):
            ct, cn, cc = st.columns([2, 1, 2])
            with ct: tipo = st.selectbox("Tipo", ["VENTA", "ENCARGO", "SORTEO"])
            with cn: num_items = st.number_input("# Productos", min_value=1, max_value=10, value=1)
            with cc: cliente = st.text_input("Cliente *", placeholder="Nombre del cliente")

            items, sub = [], 0
            for i in range(int(num_items)):
                st.markdown(f"**Producto {i+1}**")
                cp, cq = st.columns([3, 1])
                with cp:
                    nombres = [f"{p['referencia']} ({p['categoria']})" for p in productos]
                    sel = st.selectbox("Prod", nombres, key=f"p_{i}", label_visibility="collapsed")
                with cq:
                    cant = st.number_input("Cant", min_value=1, value=1, key=f"c_{i}")
                idx = nombres.index(sel)
                p = productos[idx]
                precio = p["precio_venta"]
                isub = precio * cant
                sub += isub
                items.append({"producto_id": p["id"], "cantidad": cant, "precio_unitario": precio})
                st.caption(f"${precio:,.0f} × {cant} = **${isub:,.0f}**")

            st.markdown("---")
            ca, cb, cc2 = st.columns(3)
            with ca: metodo = st.selectbox("Método Pago", ["CONTADO", "CREDITO"])
            with cb: medio = st.selectbox("Medio Pago", ["EFECTIVO", "TRANSFERENCIA"])
            with cc2: plataforma = st.selectbox("Plataforma", ["", "NEQUI", "BANCOLOMBIA", "LLAVE"])
            ce, ces = st.columns(2)
            with ce: envio = st.number_input("💰 Costo Envío ($)", min_value=0, value=0, step=1000)
            with ces: estado = st.selectbox("Estado", ["PAGADO", "PENDIENTE"])
            notas = st.text_area("📝 Notas", placeholder="Observaciones...")
            total = sub + envio

            st.markdown(f'''<div style="background:linear-gradient(135deg,#42210b,#5a3015);border-radius:12px;padding:1.2rem 1.5rem;margin:1rem 0;display:flex;justify-content:space-between;align-items:center;">
                <div><span style="color:#dbc4a0;font-size:0.85rem;">Subtotal: ${sub:,.0f}</span><br><span style="color:#dbc4a0;font-size:0.85rem;">Envío: ${envio:,.0f}</span></div>
                <div><span style="color:#fcee21;font-size:0.8rem;font-weight:500;">TOTAL</span><br><span style="color:#fefce9;font-size:2rem;font-weight:800;">${total:,.0f}</span></div>
            </div>''', unsafe_allow_html=True)

            if st.form_submit_button("✅ Registrar Venta", use_container_width=True):
                if items and cliente:
                    vid = db.registrar_venta(items, envio, cliente, tipo, metodo, medio, plataforma, estado, notas)
                    st.success(f"✅ Venta #{vid} · {cliente} · ${total:,.0f}")
                    st.balloons()
                else:
                    st.warning("⚠️ Cliente y productos son obligatorios")

    st.markdown('<div class="section-header">📋 Ventas Recientes</div>', unsafe_allow_html=True)
    vr = db.get_ventas(20)
    if vr:
        df = pd.DataFrame(vr)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
        df = df.rename(columns={"id": "#", "fecha": "Fecha", "orden": "Orden", "cliente": "Cliente",
            "tipo": "Tipo", "metodo_pago": "Método", "medio_pago": "Medio", "estado": "Estado",
            "subtotal": "Subtotal", "costo_envio": "Envío", "total": "Total", "pagado": "Pagado", "saldo": "Saldo"})
        st.dataframe(df[["#", "Fecha", "Orden", "Cliente", "Tipo", "Método", "Medio", "Estado", "Total", "Pagado", "Saldo"]],
                      use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
#  📋 ENCARGOS
# ══════════════════════════════════════════
elif pagina == "📋 Encargos":
    st.markdown("""<div class="main-header"><h1>📋 Gestión de <span class="accent">Encargos</span></h1>
        <p>Pedidos personalizados · Abonos y Saldos</p></div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📋 Encargos Activos", "➕ Nuevo Encargo"])
    with t1:
        encs = db.get_encargos()
        if encs:
            df = pd.DataFrame(encs)
            sep = df[df["estado"] == "SEPARADO"]
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Separados", len(sep))
            with c2: st.metric("Por Cobrar", fmt(sep["saldo"].sum()) if not sep.empty else "$0")
            with c3: st.metric("Total Abonado", fmt(df["abono"].sum()))

            st.dataframe(df[["id_encargo", "cliente", "producto", "cantidad", "precio_unitario", "total", "abono", "saldo", "estado", "fecha_entrega"]].rename(
                columns={"id_encargo": "ID", "cliente": "Cliente", "producto": "Producto", "cantidad": "Cant.",
                          "precio_unitario": "P.Unit.", "total": "Total", "abono": "Abono", "saldo": "Saldo",
                          "estado": "Estado", "fecha_entrega": "Entrega"}),
                use_container_width=True, hide_index=True)

            pend = [e for e in encs if e["estado"] == "SEPARADO"]
            if pend:
                st.markdown('<div class="section-header">💵 Registrar Abono</div>', unsafe_allow_html=True)
                with st.form("f_abono"):
                    ops = [f"{e['id_encargo']} — {e['cliente']} — Saldo: ${e['saldo']:,.0f}" for e in pend]
                    sel = st.selectbox("Encargo", ops)
                    ab = st.number_input("Nuevo abono total ($)", min_value=0, step=1000)
                    if st.form_submit_button("💵 Registrar", use_container_width=True):
                        db.update_encargo_abono(pend[ops.index(sel)]["id"], ab)
                        st.success("✅ Abono registrado"); st.rerun()

                st.markdown('<div class="section-header">📦 Entregar</div>', unsafe_allow_html=True)
                with st.form("f_entregar"):
                    ops2 = [f"{e['id_encargo']} — {e['cliente']}" for e in pend]
                    sel2 = st.selectbox("Encargo", ops2)
                    if st.form_submit_button("✅ Marcar Entregado", use_container_width=True):
                        db.update_encargo_estado(pend[ops2.index(sel2)]["id"], "ENTREGADO")
                        st.success("✅ Entregado"); st.rerun()
        else:
            st.info("Sin encargos.")

    with t2:
        with st.form("f_enc", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ide = st.text_input("ID Encargo *", placeholder="4-EN")
                cli = st.text_input("Cliente *")
                prod = st.text_input("Producto *")
            with c2:
                cant = st.number_input("Cantidad", min_value=1, value=1)
                pre = st.number_input("Precio ($)", min_value=0, step=500)
                abo = st.number_input("Abono ($)", min_value=0, step=500)
            fe = st.text_input("Fecha entrega")
            obs = st.text_area("Observaciones")
            if st.form_submit_button("💾 Crear Encargo", use_container_width=True):
                if ide and cli and prod:
                    db.add_encargo(ide, cli, prod, cant, pre, abo, fe, obs)
                    st.success(f"✅ Encargo {ide} creado"); st.rerun()

# ══════════════════════════════════════════
#  📦 INSUMOS
# ══════════════════════════════════════════
elif pagina == "📦 Insumos":
    st.markdown("""<div class="main-header"><h1>📦 Gestión de <span class="accent">Insumos</span></h1>
        <p>Materiales y empaque</p></div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📋 Inventario", "➕ Agregar"])
    with t1:
        ins = db.get_insumos()
        if ins:
            df = pd.DataFrame(ins)
            st.dataframe(df[["nombre", "unidad", "cantidad", "costo_unitario", "proveedor", "punto_pedido"]].rename(
                columns={"nombre": "Insumo", "unidad": "Unidad", "cantidad": "Stock", "costo_unitario": "Costo",
                          "proveedor": "Proveedor", "punto_pedido": "Pto.Pedido"}),
                use_container_width=True, hide_index=True)

            with st.form("f_reab"):
                ci, cq = st.columns([3, 1])
                with ci: isel = st.selectbox("Insumo", [i["nombre"] for i in ins])
                with cq: cadd = st.number_input("Cantidad", min_value=1, value=1)
                if st.form_submit_button("📥 Reabastecer", use_container_width=True):
                    obj = next(i for i in ins if i["nombre"] == isel)
                    db.update_insumo_cantidad(obj["id"], cadd)
                    st.success(f"✅ +{cadd}"); st.rerun()
    with t2:
        with st.form("f_ins", clear_on_submit=True):
            n = st.text_input("Nombre *")
            c1, c2 = st.columns(2)
            with c1:
                u = st.selectbox("Unidad", ["unidades", "paquete", "metros", "gramos"])
                q = st.number_input("Cantidad", min_value=0.0, step=1.0)
            with c2:
                co = st.number_input("Costo ($)", min_value=0, step=100)
                pp = st.number_input("Pto. pedido", min_value=0.0, value=1.0)
            prov = st.text_input("Proveedor")
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                if n: db.add_insumo(n, u, q, co, prov, pp); st.success("✅"); st.rerun()

# ══════════════════════════════════════════
#  💎 PRODUCTOS
# ══════════════════════════════════════════
elif pagina == "💎 Productos":
    st.markdown("""<div class="main-header"><h1>💎 Gestión de <span class="accent">Productos</span></h1>
        <p>Catálogo completo — 65 productos</p></div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📋 Catálogo", "➕ Agregar"])
    with t1:
        prods = db.get_productos()
        if prods:
            df = pd.DataFrame(prods)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Productos", len(df))
            with c2: st.metric("Valor Inventario", fmt(sum(p["precio_venta"] * p["stock"] for p in prods)))
            with c3:
                bajo = len(df[df["stock"] <= df["punto_pedido"]])
                st.metric("Stock Bajo", bajo, delta=f"-{bajo}" if bajo > 0 else "0", delta_color="inverse")

            cats = ["Todas"] + sorted(df["categoria"].unique().tolist())
            cat_f = st.selectbox("Filtrar categoría", cats)
            dff = df if cat_f == "Todas" else df[df["categoria"] == cat_f]

            st.dataframe(dff[["id", "categoria", "referencia", "unidad_medida", "precio_venta", "costo", "stock"]].rename(
                columns={"id": "ID", "categoria": "Categoría", "referencia": "Referencia", "unidad_medida": "Unidad",
                          "precio_venta": "Precio Venta", "costo": "Costo Nihao", "stock": "Stock"}),
                use_container_width=True, hide_index=True)

            with st.form("f_stock"):
                cs, cn = st.columns([3, 1])
                with cs: psel = st.selectbox("Producto", [p["referencia"] for p in prods])
                with cn: ns = st.number_input("Nuevo stock", min_value=0)
                if st.form_submit_button("Actualizar"):
                    o = next(p for p in prods if p["referencia"] == psel)
                    db.update_producto(o["id"], o["categoria"], o["referencia"], o["unidad_medida"],
                                        o["precio_venta"], o["costo"], ns, o["punto_pedido"])
                    st.success(f"✅ Stock → {ns}"); st.rerun()

    with t2:
        with st.form("f_prod", clear_on_submit=True):
            ref = st.text_input("Referencia *")
            c1, c2 = st.columns(2)
            with c1:
                cat = st.selectbox("Categoría", ["ARETES", "ARETES TOPOS", "ARETES ARGOLLAS", "CADENA",
                                                   "PULSERA", "ANILLO", "GAFAS", "SET", "OTRO"])
                uni = st.selectbox("Unidad", ["UNIDAD", "PAR", "SET x3", "SET x2"])
            with c2:
                pv = st.number_input("Precio Venta ($)", min_value=0, step=500)
                cost = st.number_input("Costo Nihao ($)", min_value=0, step=500)
            stk = st.number_input("Stock", min_value=0, value=1)
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                if ref and pv > 0:
                    db.add_producto(cat, ref, uni, pv, cost, stk)
                    st.success(f"✅ '{ref}' agregado"); st.rerun()

# ══════════════════════════════════════════
#  💰 GASTOS
# ══════════════════════════════════════════
elif pagina == "💰 Gastos":
    st.markdown("""<div class="main-header"><h1>💰 Control de <span class="accent">Gastos</span></h1>
        <p>Envíos y empaque — Total: $285,172</p></div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📋 Historial", "➕ Registrar"])
    with t1:
        gastos = db.get_gastos()
        if gastos:
            df = pd.DataFrame(gastos)
            total_g = df["monto"].sum()
            rg = an.resumen_gastos()

            c1, c2 = st.columns(2)
            with c1: st.metric("Total Gastos", fmt(total_g))
            with c2: st.metric("# Movimientos", len(df))

            if not rg.empty:
                fig = px.pie(rg, values="total", names="categoria", color_discrete_sequence=COCOPOP_COLORS, hole=0.45)
                fig.update_layout(**PLOTLY_LAYOUT, height=300)
                st.plotly_chart(fig, use_container_width=True)

            df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d/%m/%Y")
            st.dataframe(df[["fecha", "tipo", "categoria", "descripcion", "medio", "monto"]].rename(
                columns={"fecha": "Fecha", "tipo": "Tipo", "categoria": "Categoría",
                          "descripcion": "Descripción", "medio": "Medio", "monto": "Monto"}),
                use_container_width=True, hide_index=True)

    with t2:
        with st.form("f_gasto", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tipo = st.selectbox("Tipo", ["Variable", "Fijo"])
                cat = st.selectbox("Categoría", ["Envio", "Empaque", "Otro"])
                desc = st.text_input("Descripción", placeholder="Ej: Envio a Colombia")
            with c2:
                med = st.selectbox("Medio", ["Nequi", "Tarjeta", "Efectivo", "Bancolombia"])
                monto = st.number_input("Monto ($)", min_value=0, step=1000)
            if st.form_submit_button("💾 Registrar", use_container_width=True):
                if monto > 0:
                    db.add_gasto(tipo, cat, desc, med, monto)
                    st.success("✅ Gasto registrado"); st.rerun()

# ══════════════════════════════════════════
#  📈 GANANCIA
# ══════════════════════════════════════════
elif pagina == "📈 Ganancia":
    st.markdown("""<div class="main-header"><h1>📈 Análisis de <span class="accent">Ganancia</span></h1>
        <p>Ganancia por producto — Réplica de hoja GANANCIA</p></div>""", unsafe_allow_html=True)

    k = an.calcular_kpis(30)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Ganancia Total", fmt(k["ganancia_total"]))
    with c2: st.metric("Total Gastos", fmt(k["total_gastos"]))
    with c3: st.metric("Ganancia Neta", fmt(k["ganancia_total"] - k["total_gastos"]))

    st.markdown('<div class="section-header">💰 Ganancia por Producto</div>', unsafe_allow_html=True)
    gp = an.ganancia_por_producto()
    if not gp.empty:
        st.dataframe(gp, use_container_width=True, hide_index=True, height=500)

        total_ganancia = gp["Ganancia Total"].sum()
        st.markdown(f"""<div style="background:linear-gradient(135deg,#42210b,#5a3015);border-radius:12px;padding:1.2rem;margin:1rem 0;text-align:center;">
            <span style="color:#fcee21;font-size:0.9rem;">GANANCIA TOTAL</span><br>
            <span style="color:#fefce9;font-size:2.5rem;font-weight:800;">${total_ganancia:,.0f}</span>
        </div>""", unsafe_allow_html=True)

        # Top 10 por ganancia
        top10 = gp.head(10)
        fig = px.bar(top10, x="Ganancia Total", y="Producto", orientation="h",
                     color="Ganancia Total",
                     color_continuous_scale=[[0, "#dbc4a0"], [0.5, "#8B6914"], [1, "#42210b"]],
                     text=top10["Ganancia Total"].apply(lambda x: fmt(x)))
        fig.update_layout(**PLOTLY_LAYOUT, height=400, yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        fig.update_traces(textposition="inside", textfont=dict(color="white", size=12, family="Outfit"))
        st.plotly_chart(fig, use_container_width=True)

    # Clientes top
    st.markdown('<div class="section-header">👥 Ventas por Cliente</div>', unsafe_allow_html=True)
    vc = an.ventas_por_cliente()
    if not vc.empty:
        fig = px.bar(vc.head(10), x="total", y="cliente", orientation="h",
                     color_discrete_sequence=["#42210b"], text=vc.head(10)["total"].apply(lambda x: fmt(x)),
                     labels={"cliente": "", "total": "Total ($)"})
        fig.update_layout(**PLOTLY_LAYOUT, height=380, yaxis=dict(autorange="reversed"))
        fig.update_traces(textposition="inside", textfont=dict(color="white", size=12, family="Outfit"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════
#  🧠 ANÁLISIS INTELIGENTE
# ══════════════════════════════════════════
elif pagina == "🧠 Análisis Inteligente":
    st.markdown("""<div class="main-header"><h1>🧠 Análisis <span class="accent">Inteligente</span></h1>
        <p>Punto de pedido y proyecciones</p></div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: dias = st.slider("Días análisis", 7, 90, 28)
    with c2: te = st.slider("Tiempo entrega (días)", 1, 30, 7)
    with c3: fs = st.slider("Factor seguridad (%)", 10, 50, 20) / 100

    st.markdown("""<div class="alert-card"><strong>🧠 Fórmula:</strong>
        <code>Punto de Pedido = (Prom. ventas diarias × Tiempo entrega) + Stock seguridad</code></div>""", unsafe_allow_html=True)

    pp = an.calcular_punto_pedido(dias, te, fs)
    if not pp.empty:
        def hl(row):
            if "🔴" in str(row["Estado"]): return ["background-color:rgba(231,76,60,0.12)"] * len(row)
            elif "🟡" in str(row["Estado"]): return ["background-color:rgba(252,238,33,0.15)"] * len(row)
            elif "🟠" in str(row["Estado"]): return ["background-color:rgba(243,156,18,0.12)"] * len(row)
            return [""] * len(row)
        st.dataframe(pp.style.apply(hl, axis=1), use_container_width=True, hide_index=True, height=450)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Stock", x=pp["Producto"], y=pp["Stock Actual"], marker_color="#42210b"))
        fig.add_trace(go.Scatter(name="Pto. Pedido", x=pp["Producto"], y=pp["Punto de Pedido"],
            mode="lines+markers", line=dict(color="#e74c3c", width=2, dash="dash"), marker=dict(size=8, color="#e74c3c")))
        fig.update_layout(**PLOTLY_LAYOUT, height=400, xaxis=dict(tickangle=-45, showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(66,33,11,0.07)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">📊 Ventas por Tipo</div>', unsafe_allow_html=True)
    tipos = an.ventas_por_tipo()
    if not tipos.empty:
        fig = px.bar(tipos, x="tipo", y="total", color="tipo", color_discrete_sequence=COCOPOP_COLORS,
                     text="num_ventas", labels={"tipo": "", "total": "Ingresos"})
        fig.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False)
        fig.update_traces(texttemplate="%{text} ventas", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
