# Configuración del MCP Google Sheets

## ⚠️ IMPORTANTE: Actualiza estos valores antes de ejecutar el servidor

### 1. Service Account
- Descarga el archivo JSON de tu Service Account desde Google Cloud Console
- Guárdalo en: `C:\MCPS\mcp-google-sheets\credentials\service-account.json`
- O actualiza la ruta en `run_server.bat`

### 2. Drive Folder ID
- Crea una carpeta en Google Drive
- Compártela con el email de tu Service Account (con permisos de Editor)
- Copia el ID desde la URL: https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
- Actualiza el valor en `run_server.bat`

### 3. Para ejecutar el servidor:
```cmd
run_server.bat
```

### 4. Para integrar con Claude Desktop:
Agrega esto a tu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "C:\\MCPS\\mcp-google-sheets\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_google_sheets"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "C:\\MCPS\\mcp-google-sheets\\credentials\\service-account.json",
        "DRIVE_FOLDER_ID": "tu_folder_id_aqui"
      }
    }
  }
}
```

## 📁 Estructura de archivos:
```
C:\MCPS\mcp-google-sheets\
├── credentials\
│   └── service-account.json  (debes colocar aquí tu archivo)
├── run_server.bat            (script para ejecutar el servidor)
└── ... (otros archivos del proyecto)
```
