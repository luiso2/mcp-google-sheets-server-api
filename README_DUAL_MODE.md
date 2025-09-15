# MCP Google Sheets - Dual Mode (MCP + HTTP API)

Este servidor ahora soporta dos modos de operación:
1. **Modo MCP**: Para uso con Claude Desktop (protocolo estándar MCP via stdio)
2. **Modo HTTP API**: Para uso con cualquier LLM o aplicación (REST API)

## Instalación

```bash
# Instalar dependencias
pip install -e .

# O con uv
uv pip install -e .
```

## Modo 1: MCP para Claude Desktop (Sin cambios)

### Configuración

Mantén tu configuración actual en Claude Desktop:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\mcp-google-sheets", "mcp-google-sheets"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "path/to/service-account.json",
        "DRIVE_FOLDER_ID": "your-folder-id"
      }
    }
  }
}
```

### Uso

El servidor MCP funciona exactamente igual que antes. Claude Desktop se comunicará automáticamente con el servidor.

## Modo 2: HTTP API para otros LLMs

### Inicio del servidor

```bash
# Opción 1: Comando directo
python -m mcp_google_sheets.api --host 0.0.0.0 --port 8080

# Opción 2: Script instalado
mcp-google-sheets-api --port 8080

# Opción 3: Docker
docker-compose up
```

### Configuración de API Keys

Edita el archivo `config/api_keys.json`:

```json
{
  "my_app": "sk-my-secure-api-key",
  "openai_integration": "sk-openai-key-12345"
}
```

### Documentación interactiva

Una vez iniciado el servidor, accede a:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Uso con Python

```python
from client_example import MCPGoogleSheetsClient

# Inicializar cliente
client = MCPGoogleSheetsClient(
    api_url="http://localhost:8080",
    api_key="sk-my-secure-api-key"
)

# Obtener datos de una hoja
data = client.get_sheet_data(
    spreadsheet_id="your-spreadsheet-id",
    sheet="Sheet1",
    range="A1:C10"
)

# Actualizar celdas
client.update_cells(
    spreadsheet_id="your-spreadsheet-id",
    sheet="Sheet1",
    range="A1:B2",
    data=[["Nuevo", "Valor"], ["Otro", "Dato"]]
)

# Crear nueva hoja de cálculo
new_sheet = client.create_spreadsheet("Mi Nueva Hoja")
print(f"Creada: {new_sheet['spreadsheet']['spreadsheetId']}")
```

### Integración con OpenAI

```python
import openai
from client_example import LLMGoogleSheetsTools

# Configurar herramientas
tools_client = LLMGoogleSheetsTools(
    api_url="http://localhost:8080",
    api_key="sk-my-secure-api-key"
)

# Obtener definición de herramientas para OpenAI
tools = tools_client.get_tools_definition()

# Usar con OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Get data from spreadsheet XYZ sheet Sales"}],
    tools=tools,
    tool_choice="auto"
)

# Ejecutar herramienta si es necesario
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    result = tools_client.execute_tool(
        tool_call.function.name,
        json.loads(tool_call.function.arguments)
    )
```

### Integración con LangChain

```python
from langchain.tools import Tool
from client_example import MCPGoogleSheetsClient

client = MCPGoogleSheetsClient("http://localhost:8080", "sk-key")

# Crear herramientas de LangChain
tools = [
    Tool(
        name="get_sheet_data",
        func=lambda args: client.get_sheet_data(**json.loads(args)),
        description="Get data from Google Sheets"
    ),
    Tool(
        name="update_cells",
        func=lambda args: client.update_cells(**json.loads(args)),
        description="Update cells in Google Sheets"
    )
]
```

## Endpoints disponibles

### Herramientas principales

- `POST /tools/get_sheet_data` - Obtener datos de una hoja
- `POST /tools/get_sheet_formulas` - Obtener fórmulas
- `POST /tools/update_cells` - Actualizar celdas
- `POST /tools/batch_update_cells` - Actualización por lotes
- `POST /tools/add_rows` - Agregar filas
- `POST /tools/create_spreadsheet` - Crear hoja de cálculo
- `POST /tools/create_sheet` - Crear hoja en spreadsheet
- `GET /tools/list_spreadsheets` - Listar hojas de cálculo
- `GET /tools/list_sheets/{spreadsheet_id}` - Listar hojas
- `POST /tools/share_spreadsheet` - Compartir hoja de cálculo
- `POST /tools/rename_sheet` - Renombrar hoja
- `POST /tools/copy_sheet` - Copiar hoja

### Utilidades

- `GET /health` - Estado del servidor
- `GET /docs` - Documentación Swagger
- `GET /openapi.json` - Especificación OpenAPI

## Docker

### Build y ejecución

```bash
# Build
docker build -t mcp-google-sheets-api .

# Ejecutar
docker run -p 8080:8080 \
  -v ./credentials:/app/credentials:ro \
  -v ./config:/app/config:ro \
  -e SERVICE_ACCOUNT_PATH=/app/credentials/service-account.json \
  mcp-google-sheets-api
```

### Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## Seguridad

### API Keys

- Cada cliente debe tener su propia API key
- Las keys se almacenan en `config/api_keys.json`
- Usa keys seguras en producción (mínimo 32 caracteres)

### Mejores prácticas

1. **HTTPS en producción**: Usa un reverse proxy (nginx) con SSL
2. **Rate limiting**: Implementa límites de tasa para prevenir abuso
3. **Monitoreo**: Registra todas las llamadas API
4. **Rotación de keys**: Cambia las API keys periódicamente
5. **Firewall**: Restringe acceso por IP si es posible

## Troubleshooting

### El servidor MCP no funciona

Verifica que las credenciales de Google estén configuradas:
- `SERVICE_ACCOUNT_PATH` apunta a un archivo válido
- El service account tiene permisos en Google Sheets

### El servidor HTTP no inicia

```bash
# Verificar puerto disponible
netstat -an | grep 8080

# Verificar instalación de dependencias
pip list | grep fastapi
```

### Error de autenticación API

- Verifica que el header `X-API-Key` esté presente
- Confirma que la key existe en `config/api_keys.json`

## Migración desde MCP puro

No se requieren cambios. El modo MCP original sigue funcionando exactamente igual.
El modo HTTP es completamente opcional y adicional.

## Ejemplo completo

```python
#!/usr/bin/env python3
import json
from client_example import MCPGoogleSheetsClient

# Conectar al servidor
client = MCPGoogleSheetsClient(
    api_url="http://localhost:8080",
    api_key="sk-my-secure-key"
)

# Crear nueva hoja de cálculo
new_sheet = client.create_spreadsheet("Ventas Q4 2024")
sheet_id = new_sheet['spreadsheet']['spreadsheetId']
print(f"Nueva hoja creada: {sheet_id}")

# Agregar datos
client.update_cells(
    spreadsheet_id=sheet_id,
    sheet="Sheet1",
    range="A1:C3",
    data=[
        ["Producto", "Cantidad", "Precio"],
        ["Widget A", 100, 25.50],
        ["Widget B", 75, 32.00]
    ]
)

# Leer datos
data = client.get_sheet_data(sheet_id, "Sheet1", "A1:C3")
print(json.dumps(data, indent=2))

# Compartir con equipo
client.share_spreadsheet(
    spreadsheet_id=sheet_id,
    email_addresses=["team@example.com"],
    role="writer"
)
```

## Soporte

Para problemas o preguntas:
1. Revisa la documentación en `/docs`
2. Consulta los logs del servidor
3. Abre un issue en GitHub