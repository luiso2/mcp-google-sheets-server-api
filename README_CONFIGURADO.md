# MCP Google Sheets - CONFIGURADO Y LISTO ✅

## Estado: FUNCIONANDO CORRECTAMENTE

### 📋 Información de Configuración:
- **Service Account Email:** sheet-de-esencial-pack@absolute-codex-469116-k9.iam.gserviceaccount.com
- **Drive Folder ID:** 1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ
- **Proyecto GCP:** absolute-codex-469116-k9

### 🚀 Cómo Ejecutar el Servidor:

#### Opción 1: Usando el script batch (Recomendado)
```cmd
C:\MCPS\mcp-google-sheets\run_server.bat
```

#### Opción 2: Manualmente
```cmd
cd C:\MCPS\mcp-google-sheets
set SERVICE_ACCOUNT_PATH=C:\MCPS\mcp-google-sheets\credentials\service-account.json
set DRIVE_FOLDER_ID=1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ
uv run mcp-google-sheets
```

### 🔌 Integración con Claude Desktop:

1. Abre el archivo de configuración de Claude Desktop:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Agrega o actualiza la configuración con:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "C:\\MCPS\\mcp-google-sheets\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_google_sheets"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "C:\\MCPS\\mcp-google-sheets\\credentials\\service-account.json",
        "DRIVE_FOLDER_ID": "1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ"
      }
    }
  }
}
```

3. Reinicia Claude Desktop para que tome los cambios.

### 📊 Herramientas Disponibles:

- **list_spreadsheets** - Lista todas las hojas de cálculo
- **create_spreadsheet** - Crea una nueva hoja
- **get_sheet_data** - Lee datos de una hoja
- **update_cells** - Actualiza celdas específicas
- **batch_update_cells** - Actualiza múltiples rangos
- **add_rows** - Agrega filas al final
- **list_sheets** - Lista pestañas de una hoja
- **create_sheet** - Crea nueva pestaña
- **share_spreadsheet** - Comparte con usuarios
- Y muchas más...

### 🎯 Ejemplos de Uso en Claude:

- "Lista todas las hojas de cálculo en mi carpeta"
- "Crea una nueva hoja llamada 'Inventario 2025'"
- "Lee los datos de la hoja 'Ventas' en el rango A1:D10"
- "Actualiza la celda B2 con el valor 'Completado'"
- "Agrega estas filas: [['Producto', 'Precio'], ['Laptop', '1200']]"

### ⚠️ Importante:

- La carpeta de Drive debe estar compartida con el Service Account
- El servidor necesita estar ejecutándose para que Claude pueda usarlo
- Si cambias las credenciales, actualiza los archivos correspondientes

### 📁 Estructura de Archivos:
```
C:\MCPS\mcp-google-sheets\
├── credentials\
│   └── service-account.json    ✅ (Configurado)
├── run_server.bat              ✅ (Listo para usar)
├── test_auth.py                ✅ (Script de prueba)
├── claude_config.json          ✅ (Config para Claude)
└── README_CONFIGURADO.md       ✅ (Este archivo)
```

### 🧪 Para Probar la Autenticación:
```cmd
cd C:\MCPS\mcp-google-sheets
uv run python test_auth.py
```

---
**Configuración completada el:** 2025-09-07
