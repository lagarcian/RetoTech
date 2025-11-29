import re
import logging
import json
from typing import Dict, List, Union

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Anonymizer:
    """
    Módulo de Privacidad (Privacy by Design).
    Se encarga de ofuscar PII (Personal Identifiable Information) en los tickets.
    """
    def __init__(self):
        # Regex para datos sensibles
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b',
            # IP: Detecta IPs pero ignoraremos las privadas en el threat check, aquí las ocultamos todas
            'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 
            'password': r'(password|contraseña|clave)\s*=\s*([^\s]+)',
            'credit_card': r'\b(?:\d[ -]*?){13,16}\b'
        }

    def sanitize_text(self, text: str) -> str:
        """Reemplaza datos sensibles con tokens genéricos en una cadena de texto."""
        sanitized = text
        
        # 1. Enmascarar Emails
        sanitized = re.sub(self.patterns['email'], '[EMAIL_REDACTED]', sanitized)
        
        # 2. Enmascarar IPs
        sanitized = re.sub(self.patterns['ip'], '[IP_REDACTED]', sanitized)
        
        # 3. Enmascarar Teléfonos
        sanitized = re.sub(self.patterns['phone'], '[PHONE_REDACTED]', sanitized)
        
        # 4. Enmascarar Contraseñas (Captura el valor después del signo =)
        sanitized = re.sub(self.patterns['password'], r'\1=[PASSWORD_SCRUBBED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized

    def sanitize_json(self, data: Dict) -> Dict:
        """
        Recorre un diccionario completo y limpia todos los valores de tipo string.
        Asegura que campos estructurados (como 'email' o 'telefono') también sean sanitizados.
        """
        cleaned_data = data.copy()
        for key, value in cleaned_data.items():
            if isinstance(value, str):
                # Aplicamos la limpieza a cada campo de texto en el JSON
                cleaned_data[key] = self.sanitize_text(value)
            elif isinstance(value, dict):
                # Recursividad básica para diccionarios anidados
                cleaned_data[key] = self.sanitize_json(value)
            # Nota: Podríamos agregar manejo de listas si fuera necesario
        return cleaned_data

class ThreatDetector:
    """
    Módulo de seguridad: Primera línea de defensa (Anti-Phishing).
    """
    def __init__(self):
        self.phishing_keywords = [
            r"urgente", r"inmediato", r"suspensión", r"bloqueo de cuenta",
            r"verificar su identidad", r"ganador", r"verify your account", 
            r"urgent action", r"bank transfer",
            # Nuevas palabras clave agregadas
            r"actualice su cuenta", r"cobro no reconocido", r"pago pendiente",
            r"contraseña expirada", r"clic aquí", r"descargar adjunto",
            r"atención inmediata", r"confirmar datos", r"seguridad de cuenta",
            r"alerta de seguridad", r"verificación urgente"
        ]
        self.ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


    def _is_private_ip(self, ip: str) -> bool:
        """Determina si una IP es local/privada (común en tickets de soporte)."""
        return ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("127.")

    def ingest_json_payload(self, json_payload: str) -> List[Dict]:
        """Procesa JSON, normalizando campos diferentes (ej: texto_ticket -> body)."""
        try:
            data = json.loads(json_payload)
            # Normalizar a lista si es un solo objeto
            tickets = [data] if isinstance(data, dict) else data
            
            logging.info(f"Procesando lote de {len(tickets)} tickets...")
            results = []
            
            for t in tickets:
                # Mapeo de campos flexibles
                t_id = t.get("id") or t.get("usuario", "UNKNOWN_ID")
                t_body = t.get("body") or t.get("texto_ticket", "")
                
                scan_result = self.scan_ticket(t_id, t_body)
                results.append(scan_result)
            return results
            
        except json.JSONDecodeError as e:
            logging.error(f"Error JSON: {e}")
            return []

    def scan_ticket(self, ticket_id: str, text_content: str) -> Dict:
        threat_score = 0
        detected_triggers = []
        text_lower = text_content.lower()

        # 1. Keywords
        for pattern in self.phishing_keywords:
            if re.search(pattern, text_lower):
                threat_score += 20
                detected_triggers.append(f"Keyword: {pattern}")

        # 2. URLs y IPs
        urls = re.findall(self.url_pattern, text_content)
        ips = re.findall(self.ip_pattern, text_content)
        
        # Lógica mejorada: Solo penalizar IPs públicas (no locales)
        public_ips = [ip for ip in ips if not self._is_private_ip(ip)]
        if public_ips:
            threat_score += 50
            detected_triggers.append(f"Public IP: {public_ips}")
            
        if len(urls) > 3:
            threat_score += 30
            detected_triggers.append("Excessive Links")

        is_threat = threat_score >= 40
        return {
            "ticket_id": ticket_id,
            "original_text": text_content, # Guardamos temporalmente para pasar al anonimizador
            "status": "THREAT_DETECTED" if is_threat else "SAFE",
            "risk_score": threat_score,
            "triggers": detected_triggers,
            "next_action": "ISOLATE" if is_threat else "ANONYMIZE"
        }

# --- PIPELINE PRINCIPAL (SIMULACIÓN) ---
if __name__ == "__main__":
    # Inicializar módulos
    detector = ThreatDetector()
    anonymizer = Anonymizer()

    # Input del usuario
    json_ticket = """
    {
        "nombre": "Luis García",
        "email": "luis.garcia@example.com",
        "usuario": "lgarcia89",
        "contraseña": "MiClaveUltraSecreta123",
        "IP": "192.168.1.25",
        "telefono": "3214567890",
        "prioridad": "Alta",
        "texto_ticket": "Tengo problemas con la VPN. Mi IP es 192.168.1.25, mi teléfono es 3214567890 y envié un correo desde luis.garcia@example.com. password=MiClaveUltraSecreta123"
    }
    """

    print("--- INICIANDO PIPELINE VORTEX: SEGURIDAD + PRIVACIDAD ---\n")
    
    # 1. Fase de Ingesta y Detección
    analisis_seguridad = detector.ingest_json_payload(json_ticket)
    
    # Simulamos acceso a los datos crudos originales para poder limpiar el objeto completo
    # En producción, esto se manejaría pasando el objeto completo por el pipeline
    datos_crudos = json.loads(json_ticket)
    if isinstance(datos_crudos, dict): 
        datos_crudos = [datos_crudos] # Normalizar a lista para facilitar búsqueda por ID
    
    for resultado in analisis_seguridad:
        print(f"Ticket ID: {resultado['ticket_id']}")
        print(f"Estado de Amenaza: {resultado['status']} (Score: {resultado['risk_score']})")
        
        if resultado['next_action'] == "ISOLATE":
            print("ACCION: Bloqueado por seguridad.")
        
        elif resultado['next_action'] == "ANONYMIZE":
            print("ACCION: Aprobado. Iniciando limpieza profunda de PII...")
            
            # PASO CRÍTICO: Recuperar el objeto original completo para limpiar metadatos
            # Buscamos el ticket original usando el ID o Usuario
            ticket_original = next(
                (t for t in datos_crudos if t.get('id') == resultado['ticket_id'] or t.get('usuario') == resultado['ticket_id']), 
                None
            )
            
            if ticket_original:
                # Limpiamos TODO el objeto, no solo el texto
                ticket_limpio = anonymizer.sanitize_json(ticket_original)
                
                print(f"\n[JSON ORIGINAL]:\n{json.dumps(ticket_original, indent=2, ensure_ascii=False)}")
                print(f"\n[JSON SEGURO] (Listo para IA):\n{json.dumps(ticket_limpio, indent=2, ensure_ascii=False)}")
            else:
                print("Error: No se pudo recuperar el ticket original para limpieza completa.")

            print("\n>> Ticket listo para Fase de IA (Churn Analysis) <<")

