#!/usr/bin/env python3
# coding: utf-8
"""
pipeline_sensor5.py - Versão com detecção automática de colunas,
joins flexíveis e geração de dashboards interativos (Plotly).

Inclui funções robustas de salvamento para evitar PermissionError em
ambientes Windows/OneDrive (tenta chmod, grava em tmp e faz replace).
"""

import os
import tempfile
import stat
import logging
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("pipeline_sensor5")


# --- Funções utilitárias ---
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def safe_merge(left, right, on, how="left"):
    """Faz merge apenas se as colunas existirem em ambos os DataFrames"""
    if left is None or right is None:
        return left
    if on in left.columns and on in right.columns:
        return left.merge(right, on=on, how=how)
    else:
        logger.warning("Merge ignorado: coluna '%s' não existe em ambos os DataFrames", on)
        return left


# --- Funções de gravação robusta (lida com PermissionError / readonly / OneDrive) ---
def _ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent:
        ensure_dir(parent)


def _remove_readonly_if_exists(path):
    if os.path.exists(path):
        try:
            os.chmod(path, stat.S_IWRITE)
            logger.debug("Atributo readonly removido (se existia) em: %s", path)
        except Exception as e:
            logger.debug("Não foi possível alterar atributos do arquivo %s: %s", path, e)


def safe_save_csv(df, path, **to_csv_kwargs):
    """
    Tenta salvar DataFrame em CSV de forma robusta.
    - tenta salvar direto
    - se PermissionError: tenta chmod e regravar
    - se ainda falhar: salva em arquivo temporário no mesmo diretório e faz os.replace(tmp, path)
    Retorna o caminho final salvo (ou levanta exceção se falhar).
    """
    _ensure_parent_dir(path)
    try:
        df.to_csv(path, **to_csv_kwargs)
        logger.info("Salvo CSV: %s", path)
        return path
    except PermissionError as e:
        logger.warning("PermissionError ao salvar %s: %s. Tentando remover atributo readonly e regravar...", path, e)
        _remove_readonly_if_exists(path)
        try:
            df.to_csv(path, **to_csv_kwargs)
            logger.info("Salvo CSV depois de chmod: %s", path)
            return path
        except PermissionError:
            # fallback: escrever em tmp e tentar substituir
            try:
                dir_ = os.path.dirname(path) or "."
                fd, tmp = tempfile.mkstemp(prefix="tmp_save_", suffix=".csv", dir=dir_)
                os.close(fd)
                df.to_csv(tmp, **to_csv_kwargs)
                try:
                    os.replace(tmp, path)
                    logger.info("Salvo CSV via tmp -> replace: %s", path)
                    return path
                except Exception as e2:
                    logger.warning("Não foi possível substituir o arquivo final: %s. Mantendo tmp em %s. Erro: %s",
                                   path, tmp, e2)
                    return tmp
            except Exception as e3:
                logger.error("Falha ao salvar CSV em tmp: %s", e3)
                raise


def safe_save_figure(fig_or_savetarget, path, savefunc=None, **save_kwargs):
    """
    Save a Plotly/Matplotlib figure robustly.
    - Se savefunc for fornecida, chama savefunc(path, **save_kwargs).
    - Caso contrário, tenta usar .write_html (Plotly).
    Retorna o caminho final salvo (ou levanta exceção se falhar).
    """
    _ensure_parent_dir(path)
    try:
        if savefunc is not None:
            savefunc(path, **save_kwargs)
        else:
            if hasattr(fig_or_savetarget, "write_html"):
                fig_or_savetarget.write_html(path, include_plotlyjs="cdn")
            else:
                raise ValueError("Nenhuma função de salvamento válida informada para safe_save_figure.")
        logger.info("Figura salva: %s", path)
        return path
    except PermissionError as e:
        logger.warning("PermissionError ao salvar figura %s: %s. Tentando fallback...", path, e)
        _remove_readonly_if_exists(path)
        try:
            if savefunc is not None:
                savefunc(path, **save_kwargs)
            else:
                if hasattr(fig_or_savetarget, "write_html"):
                    fig_or_savetarget.write_html(path, include_plotlyjs="cdn")
            logger.info("Figura salva depois de chmod: %s", path)
            return path
        except PermissionError:
            # fallback tmp + replace
            try:
                dir_ = os.path.dirname(path) or "."
                fd, tmp = tempfile.mkstemp(prefix="tmp_save_fig_", suffix=os.path.splitext(path)[1] or ".html",
                                           dir=dir_)
                os.close(fd)
                if savefunc is not None:
                    savefunc(tmp, **save_kwargs)
                else:
                    fig_or_savetarget.write_html(tmp, include_plotlyjs="cdn")
                try:
                    os.replace(tmp, path)
                    logger.info("Figura salva via tmp -> replace: %s", path)
                    return path
                except Exception as e2:
                    logger.warning("Não foi possível substituir o arquivo final: %s. Mantendo tmp em %s. Erro: %s",
                                   path, tmp, e2)
                    return tmp
            except Exception as e3:
                logger.error("Falha ao salvar figura em tmp: %s", e3)
                raise


# --- Função para dashboards ---
def gerar_dashboards(df, outdir):
    dash_dir = os.path.join(outdir, "dashboards")
    ensure_dir(dash_dir)
    dash_path = os.path.join(dash_dir, "dashboard.html")

    figs = []
    # Gráficos de distribuição numérica
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    for col in num_cols:
        try:
            fig = px.histogram(df, x=col, nbins=30, title=f"Distribuição de {col}")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist para %s: %s", col, e)

        try:
            fig = px.box(df, y=col, title=f"Boxplot de {col}")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar box para %s: %s", col, e)

    for col in cat_cols:
        try:
            fig = px.histogram(df, x=col, title=f"Distribuição de {col} (categórica)")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist categórica para %s: %s", col, e)

    # Se houver 'falha'
    if "falha" in df.columns:
        try:
            fig = px.histogram(df, x="falha", title="Distribuição de Falhas", color="falha")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist de falha: %s", e)

        for col in num_cols[:5]:  # limita a 5 para não gerar centenas de gráficos
            try:
                fig = px.box(df, x="falha", y=col, color="falha", title=f"{col} x Falha")
                figs.append(fig)
            except Exception as e:
                logger.debug("Erro ao criar box falha x %s: %s", col, e)

    # Se houver 'criticidade'
    if "criticidade" in df.columns:
        try:
            fig = px.histogram(df, x="criticidade", title="Distribuição de Criticidade", color="criticidade")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist criticidade: %s", e)

    # Salvar em HTML único usando arquivo temporário e replace
    try:
        dir_ = os.path.dirname(dash_path) or "."
        fd, tmp = tempfile.mkstemp(prefix="tmp_dash_", suffix=".html", dir=dir_)
        os.close(fd)
        with open(tmp, "w", encoding="utf-8") as f:
            for fig in figs:
                f.write(pio.to_html(fig, include_plotlyjs="cdn", full_html=False, auto_play=False))
        try:
            os.replace(tmp, dash_path)
            logger.info("Dashboard gerado em: %s", dash_path)
        except Exception as e:
            logger.warning("Não foi possível mover dashboard tmp -> final: %s. Mantendo tmp em %s. Erro: %s", dash_path,
                           tmp, e)
    except Exception as e:
        logger.error("Falha ao gerar dashboard: %s", e)


# --- Função para dashboards de dados enriquecidos ---
def gerar_dashboards_enriquecidos(df, outdir):
    dash_dir = os.path.join(outdir, "dashboards")
    ensure_dir(dash_dir)
    dash_path = os.path.join(dash_dir, "dashboard_enriquecidos.html")

    figs = []

    # Série temporal por máquina
    if "ts" in df.columns and "id_maquina" in df.columns:
        for col in ["vibracao", "temperatura", "velocidade_motor"]:
            if col in df.columns:
                try:
                    fig = px.line(df, x="ts", y=col, color="id_maquina",
                                  title=f"Série temporal de {col} por máquina")
                    figs.append(fig)
                except Exception as e:
                    logger.debug("Erro ao criar série temporal %s: %s", col, e)

    # Distribuição das variáveis numéricas
    for col in ["vibracao", "temperatura", "velocidade_motor", "dias_ultima_manutencao"]:
        if col in df.columns:
            try:
                fig = px.histogram(df, x=col, nbins=30, title=f"Distribuição de {col}")
                figs.append(fig)
            except Exception as e:
                logger.debug("Erro ao criar hist enriquecido para %s: %s", col, e)

            try:
                fig = px.box(df, y=col, title=f"Boxplot de {col}")
                figs.append(fig)
            except Exception as e:
                logger.debug("Erro ao criar box enriquecido para %s: %s", col, e)

    # Falha
    if "falha" in df.columns:
        try:
            fig = px.histogram(df, x="falha", title="Distribuição de Falhas", color="falha")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist falha (enriq): %s", e)

        for col in ["vibracao", "temperatura", "velocidade_motor"]:
            if col in df.columns:
                try:
                    fig = px.box(df, x="falha", y=col, color="falha", title=f"{col} x Falha")
                    figs.append(fig)
                except Exception as e:
                    logger.debug("Erro ao criar box falha x %s (enriq): %s", col, e)

    # Qualidade do ar
    if "qualidade_de_ar" in df.columns:
        try:
            fig = px.histogram(df, x="qualidade_de_ar", title="Distribuição de Qualidade do Ar",
                               color="qualidade_de_ar")
            figs.append(fig)
        except Exception as e:
            logger.debug("Erro ao criar hist qualidade_de_ar: %s", e)

        if "temperatura" in df.columns:
            try:
                fig = px.box(df, x="qualidade_de_ar", y="temperatura", color="qualidade_de_ar",
                             title="Temperatura x Qualidade do Ar")
                figs.append(fig)
            except Exception as e:
                logger.debug("Erro ao criar box qualidade_de_ar x temperatura: %s", e)

    # Salvar HTML único (tmp -> replace)
    try:
        dir_ = os.path.dirname(dash_path) or "."
        fd, tmp = tempfile.mkstemp(prefix="tmp_dash_enriq_", suffix=".html", dir=dir_)
        os.close(fd)
        with open(tmp, "w", encoding="utf-8") as f:
            for fig in figs:
                f.write(pio.to_html(fig, include_plotlyjs="cdn", full_html=False, auto_play=False))
        try:
            os.replace(tmp, dash_path)
            logger.info("Dashboard de dados enriquecidos gerado em: %s", dash_path)
        except Exception as e:
            logger.warning("Não foi possível mover dashboard_enriq tmp -> final: %s. Mantendo tmp em %s. Erro: %s",
                           dash_path, tmp, e)
    except Exception as e:
        logger.error("Falha ao gerar dashboard_enriq: %s", e)


def gerar_readings_from_sensores(df_sensores, outdir, filename="readings.csv"):
    """
    Gera readings.csv com colunas exatas:
      ts, temperatura, vibracao, qualidade_de_ar
    a partir do DataFrame df_sensores (leitura_sensores.csv).
    Salva em outdir/filename usando safe_save_csv.
    """
    ensure_dir(outdir)
    n = len(df_sensores)

    # --- TS ---
    ts_candidates = [c for c in df_sensores.columns if c.lower() in ("ts", "timestamp", "data", "datetime", "date")]
    if ts_candidates:
        ts_col = ts_candidates[0]
        ts = pd.to_datetime(df_sensores[ts_col], errors="coerce")
        if ts.isna().any():
            start = pd.Timestamp.now().floor("T")
            fallback = pd.date_range(start=start, periods=n, freq="T")
            ts = ts.fillna(fallback[:n])
    else:
        start = pd.Timestamp.now().floor("T")
        ts = pd.date_range(start=start, periods=n, freq="T")

    # Garantir que seja Series para aplicar dt.strftime
    if isinstance(ts, pd.Series):
        ts_str = ts.dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        ts_str = pd.Series(ts).dt.strftime("%Y-%m-%d %H:%M:%S.%f")

    # --- TEMPERATURA ---
    if "temperatura" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temperatura"], errors="coerce")
    elif "temperature" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temperature"], errors="coerce")
    elif "temp" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temp"], errors="coerce")
    else:
        temperatura = pd.Series([np.nan] * n)

    # --- VIBRACAO ---
    if "vibracao" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vibracao"], errors="coerce")
    elif "vibration" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vibration"], errors="coerce")
    elif "vib" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vib"], errors="coerce")
    else:
        vibracao = pd.Series([np.nan] * n)

    # --- QUALIDADE_DE_AR ---
    if "qualidade_de_ar" in df_sensores.columns:
        q = df_sensores["qualidade_de_ar"]
        q_num = pd.to_numeric(q, errors="coerce")
        if q_num.notna().any():
            qualidade_de_ar = q_num
        else:
            qualidade_de_ar = q.astype(str).replace("nan", pd.NA)
    elif "aqi_pm25" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["aqi_pm25"], errors="coerce")
    elif "air_q" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["air_q"], errors="coerce")
    elif "aqi" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["aqi"], errors="coerce")
    else:
        qualidade_de_ar = pd.Series([pd.NA] * n)

    # montar DataFrame com a ordem e nomes exatos solicitados
    out_df = pd.DataFrame({
        "ts": ts_str,
        "temperatura": pd.to_numeric(temperatura, errors="coerce"),
        "vibracao": pd.to_numeric(vibracao, errors="coerce"),
        "qualidade_de_ar": qualidade_de_ar
    })

    outpath = os.path.join(outdir, filename)
    safe_save_csv(out_df, outpath, index=False, encoding="utf-8")
    logger.info("readings.csv gerado em: %s (linhas=%d)", outpath, len(out_df))
    return outpath

    # --- TEMPERATURA ---
    if "temperatura" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temperatura"], errors="coerce")
    elif "temperature" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temperature"], errors="coerce")
    elif "temp" in df_sensores.columns:
        temperatura = pd.to_numeric(df_sensores["temp"], errors="coerce")
    else:
        temperatura = pd.Series([np.nan] * n)

    # --- VIBRACAO ---
    if "vibracao" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vibracao"], errors="coerce")
    elif "vibration" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vibration"], errors="coerce")
    elif "vib" in df_sensores.columns:
        vibracao = pd.to_numeric(df_sensores["vib"], errors="coerce")
    else:
        vibracao = pd.Series([np.nan] * n)

    # --- QUALIDADE_DE_AR ---
    if "qualidade_de_ar" in df_sensores.columns:
        # tenta manter numérico se for numérico, senão string
        q = df_sensores["qualidade_de_ar"]
        q_num = pd.to_numeric(q, errors="coerce")
        if q_num.notna().any():
            qualidade_de_ar = q_num
        else:
            qualidade_de_ar = q.astype(str).replace("nan", pd.NA)
    elif "aqi_pm25" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["aqi_pm25"], errors="coerce")
    elif "air_q" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["air_q"], errors="coerce")
    elif "aqi" in df_sensores.columns:
        qualidade_de_ar = pd.to_numeric(df_sensores["aqi"], errors="coerce")
    else:
        qualidade_de_ar = pd.Series([pd.NA] * n)

    # montar DataFrame com a ordem e nomes exatos solicitados
    out_df = pd.DataFrame({
        "ts": ts_str,
        "temperatura": pd.to_numeric(temperatura, errors="coerce"),
        "vibracao": pd.to_numeric(vibracao, errors="coerce"),
        "qualidade_de_ar": qualidade_de_ar
    })

    outpath = os.path.join(outdir, filename)
    safe_save_csv(out_df, outpath, index=False, encoding="utf-8")
    logger.info("readings.csv gerado em: %s (linhas=%d)", outpath, len(out_df))
    return outpath


# --- Pipeline principal ---
def main():
    # ajuste seu base_path se necessário
    base_path = r"C:\Users\CarlosSouza\OneDrive\BACKUP\OneDrive\Documentos\3_PESSOAIS_DADOS_ARQUIVOS\FIAP\FASE_5\Trabalho_Rascunho"

    arquivos = {
        "sensores": os.path.join(base_path, "leitura_sensores.csv"),
        "maquinas": os.path.join(base_path, "maquina_autonoma.csv"),
        "manutencao": os.path.join(base_path, "manutencao.csv"),
        "funcionarios": os.path.join(base_path, "funcionario.csv"),
    }

    # saída
    outdir = os.path.join(base_path, "saida")
    figs_dir = os.path.join(outdir, "figs")
    rel_dir = os.path.join(outdir, "relatorios")
    ensure_dir(outdir);
    ensure_dir(figs_dir);
    ensure_dir(rel_dir)

    logger.info("Carregando dados...")
    # leitura com try/except mais verboso para diagnosticar erros de leitura/perm
    try:
        df_sensores = pd.read_csv(arquivos["sensores"])
        df_maquinas = pd.read_csv(arquivos["maquinas"])
        df_manutencao = pd.read_csv(arquivos["manutencao"])
        df_funcionarios = pd.read_csv(arquivos["funcionarios"])
    except Exception as e:
        logger.error("Erro ao carregar arquivos CSV: %s", e)
        raise

    # merges automáticos
    df = safe_merge(df_sensores, df_maquinas, on="id_maquina")
    df = safe_merge(df, df_manutencao, on="id_maquina")
    df = safe_merge(df, df_funcionarios, on="id_funcionario")

    # features numéricas e categóricas (detecta automaticamente)
    numeric_features = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["falha"]]
    categorical_features = [c for c in df.select_dtypes(include=["object"]).columns]

    logger.info("Features numéricas detectadas: %s", numeric_features)
    logger.info("Features categóricas detectadas: %s", categorical_features)

    # salvar dataset enriquecido (usando função robusta)
    enriched_path = os.path.join(rel_dir, "dados_enriquecidos.csv")
    safe_save_csv(df, enriched_path, index=False, encoding="utf-8")

    # treinamento supervisionado (se coluna falha existir)
    if "falha" in df.columns and df["falha"].nunique() > 1:
        X = df[numeric_features + categorical_features]
        y = df["falha"].astype(int)

        pre = ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), numeric_features),
            ("cat", Pipeline(
                [("imp", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]),
             categorical_features)
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
        clf = Pipeline(
            [("pre", pre), ("rf", RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"))])
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        metrics_path = os.path.join(rel_dir, "metricas_classificacao.csv")
        safe_save_csv(pd.DataFrame(report).transpose(), metrics_path)

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 4))
        plt.imshow(cm, cmap="Blues")
        plt.title("Matriz de Confusão")
        for (i, j), val in np.ndenumerate(cm):
            plt.text(j, i, val, ha="center", va="center")
        plt.tight_layout()

        # salvar figura de forma robusta
        conf_path = os.path.join(figs_dir, "confusion_matrix.png")
        savefunc = lambda p, **kw: plt.savefig(p, **kw)
        safe_save_figure(None, conf_path, savefunc=savefunc, bbox_inches="tight")
        plt.close()

    # IsolationForest (anomalias)
    if numeric_features:
        try:
            iso = IsolationForest(n_estimators=200, random_state=42, contamination=0.02)
            scores = -iso.fit(df[numeric_features].fillna(0)).score_samples(df[numeric_features].fillna(0))
            df["anomalia_score"] = scores
            df["anomalia_rank_pct"] = pd.Series(scores).rank(pct=True)
            df["criticidade"] = pd.cut(df["anomalia_rank_pct"], bins=[0, 0.75, 0.9, 0.98, 1.0],
                                       labels=["Baixo", "Médio", "Alto", "Crítico"])
        except Exception as e:
            logger.error("Erro ao rodar IsolationForest: %s", e)
    else:
        logger.warning("Nenhuma feature numérica encontrada para anomalias.")

    result_path = os.path.join(rel_dir, "dados_resultados.csv")
    safe_save_csv(df, result_path, index=False, encoding="utf-8")
    logger.info("Pipeline concluído. Resultados em: %s", outdir)

    # gerar readings.csv com as colunas ts, temperatura, vibracao, qualidade_de_ar
    try:
        gerar_readings_from_sensores(df_sensores, outdir, filename="readings.csv")
    except Exception as e:
        logger.error("Falha ao gerar readings.csv: %s", e)

    # --- Geração de Dashboards ---
    gerar_dashboards(df, outdir)
    gerar_dashboards_enriquecidos(df, outdir)


if __name__ == "__main__":
    main()
