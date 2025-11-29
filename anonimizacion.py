import pandas as pd
import re
import json



def mask_name(name):
    if pd.isna(name): 
        return name
    return name[0] + "***"

def mask_email(email):
    if pd.isna(email):
        return email
    try:
        usuario, dominio = email.split("@")
        return usuario[0] + "***@" + dominio
    except:
        return "***"

def mask_phone(phone):
    if pd.isna(phone):
        return phone
    return "***" + phone[-2:]

def clean_text(text):
    if pd.isna(text): 
        return text
    
    
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
  
    text = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "[IP]", text)
  
    text = re.sub(r"\b\d{7,10}\b", "[PHONE]", text)
    
    return text




def ticket_from_json(json_input):
    """
    Recibe un JSON (string o dict) y lo convierte a DataFrame.
    Añade la hora automáticamente.
    """
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input

   
    data["hora"] = str(pd.Timestamp.now())

    
    expected_fields = ["nombre", "email", "telefono", "prioridad", "texto_ticket", "hora"]
    for field in expected_fields:
        data.setdefault(field, None)

    return pd.DataFrame([data])




def anonimizar_ticket(df):
    df = df.copy()

    df["nombre"] = df["nombre"].apply(mask_name)
    df["email"] = df["email"].apply(mask_email)
    df["telefono"] = df["telefono"].apply(mask_phone)
    df["texto_ticket"] = df["texto_ticket"].apply(clean_text)

    return df




json_ticket = """
{
    "nombre": "Luis García",
    "email": "luis.garcia@example.com",
    "telefono": "3214567890",
    "prioridad": "Alta",
    "texto_ticket": "Tengo problemas con la VPN. Mi IP es 192.168.1.25, mi teléfono es 3214567890 y envié un correo desde luis.garcia@example.com."
}
"""



df_original = ticket_from_json(json_ticket)
df_masked = anonimizar_ticket(df_original)

print("=== TICKET ORIGINAL ===")
print(df_original)

print("\n=== TICKET ANONIMIZADO PARA IA ===")
print(df_masked)
