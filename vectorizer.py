import mysql.connector
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import joblib 
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Descargar léxico VADER si no existe
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# --- CONFIGURACIÓN DB ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'wp_tickets_user',
    'password': 'Temp300%', 
    'database': 'creativecodelabs_tickets'
}

def get_sentiment_score(text):
    """Calcula el puntaje de sentimiento (-1 a 1)."""
    if not isinstance(text, str):
        return 0.0
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)['compound']

def main():
    print("--- 1. INICIANDO VECTORIZACIÓN ---")
    
    # 1. Extraer datos
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = "SELECT id, description, status FROM tickets WHERE status IN ('Open', 'Closed') ORDER BY id ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        print(f"✅ Datos cargados: {len(df)} tickets.")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return

    # 2. Calcular Sentimiento
    print("⏳ Calculando sentimientos...")
    df['sentiment_score'] = df['description'].apply(get_sentiment_score)

    # 3. Vectorizar Texto (TF-IDF)
    print("⏳ Vectorizando texto...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_tfidf = vectorizer.fit_transform(df['description']).toarray()

    # 4. Fusionar (Texto + Sentimiento)
    # X es la matriz final: 5000 columnas de palabras + 1 columna de sentimiento
    X = np.hstack([X_tfidf, df['sentiment_score'].values.reshape(-1, 1)])

    # 5. Preparar Etiquetas (Solo para el Clasificador)
    le = LabelEncoder()
    y = le.fit_transform(df['status']) # 0=Closed, 1=Open

    # 6. Guardar todo
    joblib.dump(X, 'X_vectors.pkl')
    joblib.dump(y, 'y_labels.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    joblib.dump(le, 'label_encoder.pkl') # Guardamos esto para saber qué es 0 y 1

    print(f"✅ ÉXITO. Matriz X generada con forma: {X.shape}")
    print("   Archivos guardados: X_vectors.pkl, y_labels.pkl, tfidf_vectorizer.pkl")

if __name__ == "__main__":
    main()