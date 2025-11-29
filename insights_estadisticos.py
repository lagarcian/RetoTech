import nltk
nltk.download('vader_lexicon')
import pandas as pd
import numpy as np
#importar una libreria de analisis de sentimientos
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
#Importar Huggingface
import torch
from transformers import pipeline

# ---------------------------------------------------
# Función para generar insights estadísticos
# ---------------------------------------------------
def generar_insights(df, target_col="churn_risk", text_col=None):
    """
    df: DataFrame con métricas de servicio y churn
    target_col: columna que representa el riesgo de churn
    text_col: (Opcional) Nombre de la columna que contiene texto para análisis de sentimientos.
    """
    # Validación básica
    if target_col not in df.columns:
        raise ValueError(f"La columna {target_col} no existe en el DataFrame.")

    df_processed = df.copy() # Trabajar en una copia para no modificar el DataFrame original

    # Análisis de sentimientos si se proporciona una columna de texto
    if text_col and text_col in df_processed.columns:
        print(f"Realizando análisis de sentimientos en la columna '{text_col}'...")
        analyzer = SentimentIntensityAnalyzer()
        df_processed['vader_sentiment_compound'] = df_processed[text_col].apply(lambda text: analyzer.polarity_scores(str(text))['compound'])

    # Solo columnas numéricas para correlación
    numeric_cols = df_processed.select_dtypes(include=np.number).columns.tolist()

    # Calcular correlación de Pearson
    corr_matrix = df_processed[numeric_cols].corr(method="pearson")

    # Correlaciones con churn
    churn_corr = corr_matrix[target_col].sort_values(key=abs, ascending=False)

    # Identificar los principales impulsores del churn
    top_factors = churn_corr.drop(target_col).head(3)

    # Generar insights resumidos
    insights = []
    for factor, corr_value in top_factors.items():
        direction = "aumenta" if corr_value > 0 else "disminuye"
        insights.append(f"El factor '{factor}' {direction} el riesgo de churn (correlación {corr_value:.2f})")

    return {
        "Matriz de correlación": corr_matrix,
        "Correlación Churn": churn_corr,
        "Factores Top": top_factors,
        "insights": insights
    }

# ---------------------------------------------------
# Ejemplo de uso: métricas de servicio
# ---------------------------------------------------
data = {
    "avg_ticket_time": [5, 7, 3, 9, 4],           # tiempo promedio tickets correctivos
    "open_tickets": [2, 5, 1, 6, 2],             # tickets abiertos
    "customer_comments": [ # Nueva columna de texto
        "El servicio es excelente.", 
        "Pésima atención, muy lento.", 
        "Todo bien.", 
        "Fatal, quiero cancelar.", 
        "Podría mejorar."
    ],
    "project_age_months": [12, 3, 24, 1, 18],    # antigüedad del proyecto
    "churn_risk": [0.05, 0.9, 0.1, 0.95, 0.2]    # riesgo de churn
}

df_metrics = pd.DataFrame(data)

# Generar insights, usando la columna de texto para el sentimiento
resultados = generar_insights(df_metrics, target_col="churn_risk", text_col="customer_comments")

# Mostrar resultados
print("=== Correlación con churn ===")
print(resultados["Correlación Churn"], "\n")

print("=== Principales factores del churn ===")
print(resultados["Factores Top"], "\n")

print("=== Insights resumidos para el fundador ===")
for insight in resultados["insights"]:
    print("-", insight)
