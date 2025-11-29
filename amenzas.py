import re
import logging
import json  # Nueva librería para manejo de datos estándar
from typing import Dict, Tuple, List, Union

# Configuración de Logging para auditoría (Crítico en Ciberseguridad)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatDetector:
    """
    Módulo de seguridad encargado de la primera línea de defensa.
    Analiza tickets en busca de patrones de Phishing e Ingeniería Social.
    """

    def __init__(self):
        # Base de conocimiento: Palabras clave de alta sospecha en español e inglés
        self.phishing_keywords = [
            r"urgente", r"inmediato", r"suspensión", r"bloqueo de cuenta",
            r"verificar su identidad", r"haga clic aquí", r"ganador", 
            r"verify your account", r"urgent action", r"bank transfer",
            r"contraseña", r"password", r"actualizar datos bancarios"
        ]
        
        # Patrones Regex para detectar URLs sospechosas o direcciones IP
        # Detecta IPs directas (común en ataques) en lugar de dominios
        self.ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        
        # Detecta URLs (simplificado para el ejemplo)
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def ingest_json_payload(self, json_payload: str) -> List[Dict]:
        """
        Procesa un lote de tickets recibidos en formato JSON crudo.
        Simula la recepción de datos desde una API o cola de mensajes.
        
        Args:
            json_payload (str): String con formato JSON conteniendo una lista de tickets.
            
        Returns:
            List[Dict]: Lista de resultados del análisis de seguridad.
        """
        try:
            tickets = json.loads(json_payload)
            logging.info(f"Payload JSON recibido. Procesando {len(tickets)} tickets...")
            
            results = []
            for ticket in tickets:
                # Validación básica de estructura
                if "id" not in ticket or "body" not in ticket:
                    logging.error(f"Estructura de ticket inválida: {ticket}")
                    continue
                    
                scan_result = self.scan_ticket(ticket["id"], ticket["body"])
                results.append(scan_result)
                
            return results
            
        except json.JSONDecodeError as e:
            logging.error(f"Error crítico al decodificar JSON: {e}")
            return []

    def scan_ticket(self, ticket_id: str, text_content: str) -> Dict:
        """
        Ejecuta el análisis de amenazas sobre el contenido de un ticket.
        
        Args:
            ticket_id (str): Identificador único del ticket.
            text_content (str): El cuerpo del mensaje del ticket.
            
        Returns:
            Dict: Resultado del análisis con estado (SAFE/THREAT), score y metadatos.
        """
        logging.info(f"Iniciando escaneo de seguridad para Ticket ID: {ticket_id}")
        
        threat_score = 0
        detected_triggers = []

        # 1. Análisis de Palabras Clave (Heurística)
        text_lower = text_content.lower()
        for pattern in self.phishing_keywords:
            if re.search(pattern, text_lower):
                threat_score += 20
                detected_triggers.append(f"Keyword: {pattern}")

        # 2. Análisis de Enlaces e IPs
        urls = re.findall(self.url_pattern, text_content)
        ips = re.findall(self.ip_pattern, text_content)
        
        if ips:
            threat_score += 50 # Las IPs directas son muy sospechosas en correos de clientes
            detected_triggers.append(f"Suspicious IP found: {ips}")
            
        if len(urls) > 3: # Exceso de links puede indicar spam/phishing
            threat_score += 30
            detected_triggers.append("Excessive Links")

        # 3. Evaluación de Riesgo (Umbral)
        # Si el score supera 40, se considera amenaza y se aísla.
        is_threat = threat_score >= 40
        status = "THREAT_DETECTED" if is_threat else "SAFE"
        action = "ISOLATE_TICKET" if is_threat else "PROCEED_TO_ANONYMIZATION"

        result = {
            "ticket_id": ticket_id,
            "status": status,
            "risk_score": threat_score,
            "triggers": detected_triggers,
            "next_action": action
        }

        self._log_result(result)
        return result

    def _log_result(self, result: Dict):
        """Registra el resultado. Si es amenaza, usa nivel WARNING/CRITICAL."""
        if result["status"] == "THREAT_DETECTED":
            logging.warning(f"AMENAZA DETECTADA: {result}")
        else:
            logging.info(f"Ticket limpio: {result['ticket_id']}")

# --- SIMULACIÓN DE EJECUCIÓN (MAIN) ---
if __name__ == "__main__":
    detector = ThreatDetector()

    # SIMULACIÓN: Payload JSON tal como llegaría de una API externa o Frontend
    json_input_data = """
    [
        {
            "id": "TKT-001",
            "body": "Hola, tengo un problema con mi factura del mes pasado. ¿Podrían revisarlo? Gracias."
        },
        {
            "id": "TKT-002",
            "body": "URGENTE: Su cuenta ha sido bloqueada. Para recuperar el acceso haga clic en http://192.168.1.55/login y verifique su contraseña inmediatamente."
        },
        {
            "id": "TKT-003",
            "body": "Buenos días, adjunto los logs del error en el servidor de desarrollo."
        },
        {
            "id": "TKT-004",
            "body": "Estimado usuario, actualice sus datos bancarios aquí para evitar la suspensión."
        }
    ]
    """

    print("--- INICIANDO PROTOCOLO VORTEX DE SEGURIDAD (JSON INPUT) ---\n")
    
    # Procesamos el JSON directamente usando el nuevo método de ingesta
    analysis_results = detector.ingest_json_payload(json_input_data)
    
    processed_tickets_count = 0
    
    print("\n--- RESULTADOS DEL ANÁLISIS ---")
    for resultado in analysis_results:
        # Lógica de Compuerta (Gatekeeper)
        if resultado["next_action"] == "ISOLATE_TICKET":
            print(f"ALERTA [BLOQUEADO]: Ticket {resultado['ticket_id']} (Score: {resultado['risk_score']}) -> {resultado['triggers']}")
        else:
            print(f"EXITO  [APROBADO]: Ticket {resultado['ticket_id']} pasa a Anonimización.")
            processed_tickets_count += 1

    print("\n--- REPORTE FINAL ---")
    print(f"Tickets procesados para siguiente fase: {processed_tickets_count} de {len(analysis_results)}")