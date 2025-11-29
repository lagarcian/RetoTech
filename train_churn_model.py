import joblib
import numpy as np
import pandas as pd
import mysql.connector
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

DB_CONFIG = {
    'host': 'localhost', 'user': 'wp_tickets_user', 
    'password': 'Temp300%', 'database': 'creativecodelabs_tickets'
}

def main():
    print("\n--- 3. ENTRENANDO ANALISTA DE RIESGOS (CHURN) ---")

    try:
        # 1. Cargar Vectores
        X = joblib.load('X_vectors.pkl')
        sentiment_scores = X[:, -1] # La última columna es el sentimiento
        
        # 2. Sincronizar con DB para obtener Tiempos
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT id, status, created_at FROM tickets ORDER BY id ASC", conn)
        conn.close()

        # Recorte de seguridad por si hay nuevos tickets desde que se corrió vectorizer
        if len(df) > X.shape[0]:
            df = df.head(X.shape[0])

        # 3. Ingeniería de Datos (Simulación de TTR para entrenamiento)
        # Convertir fechas
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Generar horas aleatorias de resolución (Simulación)
        np.random.seed(42)
        random_hours = np.random.randint(1, 100, size=len(df))
        df['ttr_hours'] = random_hours 
        
        # 4. Crear el Target (Y): Índice de Riesgo
        # Lógica: Más tiempo + Sentimiento Negativo = Mayor Riesgo
        
        # Normalizar TTR (0 a 1)
        ttr_norm = df['ttr_hours'] / df['ttr_hours'].max()
        # Normalizar Sentimiento (de -1/1 a 0/1) -> (s + 1) / 2. Luego invertimos (1 - s) porque negativo es malo.
        # Sentimiento: -1 (Odio) -> Norm: 0 -> Invertido: 1 (Alto Riesgo)
        sent_risk = 1 - ((sentiment_scores + 1) / 2)
        
        # Fórmula combinada
        raw_risk = (ttr_norm * 0.5) + (sent_risk * 0.5)
        
        # Escalar a 0-100
        scaler = MinMaxScaler(feature_range=(0, 100))
        Y_churn = scaler.fit_transform(raw_risk.reshape(-1, 1))

        # 5. Red Neuronal de Regresión (3 Capas)
        model = Sequential()
        model.add(Dense(64, input_dim=X.shape[1], activation='relu')) # Capa 1
        model.add(Dense(32, activation='relu'))                       # Capa 2
        model.add(Dense(1, activation='linear'))                      # Capa 3 (Salida continua)

        model.compile(loss='mse', optimizer='adam', metrics=['mae'])

        # 6. Entrenar
        X_train, X_test, y_train, y_test = train_test_split(X, Y_churn, test_size=0.2, random_state=42)
        print("⏳ Entrenando predicción de riesgos...")
        model.fit(X_train, y_train, epochs=30, batch_size=4, verbose=1)

        # 7. Guardar
        model.save('churn_risk_model.h5')
        joblib.dump(scaler, 'churn_scaler.pkl') # Guardar escalador para usarlo al predecir
        print("✅ Modelo guardado: churn_risk_model.h5 y churn_scaler.pkl")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()