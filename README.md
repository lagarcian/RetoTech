# RetoTech
Reto para Hackaton Lote 2 A Team

Somos 
Camilo Figuera Desarrollador y Psicólogo,
Julian Niño Estudiante de Administración Ambiental,
Luis García Matemático. 

RETOTECH: SOLUCION DE PROCESAMIENTO INTELIGENTE Y SEGURO DE TICKETS
===================================================================

DESCRIPCION GENERAL
-------------------
Retotech es una arquitectura de solución diseñada para la gestión, aseguramiento 
[cite_start]y clasificación automática de tickets de soporte[cite: 1]. El sistema implementa un flujo 
de trabajo híbrido (PHP/Python) que intercepta los datos antes de su almacenamiento, 
garantizando seguridad y privacidad previas al análisis predictivo con Inteligencia 
[cite_start]Artificial[cite: 2, 3].


ARQUITECTURA DE LA SOLUCION
---------------------------

ETAPA 1: PRE-PROCESAMIENTO Y SEGURIDAD (IMPLEMENTADO)
Antes de que la IA analice cualquier ticket, los datos atraviesan una capa 
[cite_start]rigurosa de limpieza y protección[cite: 3]:

1. Detección de Amenazas (Phishing):
   - Módulo: ThreatDetector (en process_ticket.py).
   - Función: Escanea palabras clave de riesgo (ej: "urgente", "bloqueo").
   - [cite_start]Lógica: Si el puntaje de riesgo es >= 40, el ticket es bloqueado[cite: 3].

2. Aislamiento de Ataques:
   - Mecanismo: El plugin 'custom-ticket-handler.php' detiene tickets peligrosos.
   - Auditoría: Los tickets bloqueados NO ingresan a la base de datos principal; 
     [cite_start]se desvían a la tabla 'blocked_tickets'[cite: 3].

3. Anonimización (Privacy by Design):
   - Módulo: Anonymizer (en process_ticket.py).
   - Acción: Utiliza expresiones regulares para reemplazar PII (correos, IPs) 
     [cite_start]con tokens seguros (ej: [EMAIL_REDACTED]) antes de guardar en BD[cite: 3].

4. Almacenamiento Seguro:
   - [cite_start]Tabla 'tickets': Recibe únicamente datos limpios[cite: 3].
   - [cite_start]Tabla 'blocked_tickets': Recibe datos crudos de amenazas[cite: 3].


ETAPA 2: INTELIGENCIA ARTIFICIAL Y NLP 
[cite_start]Los datos asegurados alimentan el pipeline de Machine Learning[cite: 4]:

1. Vectorización (Completo):
   - Script: vectorizer.py.
   - [cite_start]Estado: Matriz de entrada X generada y archivos .pkl listos[cite: 4].

2. Análisis de Sentimientos :
   - Objetivo: Generar una métrica de frustración normalizada (entre -1.0 y 1.0) 
     [cite_start]utilizando la librería NLTK[cite: 4].

3. Clasificación Neuronal:
   - Script: train_model.py.
   - [cite_start]Objetivo: Entrenar el modelo final 'ticket_classifier_model.h5'[cite: 4].

ETAPA 3: MODULO DE ANALITICA AVANZADA
----------------------------
Archivo: insights_estadisticos.py

Como complemento a la gestión operativa, la solución incluye un motor de análisis 
híbrido para la toma de decisiones.

- Propósito: Identificar factores que impulsan el riesgo de churn (abandono).
- Metodología: Combina estadística descriptiva (correlación de Pearson) con 
  Procesamiento de Lenguaje Natural (NLP).
- Funcionalidad: Analiza métricas de servicio y texto libre para generar insights 
  automáticos sobre la satisfacción del cliente.


TECNOLOGIAS CLAVE
-----------------
- Backend: PHP (Intercepción), Python (Procesamiento y ML).
- NLP & IA: NLTK (VADER Sentiment Analysis), Scikit-Learn, TensorFlow/Keras.
- Seguridad: Regex para saneamiento, Lógica de umbral de riesgo.
