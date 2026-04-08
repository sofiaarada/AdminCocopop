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
    pagina = st.radio("Nav", ["📊 Dashboard", "🛒 Registrar Venta", "📋 Encargos", "🛍️ Compras", "📦 Insumos",
                               "💎 Productos", "💰 Gastos", "📈 Ganancia", "🧠 Análisis Inteligente", "🧮 Caja"],
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

    # === BUSINESS INTELLIGENCE ===
    st.markdown("---")
    st.markdown('<div class="main-header" style="background: linear-gradient(135deg, #1A1A1D 0%, #4E4E50 100%);"><h1>💡 Business <span style="color:#fcee21;">Intelligence</span></h1><p style="color:#FFF;">Métricas avanzadas y recomendaciones algorítmicas</p></div>', unsafe_allow_html=True)
    
    col_ia, col_m = st.columns([1,2])
    with col_ia:
        ia_text = an.generar_ia_insight()
        st.markdown(f"""<div style='background:linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); padding:1.5rem; border-radius:12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); height:100%;'>
            <h3 style='color:#1A1A1D; font-weight:800; margin-top:0;'>✨ IA Insight Semanal</h3>
            <p style='color:#1A1A1D; font-size:1.1rem; line-height:1.5;'>{ia_text}</p>
        </div>""", unsafe_allow_html=True)
        
    with col_m:
        rr = an.rentabilidad_real()
        ca = an.costo_adquisicion()
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            margen_pct = rr["margen"] * 100
            if margen_pct > 0:
                fig_m = go.Figure(go.Indicator(mode="gauge+number", value=margen_pct, number={"suffix": "%", "font":{"color":"#42210b"}}, title={'text': "Margen Neto", 'font':{'color':"#42210b"}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#28a745" if margen_pct>30 else "#f39c12"}, 'bgcolor': "white", 'steps': [{'range': [0, 20], 'color': "#ffcccb"}]}))
                fig_m.update_layout(height=220, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_m, use_container_width=True)
        with c_m2:
            gast_acq = ca["gastos_adquisicion"]
            vent = ca["ingresos_ventas"]
            fig_bar = go.Figure(data=[go.Bar(name='Ingresos', x=['CAC vs Ventas'], y=[vent], marker_color='#28a745'), go.Bar(name='Costo Adq.', x=['CAC vs Ventas'], y=[gast_acq], marker_color='#e74c3c')])
            fig_bar.update_layout(barmode='group', height=220, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", yanchor="bottom", y=1))
            st.plotly_chart(fig_bar, use_container_width=True)
            
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        st.markdown('<div class="section-header">📈 Flujo de Caja (Evolución)</div>', unsafe_allow_html=True)
        df_flujo = an.flujo_caja(30)
        if not df_flujo.empty:
            fig_f = px.line(df_flujo, x="dia", y="saldo", markers=True, line_shape="spline")
            fig_f.update_traces(line_color='#8B6914', marker=dict(size=8))
            fig_f.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_f, use_container_width=True)
            
    with c_b2:
        st.markdown('<div class="section-header">💸 Top Categorías Egreso</div>', unsafe_allow_html=True)
        df_cat = an.egresos_por_categoria(30)
        if not df_cat.empty:
            fig_c = px.pie(df_cat, values="salida", names="categoria", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_c.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_c, use_container_width=True)
            
    st.markdown('<div class="section-header">📊 Ventas Históricas por Mes</div>', unsafe_allow_html=True)
    ventas_historicas = db.get_ventas(9999)
    if ventas_historicas:
        df_vh = pd.DataFrame(ventas_historicas)
        df_vh["fecha"] = pd.to_datetime(df_vh["fecha"], format='mixed', errors='coerce')
        df_vh["Mes"] = df_vh["fecha"].dt.to_period("M").astype(str)
        ventas_mes = df_vh.groupby("Mes")["total"].sum().reset_index()
        
        fig_vm = px.bar(ventas_mes, x="Mes", y="total", text="total", color_discrete_sequence=['#8B6914'])
        fig_vm.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_vm.update_layout(**PLOTLY_LAYOUT, height=350, yaxis_title="Ingresos ($)", xaxis_title="")
        st.plotly_chart(fig_vm, use_container_width=True)
    else:
        st.info("Sin registros de ventas suficientes.")

# ══════════════════════════════════════════
#  🛒 REGISTRAR VENTA
# ══════════════════════════════════════════
elif pagina == "🛒 Registrar Venta":
    st.markdown("""<div class="main-header"><h1>🛒 Registrar <span class="accent">Venta</span></h1>
        <p>Formulario alineado con estructura INVGASGAN</p></div>""", unsafe_allow_html=True)

    # Get products for selection
    productos = db.get_productos()
    
    if not productos:
        st.warning("⚠️ Sin productos.")
    else:
        # Move num_items outside form to trigger UI update on change
        c_n_items, _ = st.columns([1, 4])
        with c_n_items:
            num_items = st.number_input("# Productos", min_value=1, max_value=20, value=1)

        with st.form("form_venta", clear_on_submit=True):
            ct, cn, cc = st.columns([2, 1, 2])
            with ct: tipo = st.selectbox("Tipo", ["VENTA", "SORTEO"])
            # Moved outside form to allow UI update
            # with cn: num_items = st.number_input("# Productos", min_value=1, max_value=20, value=1)
            with cc: cliente = st.text_input("Cliente *", placeholder="Nombre del cliente")

            c_ord, c_pag = st.columns(2)
            with c_ord: orden_manual = st.number_input("Venta # (Consecutivo)", min_value=0, value=0, help="0 para asignar automático")
            with c_pag: abono = st.number_input("Pagado / Abono ($)", min_value=0, step=1000, value=0, help="Dejar en 0 si Estado es PAGADO y se pagó el 100%")

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
            st.markdown("**Empaque Utilizado (Se descuenta del stock)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: usa_tarjeta = st.checkbox("Incluir Tarjeta presentación")
            with cx2: usa_bolsa = st.checkbox("Incluir Bolsita Beige")
            with cx3: usa_bolsita_magica = st.checkbox("Incluir Bolsita Mágica")

            st.markdown("---")
            ca, cb, cc2 = st.columns(3)
            with ca: metodo = st.selectbox("Método Pago", ["CONTADO", "CREDITO"])
            with cb: medio = st.selectbox("Medio Pago", ["EFECTIVO", "TRANSFERENCIA", "TARJETA"])
            with cc2: plataforma = st.selectbox("Plataforma", ["", "NEQUI", "LLAVE", "BANCOLOMBIA"])
            ce, ces = st.columns(2)
            with ce: envio = st.number_input("💰 Costo Envío ($)", min_value=0, value=0, step=1000)
            with ces: estado = st.selectbox("Estado", ["PAGADO", "PENDIENTE", "SEPARADO"])
            notas = st.text_area("📝 Notas / Observaciones / Fecha Entrega", placeholder="Observaciones...")
            total = sub + envio

            st.markdown(f'''<div style="background:linear-gradient(135deg,#42210b,#5a3015);border-radius:12px;padding:1.2rem 1.5rem;margin:1rem 0;display:flex;justify-content:space-between;align-items:center;">
                <div><span style="color:#dbc4a0;font-size:0.85rem;">Subtotal: ${sub:,.0f}</span><br><span style="color:#dbc4a0;font-size:0.85rem;">Envío: ${envio:,.0f}</span></div>
                <div><span style="color:#fcee21;font-size:0.8rem;font-weight:500;">TOTAL</span><br><span style="color:#fefce9;font-size:2rem;font-weight:800;">${total:,.0f}</span></div>
            </div>''', unsafe_allow_html=True)

            if st.form_submit_button("✅ Registrar (Venta / Encargo)", use_container_width=True):
                if items and cliente:
                    ord_val = orden_manual if orden_manual > 0 else None
                    pag_val = abono if abono > 0 else None
                    vid = db.registrar_venta(items, envio, cliente, tipo, metodo, medio, plataforma, estado, notas, orden=ord_val, pagado_manual=pag_val)
                    
                    insumos_desc = []
                    if usa_tarjeta: insumos_desc.append("Tarjetas presentación (100 pzs)")
                    if usa_bolsa: insumos_desc.append("Bolsitas Beige 8*10cm (50 pzs)")
                    if usa_bolsita_magica: insumos_desc.append("Color mágico (100 pzs)")
                    if insumos_desc: db.descontar_insumos(insumos_desc)
                    
                    st.success(f"✅ {tipo} registrada de {cliente} · ${total:,.0f}")
                    st.balloons()
                else:
                    st.warning("⚠️ Cliente y productos son obligatorios")

    st.markdown('<div class="section-header">📋 Ventas Recientes</div>', unsafe_allow_html=True)
    vr = db.get_ventas(20)
    detalles_all = db.get_ventas_detalladas()
    if vr:
        for v in vr:
            prods = [f"{d['cantidad']}x {d['producto_nombre']}" for d in detalles_all if d["venta_id"] == v["id"]]
            v["producto"] = ", ".join(prods)

        df = pd.DataFrame(vr)
        df["fecha"] = pd.to_datetime(df["fecha"], format='mixed', errors='coerce').dt.strftime("%d/%m/%Y")
        df = df.rename(columns={"id": "#", "fecha": "Fecha", "orden": "Orden", "cliente": "Cliente",
            "tipo": "Tipo", "producto": "Producto(s)", "metodo_pago": "Método", "medio_pago": "Medio", "estado": "Estado",
            "subtotal": "Subtotal", "costo_envio": "Envío", "total": "Total", "pagado": "Pagado", "saldo": "Saldo"})
        st.dataframe(df[["#", "Fecha", "Orden", "Cliente", "Producto(s)", "Tipo", "Método", "Medio", "Estado", "Total", "Pagado", "Saldo"]],
                      use_container_width=True, hide_index=True)
        
        with st.expander("✏️ Editar Información de Venta"):
            v_id_edit = st.selectbox("Seleccionar Venta a Editar", [v["id"] for v in vr], format_func=lambda x: f"Venta #{x} - {next((v['cliente'] for v in vr if v['id']==x), '')}")
            v_sel = next(v for v in vr if v["id"] == v_id_edit)
            v_det = [d for d in detalles_all if d["venta_id"] == v_id_edit]
            
            with st.form("f_edit_venta"):
                st.markdown("**Editar Productos**")
                df_det = pd.DataFrame(v_det)[['producto_nombre', 'cantidad', 'precio_unitario']] if v_det else pd.DataFrame(columns=['producto_nombre', 'cantidad', 'precio_unitario'])
                opciones_prod = [p['referencia'] for p in productos]
                
                edited_items_df = st.data_editor(df_det, num_rows="dynamic", use_container_width=True,
                    column_config={
                        "producto_nombre": st.column_config.SelectboxColumn("Producto", options=opciones_prod, required=True),
                        "cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1, required=True),
                        "precio_unitario": st.column_config.NumberColumn("Precio Unit. ($)", min_value=0, step=500, required=True)
                    })

                st.markdown("---")
                c_e1, c_e2, c_e3 = st.columns(3)
                with c_e1:
                    orden_e = st.number_input("Orden (Consecutivo)", min_value=0, value=int(v_sel["orden"]))
                    cli_e = st.text_input("Cliente", value=v_sel["cliente"])
                    metodo_e = st.selectbox("Método Pago", ["CONTADO", "CREDITO"], index=0 if v_sel["metodo_pago"]=="CONTADO" else 1)
                with c_e2:
                    medios = ["EFECTIVO", "TRANSFERENCIA", "TARJETA"]
                    medio_e = st.selectbox("Medio Pago", medios, index=medios.index(v_sel["medio_pago"]) if v_sel["medio_pago"] in medios else 0)
                    plats = ["", "NEQUI", "BANCOLOMBIA", "LLAVE"]
                    plat_e = st.selectbox("Plataforma", plats, index=plats.index(v_sel["plataforma"]) if v_sel["plataforma"] in plats else 0)
                    envio_e = st.number_input("Costo Envío", min_value=0, step=1000, value=int(v_sel["costo_envio"]))
                with c_e3:
                    est_e = st.selectbox("Estado", ["PAGADO", "PENDIENTE", "SEPARADO"], index=["PAGADO", "PENDIENTE", "SEPARADO"].index(v_sel["estado"]) if v_sel["estado"] in ["PAGADO", "PENDIENTE", "SEPARADO"] else 0)
                    notas_e = st.text_area("Notas", value=v_sel["notas"] or "")
                
                if st.form_submit_button("Actualizar Venta", use_container_width=True):
                    # Convert edited items to backend format
                    nuevos_items = []
                    nombre_a_id = {p['referencia']: p['id'] for p in productos}
                    for _, row in edited_items_df.iterrows():
                        if row["producto_nombre"] in nombre_a_id:
                            nuevos_items.append({
                                "producto_id": nombre_a_id[row["producto_nombre"]], 
                                "cantidad": int(row["cantidad"]), 
                                "precio_unitario": float(row["precio_unitario"])
                            })
                    
                    db.update_venta_info(v_id_edit, cli_e, metodo_e, medio_e, plat_e, est_e, notas_e, 
                                         items=nuevos_items, costo_envio=envio_e, orden=int(orden_e))
                    st.success("✅ Información de venta actualizada y caja sincronizada"); st.rerun()

        with st.expander("🗑️ Eliminar Venta"):
            v_id_elim = st.selectbox("Seleccionar Venta a Eliminar", [v["id"] for v in vr], format_func=lambda x: f"Venta #{x} (Total: {fmt(next(v['total'] for v in vr if v['id']==x))})")
            if st.button("Eliminar permanentemente", type="primary"):
                db.delete_venta(v_id_elim)
                st.success("✅ Venta eliminada, stock restituido y caja actualizada"); st.rerun()

# ══════════════════════════════════════════
#  📋 ENCARGOS
# ══════════════════════════════════════════
elif pagina == "📋 Encargos":
    st.markdown("""<div class="main-header"><h1>📋 Gestión de <span class="accent">Encargos</span></h1>
        <p>Pedidos personalizados · Abonos y Saldos</p></div>""", unsafe_allow_html=True)

    st.info("💡 **Nota:** Esta pestaña es para el seguimiento y gestión manual de encargos personalizados.")
    
    vr = db.get_ventas(500)
    encargos = [v for v in vr if v["tipo"] in ["ENCARGO", "SEPARADO"]]
    
    if encargos:
        detalles_all = db.get_ventas_detalladas()
        for v in encargos:
            prods = [f"{d['cantidad']}x {d['producto_nombre']}" for d in detalles_all if d["venta_id"] == v["id"]]
            v["producto"] = ", ".join(prods)
            
        df = pd.DataFrame(encargos)
        sep = df[df["estado"] != "ENTREGADO"]
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Pendientes / Separados", len(sep))
        with c2: st.metric("Por Cobrar", fmt(sep["saldo"].sum()) if not sep.empty else "$0")
        with c3: st.metric("Abonado Total", fmt(df["pagado"].sum()))

        df["fecha"] = pd.to_datetime(df["fecha"], format='mixed', errors='coerce').dt.strftime("%d/%m/%Y")
        st.dataframe(df[["id", "fecha", "cliente", "producto", "estado", "total", "pagado", "saldo", "notas"]].rename(
            columns={"id": "ID", "fecha": "Fecha", "cliente": "Cliente", "producto": "Producto(s)",
                      "estado": "Estado", "total": "Total", "pagado": "Abono", "saldo": "Saldo", "notas": "Detalles"}),
            use_container_width=True, hide_index=True)

        pend = [e for e in encargos if e["estado"] in ["PENDIENTE", "SEPARADO"]]
        if pend:
            st.markdown('<div class="section-header">💵 Registrar Abono o Entrega</div>', unsafe_allow_html=True)
            with st.form("f_abono_encargo"):
                ops = [f"#{e['id']} — {e['cliente']} — Saldo: ${e['saldo']:,.0f}" for e in pend]
                sel = st.selectbox("Encargo", ops)
                ab = st.number_input("Adicionar Abono ($)", min_value=0, step=1000, help="Este valor se sumará a lo que ya está pagado")
                if st.form_submit_button("💵 Registrar Abono", use_container_width=True):
                    enc_id = pend[ops.index(sel)]["id"]
                    nuevo_abo_total = pend[ops.index(sel)]["pagado"] + ab
                    db.update_abono_venta(enc_id, nuevo_abo_total)
                    st.success(f"✅ Abono registrado sumando ${ab:,.0f}"); st.rerun()

            with st.form("f_entregar_encargo"):
                ops2 = [f"#{e['id']} — {e['cliente']} (Estado actual: {e['estado']})" for e in pend]
                sel2 = st.selectbox("Encargo a entregar (Cambia estado a ENTREGADO)", ops2)
                if st.form_submit_button("✅ Marcar como Entregado", use_container_width=True):
                    e_obj = pend[ops2.index(sel2)]
                    db.update_venta_info(e_obj["id"], e_obj["cliente"], e_obj["metodo_pago"], e_obj["medio_pago"], e_obj["plataforma"], "ENTREGADO", e_obj["notas"], orden=e_obj["orden"], costo_envio=e_obj["costo_envio"])
                    st.success("✅ Encargo Entregado registrado"); st.rerun()
    else:
        st.info("Sin encargos registrados.")

    with st.expander("➕ Crear Nuevo Encargo"):
        with st.form("f_nuevo_encargo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                id_enc = st.text_input("ID Encargo (Ref)", placeholder="Ej: 150-EN")
                cli = st.text_input("Cliente *")
                prod = st.text_input("Producto(s) *")
            with col2:
                cant = st.number_input("Cantidad", min_value=1, value=1)
                prec = st.number_input("Precio Unitario ($)", min_value=0, step=1000)
                abo = st.number_input("Abono Inicial ($)", min_value=0, step=1000)
            
            fe = st.text_input("Fecha Entrega", placeholder="Ej: Próximo lunes")
            obs = st.text_area("Observaciones")
            
            if st.form_submit_button("💾 Guardar Encargo", use_container_width=True):
                if cli and prod:
                    db.add_encargo(id_enc, cli, prod, cant, prec, abo, fe, obs)
                    st.success("✅ Encargo guardado exitosamente"); st.rerun()
                else:
                    st.error("⚠️ Cliente y Producto son obligatorios")

# ══════════════════════════════════════════
#  🛍️ COMPRAS
# ══════════════════════════════════════════
elif pagina == "🛍️ Compras":
    st.markdown("""<div class="main-header"><h1>🛍️ Registro de <span class="accent">Compras</span></h1>
        <p>Histórico para el contador · No afecta inventario ni caja automática</p></div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📋 Historial de Compras", "➕ Registrar Compra"])
    
    with t1:
        compras = db.get_compras(200)
        if compras:
            df_c = pd.DataFrame(compras)
            st.markdown("💡 **Edición Directa:** Puedes editar la fecha, proveedor, producto y costos en la tabla.")
            
            df_c["fecha"] = pd.to_datetime(df_c["fecha"], format='mixed', errors='coerce').dt.strftime("%Y-%m-%d")
            
            edited_compras = st.data_editor(df_c[["id", "fecha", "proveedor", "producto", "cantidad", "costo_unitario", "costo_total"]].rename(
                columns={"fecha": "Fecha", "proveedor": "Proveedor", "producto": "Producto", "cantidad": "Cant", "costo_unitario": "Costo Unit.", "costo_total": "Total"}),
                use_container_width=True, hide_index=True)
            
            if st.button("💾 Guardar Cambios en Compras", type="primary"):
                for i, row in edited_compras.iterrows():
                    orig = df_c.iloc[0] # Note: simpler check or loop comparison
                    db.update_compra(row["id"], row["Fecha"], row["Proveedor"], row["Producto"], row["Cant"], row["Costo Unit."])
                st.success("✅ Historial de compras actualizado."); st.rerun()
                
            with st.expander("🗑️ Eliminar Registro"):
                id_del = st.selectbox("ID a eliminar", df_c["id"])
                if st.button("Eliminar permanentemente", type="primary", key="del_compra"):
                    db.delete_compra(id_del)
                    st.success("✅ Registro eliminado"); st.rerun()
        else:
            st.info("No hay registros de compras.")

    with t2:
        with st.form("f_nueva_compra", clear_on_submit=True):
            fc = st.text_input("Fecha", value=datetime.now().strftime("%Y-%m-%d"))
            pv = st.text_input("Proveedor", value="Nihao")
            pd = st.text_input("Producto / Descripción")
            cc1, cc2 = st.columns(2)
            with cc1: ca = st.number_input("Cantidad", min_value=1, value=1)
            with cc2: cu = st.number_input("Costo Unitario ($)", min_value=0, step=100)
            
            if st.form_submit_button("✅ Guardar Compra"):
                if pd:
                    db.add_compra(fc, pv, pd, ca, cu)
                    st.success("✅ Compra registrada"); st.rerun()
                else:
                    st.warning("⚠️ El producto es obligatorio")

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
            
            st.markdown("⚠️ Puedes editar directamente el **Stock** y **Número de Pedido** en la tabla y presionar `Enter`.")
            
            df_edit = st.data_editor(df[["id", "nombre", "unidad", "cantidad", "costo_unitario", "proveedor", "punto_pedido"]].rename(
                columns={"nombre": "Insumo", "unidad": "Unidad", "cantidad": "Cantidad (Stock)", "costo_unitario": "Costo",
                          "proveedor": "Proveedor", "punto_pedido": "Número de Pedido"}),
                use_container_width=True, hide_index=True, disabled=["id", "Insumo", "Unidad", "Costo", "Proveedor"])
            
            if st.button("💾 Guardar Cambios de Inventario", type="primary"):
                for i, row in df_edit.iterrows():
                    orig = df.iloc[i]
                    if orig["cantidad"] != row["Stock"] or orig["punto_pedido"] != row["Número de Pedido"]:
                        db.update_insumo(orig["id"], orig["nombre"], orig["unidad"], row["Stock"], orig["costo_unitario"], orig["proveedor"], row["Número de Pedido"])
                st.success("Inventario actualizado masivamente."); st.rerun()

            st.markdown("---")
            with st.expander("📥 Reabastecer Rápido"):
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
                
    ins_all = db.get_insumos()
    if ins_all:
        with st.expander("✏️ Editar Insumo"):
            i_id_edit = st.selectbox("Seleccionar Insumo a Editar", [i["id"] for i in ins_all], format_func=lambda x: f"{next((i['nombre'] for i in ins_all if i['id']==x), '')}", key="edit_ins")
            ins_sel = next(i for i in ins_all if i["id"] == i_id_edit)
            with st.form("f_edit_ins"):
                n_e = st.text_input("Nombre", value=ins_sel["nombre"])
                c1_e, c2_e = st.columns(2)
                with c1_e:
                    u_e = st.selectbox("Unidad", ["unidades", "paquete", "metros", "gramos"], index=["unidades", "paquete", "metros", "gramos"].index(ins_sel["unidad"]) if ins_sel["unidad"] in ["unidades", "paquete", "metros", "gramos"] else 0)
                    q_e = st.number_input("Cantidad", min_value=0.0, step=1.0, value=float(ins_sel["cantidad"]))
                with c2_e:
                    co_e = st.number_input("Costo unitario ($)", min_value=0, step=100, value=int(ins_sel["costo_unitario"]))
                    pp_e = st.number_input("Pto. pedido", min_value=0.0, value=float(ins_sel["punto_pedido"]))
                prov_e = st.text_input("Proveedor", value=ins_sel["proveedor"] or "")
                if st.form_submit_button("Actualizar Insumo"):
                    db.update_insumo(i_id_edit, n_e, u_e, q_e, co_e, prov_e, pp_e)
                    st.success("✅ Insumo actualizado"); st.rerun()
                    
        with st.expander("🗑️ Eliminar Insumo"):
            i_id_elim = st.selectbox("Seleccionar Insumo a Eliminar", [i["id"] for i in ins_all], format_func=lambda x: f"{next((i['nombre'] for i in ins_all if i['id']==x), '')}")
            if st.button("Eliminar insumo", type="primary"):
                db.delete_insumo(i_id_elim)
                st.success("✅ Insumo inhabilitado"); st.rerun()

# ══════════════════════════════════════════
#  💎 PRODUCTOS
# ══════════════════════════════════════════
elif pagina == "💎 Productos":
    st.markdown("""<div class="main-header"><h1>💎 Gestión de <span class="accent">Productos</span></h1>
        <p>Catálogo completo — 65 productos</p></div>""", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📋 Catálogo", "➕ Agregar", "💰 Análisis de Costos"])
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
                          "precio_venta": "Precio Venta", "costo": "Precio de Compra", "stock": "Stock"}),
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
                cost = st.number_input("Precio de Compra ($)", min_value=0, step=500)
            stk = st.number_input("Stock", min_value=0, value=1)
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                if ref and pv > 0:
                    db.add_producto(cat, ref, uni, pv, cost, stk)
                    st.success(f"✅ '{ref}' agregado"); st.rerun()

    prods_all = db.get_productos()
    if prods_all:
        with st.expander("✏️ Editar Producto"):
            p_id_edit = st.selectbox("Seleccionar Producto a Editar", [p["id"] for p in prods_all], format_func=lambda x: f"{next((p['referencia'] for p in prods_all if p['id']==x), '')}", key="edit_prod")
            prod_sel = next(p for p in prods_all if p["id"] == p_id_edit)
            with st.form("f_edit_prod"):
                ref_e = st.text_input("Referencia", value=prod_sel["referencia"])
                c1_e, c2_e = st.columns(2)
                with c1_e:
                    cats = ["ARETES", "ARETES TOPOS", "ARETES ARGOLLAS", "CADENA", "PULSERA", "ANILLO", "GAFAS", "SET", "OTRO"]
                    idx_cat = cats.index(prod_sel["categoria"]) if prod_sel["categoria"] in cats else 8
                    cat_e = st.selectbox("Categoría", cats, index=idx_cat)
                    unis = ["UNIDAD", "PAR", "SET x3", "SET x2"]
                    idx_uni = unis.index(prod_sel["unidad_medida"]) if prod_sel["unidad_medida"] in unis else 0
                    uni_e = st.selectbox("Unidad", unis, index=idx_uni)
                with c2_e:
                    pv_e = st.number_input("Precio Venta ($)", min_value=0, step=500, value=int(prod_sel["precio_venta"]))
                    cost_e = st.number_input("Precio de Compra ($)", min_value=0, step=500, value=int(prod_sel["costo"]))
                stk_e = st.number_input("Stock", min_value=0, value=int(prod_sel["stock"]))
                pp_e = st.number_input("Punto Pedido", min_value=0, value=int(prod_sel["punto_pedido"]))
                if st.form_submit_button("Actualizar Producto"):
                    db.update_producto(p_id_edit, cat_e, ref_e, uni_e, pv_e, cost_e, stk_e, pp_e)
                    st.success("✅ Producto actualizado"); st.rerun()
                    
        with st.expander("🗑️ Eliminar Producto"):
            p_id_elim = st.selectbox("Seleccionar Producto a Eliminar", [p["id"] for p in prods_all], format_func=lambda x: f"{next((p['referencia'] for p in prods_all if p['id']==x), '')}")
            if st.button("Eliminar producto", type="primary"):
                db.delete_producto(p_id_elim)
                st.success("✅ Producto inhabilitado"); st.rerun()

    with t3:
        st.markdown('<div class="section-header">💰 Análisis Inteligente de Costos y Rentabilidad</div>', unsafe_allow_html=True)
        st.markdown("Ajusta el costo promedio estimado de Envío y Empaque por producto para recalcular el margen de utilidad.")
        envio_empaque_base = st.number_input("Costo base Envío + Empaque ($)", min_value=0, value=3500, step=100)
        
        df_costs = an.calcular_analisis_costos(envio_empaque_base)
        
        if not df_costs.empty:
            # Editable table for basic fields
            edited_df = st.data_editor(df_costs, 
                column_config={
                    "id": None, 
                    "categoria": None,
                    "Referencia": st.column_config.TextColumn("Referencia", disabled=True),
                    "Costo Compra": st.column_config.NumberColumn("Costo Compra ($)", min_value=0, step=500),
                    "Gastos Env/Emp": st.column_config.NumberColumn("Gastos Env/Emp", disabled=True),
                    "Costo Total": st.column_config.NumberColumn("Costo Total", disabled=True),
                    "Precio Venta": st.column_config.NumberColumn("Precio Venta ($)", min_value=0, step=500),
                    "Utilidad": st.column_config.NumberColumn("Utilidad ($)", disabled=True),
                    "Margen %": st.column_config.TextColumn("Margen %", disabled=True),
                    "Estado": st.column_config.TextColumn("Estado", disabled=True),
                },
                use_container_width=True, hide_index=True, key="editor_costos_new")
            
            if st.button("💾 Guardar Cambios en Productos", use_container_width=True):
                # Check for changes by comparing with original prods_all
                cambios = 0
                for index, row in edited_df.iterrows():
                    p_orig = next(p for p in prods_all if p["id"] == row["id"])
                    if p_orig["costo"] != row["Costo Compra"] or p_orig["precio_venta"] != row["Precio Venta"]:
                        db.update_producto(row["id"], p_orig["categoria"], p_orig["referencia"], p_orig["unidad_medida"],
                                            row["Precio Venta"], row["Costo Compra"], p_orig["stock"], p_orig["punto_pedido"])
                        cambios += 1
                
                if cambios > 0:
                    st.success(f"✅ Se actualizaron {cambios} productos correctamente.")
                    st.rerun()
                else:
                    st.info("No se detectaron cambios para guardar.")

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

            df["fecha"] = pd.to_datetime(df["fecha"], format='mixed', errors='coerce').dt.strftime("%d/%m/%Y")
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

    gastos_all = db.get_gastos()
    if gastos_all:
        with st.expander("✏️ Editar Gasto"):
            g_id_edit = st.selectbox("Seleccionar Gasto a Editar", [g["id"] for g in gastos_all], format_func=lambda x: f"{next((g['categoria'] for g in gastos_all if g['id']==x), '')} - {fmt(next((g['monto'] for g in gastos_all if g['id']==x), 0))}", key="edit_gasto")
            gasto_sel = next(g for g in gastos_all if g["id"] == g_id_edit)
            with st.form("f_edit_gasto"):
                c1_e, c2_e = st.columns(2)
                with c1_e:
                    tipos = ["Variable", "Fijo"]
                    t_idx = tipos.index(gasto_sel["tipo"]) if gasto_sel["tipo"] in tipos else 0
                    tipo_e = st.selectbox("Tipo", tipos, index=t_idx)
                    cats = ["Envio", "Empaque", "Otro"]
                    c_idx = cats.index(gasto_sel["categoria"]) if gasto_sel["categoria"] in cats else 2
                    cat_e = st.selectbox("Categoría", cats, index=c_idx)
                    desc_e = st.text_input("Descripción", value=gasto_sel["descripcion"] or "")
                with c2_e:
                    meds = ["Nequi", "Tarjeta", "Efectivo", "Bancolombia"]
                    m_idx = meds.index(gasto_sel["medio"]) if gasto_sel["medio"] in meds else 0
                    med_e = st.selectbox("Medio", meds, index=m_idx)
                    monto_e = st.number_input("Monto ($)", min_value=0, step=1000, value=int(gasto_sel["monto"]))
                if st.form_submit_button("Actualizar Gasto"):
                    db.update_gasto(g_id_edit, tipo_e, cat_e, desc_e, med_e, monto_e)
                    st.success("✅ Gasto actualizado"); st.rerun()
                    
        with st.expander("🗑️ Eliminar Gasto"):
            g_id_elim = st.selectbox("Seleccionar Gasto a Eliminar", [g["id"] for g in gastos_all], format_func=lambda x: f"{next((g['categoria'] for g in gastos_all if g['id']==x), '')} - {fmt(next((g['monto'] for g in gastos_all if g['id']==x), 0))}")
            if st.button("Eliminar gasto", type="primary"):
                db.delete_gasto(g_id_elim)
                st.success("✅ Gasto eliminado y caja actualizada"); st.rerun()

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

    # Top 10 by profit (this was the previous section)
    pass

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

# ══════════════════════════════════════════
#  🧮 CAJA
# ══════════════════════════════════════════
elif pagina == "🧮 Caja":
    st.markdown("""<div class="main-header"><h1>🧮 Módulo de <span class="accent">Caja</span></h1>
        <p>Libro Diario · Control de Ingresos y Egresos</p></div>""", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["📋 Libro Diario", "➕ Nuevo Movimiento", "✏️ Editar Movimiento", "🗑️ Eliminar"])
    
    caja = db.get_caja()
    
    with t1:
        if caja:
            df = pd.DataFrame(caja)
            ingresos = df[df["tipo"] == "INGRESO"]["entrada"].sum()
            egresos = df[df["tipo"] == "EGRESO"]["salida"].sum()
            saldo_actual = df.iloc[0]["saldo"] if not df.empty else 0
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card" style="border-left-color:#28a745;"><div class="kpi-label">💰 Total Ingresos</div><div class="kpi-value" style="color:#28a745;">{fmt(ingresos)}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card" style="border-left-color:#e74c3c;"><div class="kpi-label">💸 Total Egresos</div><div class="kpi-value" style="color:#e74c3c;">{fmt(egresos)}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card" style="border-left-color:#3498db;"><div class="kpi-label">🏦 Saldo Actual</div><div class="kpi-value" style="color:#3498db;">{fmt(saldo_actual)}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            df_show = df[["id", "fecha", "tipo", "categoria", "origen", "medio_pago", "entrada", "salida", "saldo", "estado"]].copy()
            df_show["fecha"] = pd.to_datetime(df_show["fecha"], format='mixed', errors='coerce').dt.strftime("%Y-%m-%d %H:%M")
            df_show = df_show.rename(columns={"fecha": "Fecha", "tipo": "Tipo", "categoria": "Categoría", "origen": "Origen", "medio_pago": "Medio de Pago", "entrada": "Entrada", "salida": "Salida", "saldo": "Saldo", "estado": "Estado"})
            
            st.dataframe(df_show, use_container_width=True, hide_index=True, height=500)
            
            csv = df_show.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Exportar Caja (Backup CSV)", data=csv, file_name='cocopop_caja_backup.csv', mime='text/csv')
        else:
            st.info("La caja está vacía.")

    with t2:
        with st.form("f_add_caja", clear_on_submit=True):
            st.subheader("Registrar Movimiento Manual")
            c1_a, c2_a = st.columns(2)
            with c1_a:
                fecha_a = st.text_input("Fecha", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                tipo_a = st.selectbox("Tipo de Movimiento", ["INGRESO", "EGRESO"])
                cat_a = st.text_input("Categoría", placeholder="Ej: Ajuste de inventario, Honorarios, Otros")
            with c2_a:
                origen_a = st.text_input("Origen/Descripción", value="Manual")
                medio_a = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Nequi", "Tarjeta", "Otro"])
                monto_a = st.number_input("Monto ($)", min_value=1, step=1000)
                estado_a = st.selectbox("Estado", ["Confirmado", "Pendiente"])
            
            if st.form_submit_button("✅ Guardar Movimiento", use_container_width=True):
                entrada_a = monto_a if tipo_a == "INGRESO" else 0
                salida_a = monto_a if tipo_a == "EGRESO" else 0
                db.add_movimiento_caja(fecha_a, tipo_a, cat_a, origen_a, medio_a, entrada_a, salida_a, estado_a)
                st.success("✅ Movimiento registrado y caja actualizada."); st.rerun()

    if caja:
        with t3:
            c_id_edit = st.selectbox("Seleccionar Movimiento a Editar", [c["id"] for c in caja], format_func=lambda x: f"Ref #{x} · {next((c['fecha'] for c in caja if c['id']==x), '')} · {next((c['tipo'] for c in caja if c['id']==x), '')} {fmt(next((c['entrada'] if c['tipo']=='INGRESO' else c['salida'] for c in caja if c['id']==x), 0))}")
            c_sel = next(c for c in caja if c["id"] == c_id_edit)
            
            with st.form("f_edit_caja"):
                c1_e, c2_e = st.columns(2)
                with c1_e:
                    fecha_e = st.text_input("Fecha", value=c_sel["fecha"])
                    tipos = ["INGRESO", "EGRESO"]
                    tipo_idx = tipos.index(c_sel["tipo"]) if c_sel["tipo"] in tipos else 0
                    tipo_e = st.selectbox("Tipo de Movimiento", tipos, index=tipo_idx)
                    cat_e = st.text_input("Categoría", value=c_sel["categoria"])
                with c2_e:
                    medios = ["Efectivo", "Transferencia", "Nequi", "Tarjeta", "Otro"]
                    medio_idx = medios.index(c_sel["medio_pago"]) if c_sel["medio_pago"] in medios else 0
                    medio_e = st.selectbox("Medio de Pago", medios, index=medio_idx)
                    ent_e = st.number_input("Entrada ($)", min_value=0, step=1000, value=int(c_sel["entrada"]))
                    sal_e = st.number_input("Salida ($)", min_value=0, step=1000, value=int(c_sel["salida"]))
                    estados = ["Confirmado", "Pendiente"]
                    estado_idx = estados.index(c_sel["estado"]) if c_sel["estado"] in estados else 0
                    estado_e = st.selectbox("Estado", estados, index=estado_idx)

                if st.form_submit_button("Actualizar Movimiento", use_container_width=True):
                    db.update_movimiento_caja(c_id_edit, fecha_e, tipo_e, cat_e, medio_e, ent_e, sal_e, estado_e)
                    st.success("✅ Movimiento actualizado"); st.rerun()

        with t4:
            st.warning("⚠️ Al eliminar un movimiento de caja se recalcularán todos los saldos automáticamente.")
            c_id_elim = st.selectbox("Seleccionar Movimiento a Eliminar", [c["id"] for c in caja], format_func=lambda x: f"Ref #{x} · {next((c['fecha'] for c in caja if c['id']==x), '')} · {next((c['tipo'] for c in caja if c['id']==x), '')} {fmt(next((c['entrada'] if c['tipo']=='INGRESO' else c['salida'] for c in caja if c['id']==x), 0))}", key="elim_c")
            if st.button("🗑️ Eliminar Movimiento", type="primary", use_container_width=True):
                db.delete_movimiento_caja(c_id_elim)
                st.success("✅ Movimiento eliminado correctamente"); st.rerun()
