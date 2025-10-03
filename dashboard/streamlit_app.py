import os
import pandas as pd
import numpy as np
import streamlit as st
import random

# ===================== Config =====================
st.set_page_config(page_title="HERMIA - Dashboard", layout="wide")
CSV_PATH   = "ingest/readings.csv"
ALERTS_LOG = "dashboard/alerts.csv"

# --- Parametros de estabilidade (anti-alarme falso) ---
WINDOW = 5          # tamanho da janela para avaliar persistencia
MIN_BREACHES = 3    # nro minimo de violacoes na janela para acionar alerta
HYST = {
    "vibration": 0.05,   # margem de histerese
    "air_q":     5,
    "luminosity":50,
    "temperature":2.0
}

# ===================== Utils ======================
def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "ts":"ts","temperature":"temperature","vibration":"vibration","luminosity":"luminosity","air_q":"air_q",
        "TS":"ts","TEMPERATURE":"temperature","VIBRATION":"vibration","LUMINOSITY":"luminosity","AIR_Q":"air_q",
        "TEMPERATURA":"temperature","VIBRACAO":"vibration","LUMINOSIDADE":"luminosity","QUALIDADE_AR":"air_q",
        "timestamp":"ts","datahora":"ts"
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    for c in ["ts","temperature","vibration","luminosity","air_q"]:
        if c not in df.columns:
            df[c] = np.nan
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    return df.sort_values("ts")

def ensure_dirs():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(ALERTS_LOG), exist_ok=True)

def load_csv() -> pd.DataFrame:
    ensure_dirs()
    if not os.path.exists(CSV_PATH):
        ts = pd.date_range(end=pd.Timestamp.now(), periods=50, freq="min")
        demo = pd.DataFrame({
            "ts": ts,
            "temperature": 30 + np.random.randn(50)*0.3,
            "vibration": np.clip(np.random.rand(50)*0.6, 0, None),
            "luminosity": np.random.randint(300, 800, size=50),
            "air_q": np.random.randint(50, 100, size=50)
        })
        demo.to_csv(CSV_PATH, index=False)
    return normalize_cols(pd.read_csv(CSV_PATH))

def save_csv(df: pd.DataFrame):
    ensure_dirs()
    df.to_csv(CSV_PATH, index=False)

def save_alert(regra: str, valor: float, severidade: str = "alta"):
    ensure_dirs()
    cols = ["ts","device_id","regra","valor","severidade","canal","status"]
    if not os.path.exists(ALERTS_LOG):
        pd.DataFrame(columns=cols).to_csv(ALERTS_LOG, index=False)
    log = pd.read_csv(ALERTS_LOG)
    log.loc[len(log)] = [
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "esp32-01", regra, round(float(valor or 0), 3), severidade, "whatsapp", "registrado"
    ]
    log.to_csv(ALERTS_LOG, index=False)

# ===================== App ========================
st.title("HERMIA - Dashboard (Sprint 4)")
st.caption("KPIs + grafico + alertas com severidade + log de evidencias. Anti-alarme falso com janela, histerese e persistencia.")

with st.sidebar:
    st.header("Configuracao")

    serie = st.selectbox(
        "Serie para grafico",
        ["vibration", "air_q", "luminosity", "temperature"],
        key="serie_select",
    )

    # Regras/limiares
    use_vib = st.checkbox("Usar regra de vibracao (>=)", True, key="use_vib")
    vib_thr  = st.slider("Threshold de vibracao (>=)", 0.0, 1.5, 0.8, 0.05, key="vib_thr")

    use_air = st.checkbox("Usar regra de qualidade do ar (<=)", True, key="use_air")
    air_thr  = st.slider("Threshold qualidade do ar (<=)", 0, 100, 60, 1, key="air_thr")

    use_lux = st.checkbox("Usar regra de luminosidade (faixa)", False, key="use_lux")
    lux_low, lux_high = st.slider("Faixa aceitavel (lux)", 200, 900, (300, 800), key="lux_range")

    use_temp = st.checkbox("Usar regra de temperatura (faixa)", False, key="use_temp")
    temp_low, temp_high = st.slider("Faixa aceitavel (C)", 10, 90, (20, 60), key="temp_range")

    st.divider()
    gen_mode = st.selectbox(
        "Modo ao gerar leitura",
        ["normal", "mix (20% baixa)", "forcar baixa", "forcar media", "forcar alta"],
        index=0,
        help="Gera leituras saudaveis, mistura com chance de baixa, ou força uma severidade em uma regra ligada."
    )

    colA, colB = st.columns(2)
    with colA:
        gen_read = st.button("Gerar leitura", key="gen_read")
    with colB:
        force_spike = st.button("Forcar alerta (ALTA)", key="force_spike")

# ---------- Dados ----------
df = load_csv()

# ---------- Helpers de geracao ----------
def healthy_reading(ts=None):
    return {
        "ts": ts or pd.Timestamp.now(),
        "temperature": np.random.normal(28.0, 0.8),
        "vibration":   max(0.0, np.random.normal(0.25, 0.06)),
        "luminosity":  int(np.random.normal(550, 35)),
        "air_q":       int(np.clip(np.random.normal(82, 3), 0, 100))
    }

def apply_severity_to_rule(base, rule, severity):
    """
    Ajusta UMA variavel para violar a regra escolhida respeitando a histerese.
    - 'baixa' fica logo apos a histerese (conta como violacao), mas com distancia pequena.
    - 'media' e 'alta' mais distantes.
    """
    b = dict(base)
    if rule == "vibration":
        if severity == "baixa":  b["vibration"] = float(vib_thr) + HYST["vibration"] + 0.01   # ~0.06 acima
        if severity == "media":  b["vibration"] = float(vib_thr) + 0.20
        if severity == "alta":   b["vibration"] = float(vib_thr) + 0.50
    elif rule == "air_q":
        if severity == "baixa":  b["air_q"] = max(0.0, float(air_thr) - HYST["air_q"] - 1)   # ~6 abaixo
        if severity == "media":  b["air_q"] = max(0.0, float(air_thr) - 12)
        if severity == "alta":   b["air_q"] = max(0.0, float(air_thr) - 30)
    elif rule == "luminosity":
        if severity == "baixa":
            # logo fora da faixa e apos a histerese
            if random.random() < 0.5:
                b["luminosity"] = lux_low - (HYST["luminosity"] + 5)
            else:
                b["luminosity"] = lux_high + (HYST["luminosity"] + 5)
        if severity == "media":
            b["luminosity"] = lux_low - 150 if random.random()<0.5 else lux_high + 150
        if severity == "alta":
            b["luminosity"] = lux_low - 300 if random.random()<0.5 else lux_high + 300
    elif rule == "temperature":
        if severity == "baixa":
            # logo fora da faixa e apos a histerese
            if random.random() < 0.5:
                b["temperature"] = temp_low - (HYST["temperature"] + 0.2)
            else:
                b["temperature"] = temp_high + (HYST["temperature"] + 0.2)
        if severity == "media":
            b["temperature"] = (temp_low - 4) if random.random()<0.5 else (temp_high + 4)
        if severity == "alta":
            b["temperature"] = (temp_low - 8) if random.random()<0.5 else (temp_high + 8)
    return b

def pick_enabled_rules():
    rules = []
    if use_vib:  rules.append("vibration")
    if use_air:  rules.append("air_q")
    if use_lux:  rules.append("luminosity")
    if use_temp: rules.append("temperature")
    return rules

def add_rows(rows):
    global df
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    save_csv(df)

# ---------- Acao: Gerar leitura ----------
if gen_read:
    rules_enabled = pick_enabled_rules()
    now = pd.Timestamp.now()

    if gen_mode == "normal":
        add_rows([healthy_reading(now)])
        st.toast("Leitura saudavel gerada.")

    elif gen_mode == "mix (20% baixa)" and rules_enabled and random.random() < 0.20:
        rule = random.choice(rules_enabled)
        base = healthy_reading(now)
        low  = apply_severity_to_rule(base, rule, "baixa")
        add_rows([low])
        st.toast(f"Leitura com severidade BAIXA em {rule}.")
    elif gen_mode == "mix (20% baixa)":
        add_rows([healthy_reading(now)])
        st.toast("Leitura saudavel gerada.")

    elif gen_mode in ("forcar baixa","forcar media","forcar alta"):
        # Gera 3 leituras consecutivas com a mesma severidade para cumprir persistencia
        rule = random.choice(rules_enabled or ["vibration"])
        rows = []
        for i in range(MIN_BREACHES):
            ts_i = now + pd.Timedelta(seconds=i)
            base = healthy_reading(ts_i)
            sev  = "baixa" if gen_mode.endswith("baixa") else ("media" if gen_mode.endswith("media") else "alta")
            rows.append(apply_severity_to_rule(base, rule, sev))
        add_rows(rows)
        st.toast(f"{MIN_BREACHES} leituras {gen_mode.upper()} em {rule} inseridas.")

# ---------- Acao: Forcar alerta (ALTA garantida) ----------
if force_spike:
    rules_enabled = pick_enabled_rules()
    rule = random.choice(rules_enabled or ["vibration"])
    now = pd.Timestamp.now()
    # 3 leituras ALTA para garantir persistencia + 1 normal para estabilizar depois
    rows = []
    for i in range(MIN_BREACHES):
        base = healthy_reading(now + pd.Timedelta(seconds=i))
        rows.append(apply_severity_to_rule(base, rule, "alta"))
    rows.append(healthy_reading(now + pd.Timedelta(seconds=MIN_BREACHES)))
    add_rows(rows)
    st.toast("Spike ALTA inserido + leitura normal para estabilizar.")

# ---------------- KPIs -------------------
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Leituras", f"{len(df):,}".replace(",", "."))
with col2: st.metric("Vibracao media", f"{df['vibration'].mean():.2f}")
with col3: st.metric("Qualidade do ar media", f"{df['air_q'].mean():.1f}")
with col4: st.metric("Modelo/Regra", "Regras combinadas (anti-alarme falso)")

# --------------- Grafico -----------------
st.subheader("Serie temporal")
if not df.empty:
    plot_df = df[["ts", serie]].dropna().set_index("ts").tail(500)
    st.line_chart(plot_df)
else:
    st.info("Sem dados. Verifique ingest/readings.csv.")

# ======== Alertas (janela + histerese + persistencia) ========
st.subheader("Alertas")
if not df.empty:
    window_df = df.tail(WINDOW).copy()

    def breach_vib(v):
        if pd.isna(v): return False
        return float(v) >= float(vib_thr) + HYST["vibration"]

    def breach_air(a):
        if pd.isna(a): return False
        return float(a) <= float(air_thr) - HYST["air_q"]

    def breach_range(val, low, high, key):
        if pd.isna(val): return False
        v = float(val)
        return v < (low - HYST[key]) or v > (high + HYST[key])

    count_vib = window_df["vibration"].apply(breach_vib).sum() if use_vib else 0
    count_air = window_df["air_q"].apply(breach_air).sum()     if use_air else 0
    count_lux = window_df["luminosity"].apply(lambda x: breach_range(x, lux_low, lux_high, "luminosity")).sum() if use_lux else 0
    count_tmp = window_df["temperature"].apply(lambda x: breach_range(x, temp_low, temp_high, "temperature")).sum() if use_temp else 0

    def sev_vibration(v):
        if pd.isna(v): return None
        dv = float(v) - float(vib_thr)
        if dv < 0: return None
        if dv >= 0.40: return "alta"
        if dv >= 0.15: return "media"
        return "baixa"

    def sev_airq(a):
        if pd.isna(a): return None
        da = float(air_thr) - float(a)
        if da < 0: return None
        if da >= 25: return "alta"
        if da >= 10: return "media"
        return "baixa"

    def sev_out_range(v, low, high, small, big):
        if pd.isna(v): return None
        v = float(v)
        if low <= v <= high: return None
        dist = (low - v) if v < low else (v - high)
        if dist >= big:  return "alta"
        if dist >= small:return "media"
        return "baixa"

    triggered_parts, severities = [], []
    last = window_df.iloc[-1]

    if use_vib and count_vib >= MIN_BREACHES:
        s = sev_vibration(last.get("vibration"))
        if s:
            severities.append(s)
            triggered_parts.append(f"vib>={vib_thr:g} (ult={float(last['vibration']):.2f}, {count_vib}/{WINDOW} viol.) sev={s}")

    if use_air and count_air >= MIN_BREACHES:
        s = sev_airq(last.get("air_q"))
        if s:
            severities.append(s)
            triggered_parts.append(f"air_q<={air_thr:d} (ult={int(float(last['air_q']))}, {count_air}/{WINDOW} viol.) sev={s}")

    if use_lux and count_lux >= MIN_BREACHES:
        s = sev_out_range(last.get("luminosity"), lux_low, lux_high, small=120, big=250)
        if s:
            severities.append(s)
            triggered_parts.append(f"lux fora [{lux_low},{lux_high}] (ult={int(float(last['luminosity']))}, {count_lux}/{WINDOW} viol.) sev={s}")

    if use_temp and count_tmp >= MIN_BREACHES:
        s = sev_out_range(last.get("temperature"), temp_low, temp_high, small=3.0, big=6.0)
        if s:
            severities.append(s)
            triggered_parts.append(f"temp fora [{temp_low},{temp_high}] (ult={float(last['temperature']):.1f} C, {count_tmp}/{WINDOW} viol.) sev={s}")

    LEVEL = {"baixa":1,"media":2,"alta":3}
    overall = max(severities, key=lambda s: LEVEL[s]) if severities else None

    if overall:
        regra = " | ".join(triggered_parts)
        if overall == "alta":
            st.error(f"ALERTA ({overall}): {regra}")
        elif overall == "media":
            st.warning(f"ALERTA ({overall}): {regra}")
        else:
            st.info(f"ALERTA ({overall}): {regra}")
        valor_log = last.get("vibration")
        if pd.isna(valor_log): valor_log = last.get("air_q")
        if pd.isna(valor_log): valor_log = last.get("luminosity")
        if pd.isna(valor_log): valor_log = last.get("temperature")
        save_alert(regra, valor_log, severidade=overall)
    else:
        st.success("Sem alertas persistentes na janela recente.")

# --------------- Log ---------------------
if os.path.exists(ALERTS_LOG):
    st.write("Log de alertas (evidencia):")
    st.dataframe(pd.read_csv(ALERTS_LOG).tail(20), use_container_width=True)

st.caption("Sprint 4: KPIs, grafico, alertas com severidade e log (anti-alarme falso).")

