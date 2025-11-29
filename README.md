# RetoTech
Reto para Hackaton Lote 2 A Team

Somos 
Camilo Figuera Desarrollador y Psicólogo,
Julian Niño Estudiante de Administración Ambiental,
Luis García Matemático. 

Vortex – Detección de Phishing y Anonimización de Tickets

Descripción
Vortex es un pipeline de seguridad que procesa tickets de soporte, detecta posibles amenazas de phishing y anonimiza información sensible (emails, teléfonos, IPs, contraseñas) para análisis seguro por sistemas de IA.

Funcionalidades

Anonimización de PII: emails, teléfonos, IPs, contraseñas, tarjetas de crédito.

Detección de phishing: palabras clave, URLs y IPs públicas.

Pipeline automático: decide si un ticket es seguro (ANONYMIZE) o sospechoso (ISOLATE).

Requisitos

Python ≥ 3.8

Librerías: pandas, numpy


Ticket Anonymizer

Descripción
Este proyecto proporciona un pipeline en Python para anonimizar tickets de soporte antes de enviarlos a sistemas de IA o almacenamiento. Protege la información sensible del usuario (PII) incluyendo nombres, correos electrónicos, teléfonos e IPs dentro del texto y en campos individuales.

Características principales

Lectura de tickets en formato JSON.

Captura automática de la hora del ticket.

Mascaramiento de campos: nombre, email, teléfono.

Limpieza de PII dentro del texto del ticket (IP, email, teléfono).

Compatible con pipelines de IA y almacenamiento seguro.

Tecnologías utilizadas

Python 3.x

pandas

numpy

re (expresiones regulares)
