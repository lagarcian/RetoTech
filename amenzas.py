import re
import logging
import json
import sys
from typing import Dict, List, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Anonymizer:
    """
    Módulo de Privacidad (Privacy by Design).
    Se encarga de ofuscar PII (Personal Identifiable Information) en los tickets.
    """
    def _init_(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?(\d{1,3}))?[-. (]?(\d{3})[-. )]?(\d{3})[-. ]*(\d{4})\b',
            'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 
            'password': r'(password|contraseña|clave)\s*[:=]\s*([^\s]+)', 
        }

    def sanitize_text(self, text: str) -> str:
        """Reemplaza datos sensibles con tokens genéricos en una cadena de texto."""
        sanitized = text
        
        sanitized = re.sub(self.patterns['email'], '[EMAIL_REDACTED]', sanitized)
        
        sanitized = re.sub(self.patterns['ip'], '[IP_REDACTED]', sanitized)
        
        sanitized = re.sub(r'\b(?:\+?(\d{1,3}))?[-. (]?(\d{3})[-. )]?(\d{3})[-. ]*(\d{4})\b', '[PHONE_REDACTED]', sanitized)

        sanitized = re.sub(self.patterns['password'], r'\1=[PASSWORD_SCRUBBED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized

    def sanitize_json(self, data: Dict) -> Dict:
        """Limpia todos los valores de tipo string en un diccionario."""
        cleaned_data = data.copy()
        for key, value in cleaned_data.items():
            if isinstance(value, str):
                cleaned_data[key] = self.sanitize_text(value)
            elif isinstance(value, dict):
                cleaned_data[key] = self.sanitize_json(value)
        return cleaned_data

class ThreatDetector:
    """
    Módulo de seguridad: Primera línea de defensa (Anti-Phishing).
    """
    def _init_(self):
        self.phishing_keywords = [
            r"urgente", r"inmediato", r"suspensión", r"bloqueo de cuenta",
            r"verificar su identidad", r"actualice su cuenta", r"pago pendiente",
            r"contraseña expirada", r"clic aquí", r"transferencia", r"hackeado",
            r"alerta de seguridad"
        ]
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self.ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'


    def _is_private_ip(self, ip: str) -> bool:
        """Determina si una IP es local/privada (común en tickets
