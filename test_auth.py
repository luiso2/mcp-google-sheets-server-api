import os
import sys
sys.path.insert(0, r'C:\MCPS\mcp-google-sheets\src')

# Configurar variables de entorno
os.environ['SERVICE_ACCOUNT_PATH'] = r'C:\MCPS\mcp-google-sheets\credentials\service-account.json'
os.environ['DRIVE_FOLDER_ID'] = '1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ'

# Probar la autenticacion
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    # Cargar credenciales
    creds = service_account.Credentials.from_service_account_file(
        os.environ['SERVICE_ACCOUNT_PATH'],
        scopes=SCOPES
    )
    
    # Construir el servicio
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    print("[OK] Autenticacion exitosa!")
    print(f"Service Account: {creds.service_account_email}")
    print(f"Drive Folder ID: {os.environ['DRIVE_FOLDER_ID']}")
    
    # Intentar listar archivos en la carpeta
    try:
        results = drive_service.files().list(
            q=f"'{os.environ['DRIVE_FOLDER_ID']}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        print(f"\nHojas de calculo encontradas en la carpeta: {len(files)}")
        for file in files:
            print(f"  - {file['name']} (ID: {file['id']})")
            
        if not files:
            print("  (No hay hojas de calculo en la carpeta todavia)")
            
    except Exception as e:
        print(f"\n[ADVERTENCIA] Error al listar archivos: {e}")
        print("Asegurate de que la carpeta este compartida con el Service Account")
        
    print("\n[OK] El servidor MCP esta listo para funcionar!")
    
except Exception as e:
    print(f"[ERROR] Error de autenticacion: {e}")
    print("\nVerifica que:")
    print("1. El archivo service-account.json existe y es valido")
    print("2. Las APIs estan habilitadas en Google Cloud Console")
    print("3. La carpeta de Drive esta compartida con el Service Account")
