# Clínica Sanitaria – Evaluación Sumativa 3 (TI3021)

Proyecto Python con arquitectura MVC, autenticación, consumo de servicios externos, manejo de errores y persistencia SQLite.

> **Nota sobre el contexto:** el proyecto base recibido corresponde a Clínica Sanitaria y su API OpenFDA. Para cubrir los ejemplos de la guía ES3 se conservaron sus módulos y se añadieron consultas de clima (Open-Meteo) y tipo de cambio (Frankfurter). Si el docente exige que el contexto sea exclusivamente EcoTech Solutions, se debe confirmar si acepta el caso clínico adaptado o solicitar autorización para cambiar el contexto.

## 1. Requisitos

- Python 3.10 o superior.
- Conexión a Internet para consultar las APIs.
- Windows, Linux o macOS.

## 2. Instalación

1. Descomprimir la carpeta del proyecto.
2. Abrirla en Visual Studio Code.
3. Abrir Terminal > Nueva terminal.
4. Crear entorno virtual (recomendado):

```bash
python -m venv .venv
```

Activarlo en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Windows CMD:

```bat
.venv\Scripts\activate.bat
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

5. Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## 3. Configuración segura

1. Copiar `.env.example` y renombrar la copia a `.env`.
2. Cambiar `ADMIN_INITIAL_CLAVE` por una contraseña propia de al menos 10 caracteres que incluya letras y números.
3. No compartir el archivo `.env` ni subirlo a repositorios públicos.
4. La API OpenFDA y los servicios Open-Meteo/Frankfurter no requieren clave para las consultas implementadas.

El usuario administrador inicial se crea solo cuando la tabla de usuarios está vacía. Si ya existe una base de datos con usuarios, cambiar el `.env` no reemplaza sus contraseñas.

## 4. Ejecutar

Desde la carpeta raíz:

```bash
python main.py
```

La base SQLite `clinica.db` se crea automáticamente. El primer inicio crea el usuario administrador configurado en `.env` si no existen usuarios.

## 5. Funcionalidades

### Sistema original

- Inicio de sesión y gestión de usuarios.
- Gestión de pacientes y departamentos.
- Búsqueda de medicamentos mediante OpenFDA.
- Emisión y consulta de recetas guardadas en SQLite.
- Catálogo local de contingencia para búsquedas de medicamentos cuando no hay conexión.

### Funcionalidades agregadas para ES3

En el menú principal, seleccionar **5. Servicios externos: clima y tipo de cambio**.

1. **Clima:** escribir una ciudad (por ejemplo, Chillán). Open-Meteo obtiene coordenadas y condiciones actuales: temperatura, humedad, estado del tiempo y viento.
2. **Tipo de cambio:** ingresar moneda de origen, moneda de destino y cantidad. Ejemplo: USD, CLP, 100. Frankfurter entrega la tasa disponible y el programa calcula el equivalente.
3. **Historial:** las consultas exitosas se almacenan localmente en la tabla `consulta_externa` de SQLite.

Códigos de moneda habilitados como ejemplo: CLP, USD, EUR, BRL, ARS, GBP, JPY, entre otros definidos en `services/servicios_externos_service.py`.

## 6. Seguridad aplicada

- Contraseñas nuevas almacenadas con PBKDF2-HMAC-SHA256, sal aleatoria individual y 310.000 iteraciones.
- Comparación de hashes con `hmac.compare_digest`.
- Compatibilidad con hashes SHA-256 antiguos y migración a PBKDF2 al iniciar sesión correctamente cuando la contraseña antigua cumple la longitud mínima nueva (10 caracteres). Las contraseñas antiguas más cortas siguen funcionando temporalmente, pero deben actualizarse.
- Variables de configuración y secretos fuera del código mediante `.env`.
- Validación de ciudad, moneda, cantidad y término de búsqueda.
- Consultas SQL parametrizadas.
- Timeout en las solicitudes HTTP.
- Control de errores de conexión y códigos HTTP.
- Mensajes de error controlados sin imprimir detalles internos o credenciales.
- Acceso a las opciones del menú solo después de autenticar al usuario.

**Limitación:** el bloqueo de intentos de inicio de sesión se aplica durante la ejecución actual del proceso; no es un bloqueo persistente por cuenta ni un sistema multiusuario de producción.

## 7. Pruebas manuales recomendadas

| Prueba | Acción | Resultado esperado |
|---|---|---|
| Login correcto | Ingresar usuario y contraseña configurados | Acceso al menú |
| Login incorrecto | Ingresar una contraseña equivocada | Acceso rechazado |
| Campos vacíos | Enviar usuario o contraseña vacíos | Validación y rechazo |
| Clima | Consultar Chillán con Internet | Temperatura, humedad, estado y viento |
| Ciudad inexistente | Escribir una ciudad no encontrada | Mensaje controlado, sin cerrar el programa |
| Monedas | Convertir 100 USD a CLP | Tasa y resultado calculado |
| Moneda inválida | Escribir `XXX` | Entrada rechazada |
| Cantidad inválida | Escribir cero, texto o número negativo | Entrada rechazada |
| Sin Internet | Desconectar la red y consultar | Mensaje controlado; el programa sigue activo |
| Historial | Abrir últimas consultas | Consultas exitosas previamente guardadas |
| Receta | Emitir una receta para un paciente registrado | Receta persistida en SQLite |

## 8. Auditoría de seguridad con Bandit

Ejecutar desde la raíz:

```bash
bandit -r config controllers models services views -f txt
```

Revisar cada hallazgo. No todos los avisos implican una vulnerabilidad explotable; documentar cuáles se corrigieron y justificar los que no correspondan.

También se puede comprobar la sintaxis:

```bash
python -m compileall config controllers models services views main.py
```

## 9. Evidencias para el informe o presentación

Guardar capturas de:

1. Inicio de sesión correcto.
2. Rechazo de credenciales incorrectas.
3. Consulta de clima con resultados.
4. Consulta de tipo de cambio con tasa y cálculo.
5. Historial de consultas guardadas.
6. Mensaje controlado ante ciudad o moneda inválida.
7. Resultado de Bandit y explicación de los cambios.

## 10. Uso de IA y justificación técnica

La IA puede ayudar a revisar código, pero el estudiante debe validar cada sugerencia. Para documentarlo, registrar: fragmento revisado, riesgo detectado, cambio aplicado, prueba realizada y motivo para aceptar o descartar la recomendación.

## 11. Estructura principal

```text
config/       Configuración y conexión SQLite
controllers/  Controladores MVC
models/       Entidades y acceso a datos (DAO)
services/     Consumo de APIs y lógica de servicios
views/        Menús e interacción por consola
main.py       Punto de entrada
requirements.txt
.env.example
```

## 12. Pruebas automatizadas incluidas

Ejecutar:

```bash
python -m unittest discover -s tests -v
```

Estas pruebas comprueban el hash PBKDF2, la verificación de contraseñas y validaciones de ciudad y moneda. No sustituyen las pruebas manuales de conexión real a Internet.
