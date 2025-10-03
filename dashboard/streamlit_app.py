import os
import pandas as pd
import numpy as np
import streamlit as st

# ---------------- Config ----------------
st.set_page_config(page_title="HERMIA – Dashboard", layout="wide")
CSV_PATH   = "ingest/readings.csv"
ALERTS_LOG = "dashboard/alerts.csv"

# ------------ Funções de dados ----------
def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    # mapeia cabeçalhos (funciona com maiúsculas, PT e EN)
    rename_map = {
        # inglês
        "ts":"ts","temperature":"temperature","vibration":"vibration",
        "luminosity":"luminosity","air_q":"air_q",
        # inglês MAIÚSCULO
        "TS":"ts","TEMPERATURE":"temperature","VIBRATION":"vibration",
        "LUMINOSITY":"luminosity","AIR_Q":"air_q",
        # português
        "TEMPERATURA":"temperature","VIBRACAO":"vibration",
        "LUMINOSIDADE":"luminosity","QUALIDADE_AR":"air_q",
        "timestamp":"ts","datahora":"ts"
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    # garante colunas faltantes
    for c in ["ts","temperature","vibration","luminosity","air_q"]:
        if c not in df.columns:
            df[c] = np.nan
    # timestamp ordenado
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df.sort_values("ts")
    return df

def load_csv() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        # gera um CSV demo se não existir
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        ts = pd.date_range(end=pd.Timestamp.now(), periods=50, freq="min")
        demo = pd.DataFrame({
            "ts": ts,
            "temperature": 30 + np.random.randn(50)*0.3,
            "vibration": np.clip(np.random.rand(50)*0.6, 0, None),
            "luminosity": np.random.randint(300, 800, size=50),
            "air_q": np.random.randint(50, 100, size=50)  # 0-100
        })
        demo.to_csv(CSV_PATH, index=False)
    return normalize_cols(pd.read_csv(CSV_PATH))

def save_alert(regra: str, valor: float, severidade: str = "alta"):
    os.makedirs(os.path.dirname(ALERTS_LOG), exist_ok=True)
    cols = ["ts","device_id","regra","valor","severidade","canal","status"]
    if not os.path.exists(ALERTS_LOG):
        pd.DataFrame(columns=cols).to_csv(ALERTS_LOG, index=False)
    log = pd.read_csv(ALERTS_LOG)
    log.loc[len(log)] = [
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "esp32-01", regra, round(float(valor or 0), 3), severidade, "whatsapp", "registrado"
    ]
    log.to_csv(ALERTS_LOG, index=False)

# --------------- UI / Sidebar ----------
st.title("HERMIA – Dashboard (Sprint 4)")
st.caption("KPIs + gráfico + alerta mínimo (com evidência em log).")

with st.sidebar:
    st.header("Configuração")
    serie = st.selectbox("Série para gráfico", ["vibration","air_q","luminosity","temperature"])
    vib_thr = st.slider("Threshold de vibração (≥)", 0.0, 1.5, 0.8, 0.05)
    air_thr = st.slider("Threshold qualidade do ar (≤)", 0, 100, 60, 1)  # 0-100
    simulate = st.button("Simular spike (forçar alerta)")

# --------------- Carregar dados ----------
df = load_csv()

# Simula um pico para evidência rápida
if simulate and not df.empty:
    last = df.iloc[-1].copy()
    last["ts"] = pd.Timestamp.now()
    last["vibration"] = max(1.2, float(last.get("vibration") or 0))
    last["air_q"] = min(40, int(last.get("air_q") or 100))
    df = pd.concat([df, pd.DataFrame([last])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    st.toast("Spike simulado inserido.")

# ---------------- KPIs -------------------
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Leituras", f"{len(df):,}".replace(",", "."))
with col2: st.metric("Vibração média", f"{df['vibration'].mean():.2f}")
with col3: st.metric("Qualidade do ar média", f"{df['air_q'].mean():.1f}")
with col4: st.metric("Modelo/Regra", "Regra simples")

# --------------- Gráfico -----------------
st.subheader("Série temporal")
if not df.empty:
    plot_df = df[["ts", serie]].dropna().set_index("ts").tail(500)
    st.line_chart(plot_df)
else:
    st.info("Sem dados. Verifique ingest/readings.csv.")

# --------------- Alertas -----------------
st.subheader("Alertas")
if not df.empty:
    last = df.iloc[-1]
    trig_vib = pd.notna(last.get("vibration")) and float(last["vibration"]) >= vib_thr
    trig_air = pd.notna(last.get("air_q")) and float(last["air_q"]) <= air_thr
    if trig_vib or trig_air:
        partes = []
        if trig_vib: partes.append(f"vib≥{vib_thr:g} (vib={float(last['vibration']):.2f})")
        if trig_air: partes.append(f"air_q≤{air_thr:d} (air_q={int(float(last['air_q']))})")
        regra = " | ".join(partes)
        st.error(f"⚠️ ALERTA: {regra}")
        save_alert(regra, last.get("vibration"))
    else:
        st.success("Sem alertas na última leitura.")

# Log (evidência)
if os.path.exists(ALERTS_LOG):
    st.write("**Log de alertas (evidência):**")
    st.dataframe(pd.read_csv(ALERTS_LOG).tail(20), use_container_width=True)

st.caption("Atende à Sprint 4: KPIs + 1 gráfico + 1 alerta mínimo (com evidência em log).")
