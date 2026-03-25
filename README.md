# ZekaiBot — Sistema Inteligente de Atención al Cliente
### SekaiTech | Huánuco, Perú

> Asistente virtual con IA local, base de datos real y widget embebible para la web de la empresa.

---

## ¿Qué hace este sistema?

ZekaiBot es un chatbot de atención al cliente que:

- Responde consultas de precios y productos en tiempo real desde la base de datos
- Diagnostica errores técnicos paso a paso
- Crea tickets automáticos cuando escala a un agente humano
- Funciona 24/7 sin intervención humana
- Usa IA local (Ollama) — sin costos de API externos

---

## Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL 16 + pgvector |
| ORM | SQLAlchemy 2.0 |
| IA local | Ollama + qwen2.5:3b |
| Autenticación | JWT + bcrypt |
| Frontend | HTML + CSS + JavaScript puro |

---

## Requisitos previos

Antes de empezar necesitas tener instalado:

- **WSL Ubuntu 24.04** (en Windows) o Linux/macOS
- **Python 3.11+**
- **PostgreSQL 16**
- **Ollama**
- **Git**

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/zekaibot.git
cd zekaibot/backend
```

### 2. Instalar PostgreSQL

```bash
sudo apt update
sudo service postgresql start
```

### 3. Instalar pgvector

```bash
sudo apt install postgresql-16-pgvector -y
```

### 4. Crear la base de datos

```bash
sudo -u postgres psql
```

Dentro de psql ejecuta:

```sql
CREATE DATABASE techbot;
CREATE USER techbot_user WITH PASSWORD 'techbot2025';
GRANT ALL PRIVILEGES ON DATABASE techbot TO techbot_user;
\c techbot
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 5. Ejecutar el schema

```bash
sudo -u postgres psql -d techbot -f ../db/schema.sql
```

Dar permisos al usuario:

```bash
sudo -u postgres psql -d techbot -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO techbot_user; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO techbot_user;"
```

### 6. Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Si hay error con bcrypt:

```bash
pip uninstall bcrypt -y && pip install bcrypt==4.0.1
```

### 7. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Abre `.env` y completa los valores:

```env
DATABASE_URL=postgresql://techbot_user:TU_PASSWORD@localhost:5432/techbot
REDIS_URL=redis://localhost:6379
SECRET_KEY=cambia_esto_por_una_clave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ANTHROPIC_API_KEY=no-se-usa
GOOGLE_API_KEY=no-se-usa
APP_NAME=ZekaiBot
APP_VERSION=1.0.0
DEBUG=True
```

### 8. Instalar Ollama y el modelo de IA

```bash
sudo apt install zstd -y
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b
```

Verificar que funciona:

```bash
ollama run qwen2.5:3b "hola"
```

### 9. Importar el catálogo de productos (opcional)

Si tienes el archivo SQL del catálogo de la tienda:

```bash
sudo apt install mysql-server -y
sudo service mysql start
sudo mysql -e "CREATE DATABASE sekaitech;"
sudo mysql sekaitech < tu_catalogo.sql

# Extraer productos a JSON
python3 scripts/exportar_catalogo.py

# Importar a PostgreSQL
python3 scripts/importar_catalogo.py
```

### 10. Arrancar el servidor

```bash
uvicorn main:app --reload
```

Deberías ver:

```
✅ Conexión a PostgreSQL exitosa
🚀 Iniciando ZekaiBot v1.0.0
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## Usar el sistema

### API Docs (Swagger)

Abre en el navegador:

```
http://127.0.0.1:8000/docs
```

### Widget de chat

Abre directamente en el navegador:

```
frontend/widget/widget.html
```

Asegúrate de que el servidor esté corriendo antes de abrir el widget.

---

## Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| GET | `/api/v1/auth/me` | Ver usuario actual |
| POST | `/api/v1/chat/message` | Enviar mensaje al bot |
| GET | `/api/v1/chat/history/{id}` | Ver historial de conversación |
| GET | `/health` | Estado del servidor |

---

## Estructura del proyecto

```
backend/
├── main.py                  # Punto de entrada FastAPI
├── requirements.txt         # Dependencias Python
├── catalogo.json            # Catálogo de productos (generado)
├── .env                     # Variables de entorno (NO subir a git)
├── .env.example             # Ejemplo de variables de entorno
│
├── core/
│   ├── config.py            # Configuración general
│   ├── database.py          # Conexión PostgreSQL
│   └── security.py          # JWT y bcrypt
│
├── models/                  # Modelos ORM (27 tablas)
│   ├── user.py
│   ├── catalog.py
│   └── all_models.py
│
├── schemas/                 # Validación Pydantic
│   └── user.py
│
├── api/v1/                  # Endpoints REST
│   ├── router.py
│   ├── auth.py
│   └── chat.py
│
├── services/                # Lógica de negocio
│   ├── chat_service.py      # Orquesta la conversación
│   ├── auth_service.py      # Autenticación
│   ├── rag_service.py       # Búsqueda en catálogo (RAG)
│   └── ai/
│       └── claude.py        # Motor de IA (Ollama)
│
├── repositories/            # Consultas a la BD
│   └── user_repo.py
│
└── db/
    └── schema.sql           # Schema completo de la BD

frontend/
└── widget/
    └── widget.html          # Chat widget standalone
```

---

## Cómo funciona el RAG

Cuando el cliente escribe un mensaje:

1. El sistema extrae palabras clave del mensaje
2. Busca productos relevantes en `catalogo.json` (en memoria)
3. Inyecta los productos encontrados en el prompt de la IA
4. La IA responde con precios y datos reales

Esto permite que el bot responda preguntas como "¿cuánto cuesta una impresora Epson?" con el precio exacto de la base de datos sin necesidad de entrenar el modelo.

---

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@localhost/db` |
| `SECRET_KEY` | Clave para firmar JWT | Cadena aleatoria larga |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token | `60` |
| `APP_NAME` | Nombre de la app | `ZekaiBot` |
| `DEBUG` | Modo debug | `True` en desarrollo |

---

## Solución de problemas comunes

**Error: `permission denied for table`**
```bash
sudo -u postgres psql -d techbot -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO techbot_user; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO techbot_user;"
```

**Error: `bcrypt has no attribute __about__`**
```bash
pip uninstall bcrypt -y && pip install bcrypt==4.0.1
```

**Error: `proxies` en Anthropic**
```bash
pip install anthropic --upgrade
```

**Ollama no responde**
```bash
ollama serve &
ollama run qwen2.5:3b "test"
```

**PostgreSQL no arranca en WSL**
```bash
sudo service postgresql start
```

Para que arranque automáticamente al abrir WSL:
```bash
echo "sudo service postgresql start" >> ~/.bashrc
```

---

## Datos de la empresa configurados

El bot está configurado con los datos reales de SekaiTech:

- **Dirección:** Jr. Huallayco 1135 - Huánuco, Perú
- **WhatsApp:** 933573985 / 991375813
- **Email:** ventas@sekaitech.com.pe
- **Web:** https://sekaitech.com.pe
- **Horarios:** Lunes a Sábado 8:00am - 7:00pm

Para cambiar estos datos edita el `SYSTEM_PROMPT` en `services/ai/claude.py`.


## Autor

**Josias** — Practicante de Desarrollo de Software  
SekaiTech — Huánuco, Perú — 2025


---

# 🏢 Grupo Almerco - Evaluación de Desempeño Técnico (Practicantes)

> **Proyecto:** Backend API con FastAPI, IA Local (Ollama) y Arquitectura RAG  
> **Nivel de Impacto:** Alto 🚀 (Excelente base arquitectónica y elección de *stack*. Demuestra gran potencial para productos SaaS, pero requiere madurez urgente en DevOps, Seguridad y Escalamiento).

| Criterio | Resultado | Estado |
| :--- | :---: | :---: |
| **Calificación Final** | **16 / 20** | 🟡 Aprobado con Observaciones |
| **Arquitectura y Diseño** | Excelente | 🌟 |
| **Implementación IA (RAG)** | Bueno (Prototipo) | ✅ |
| **DevOps, Seguridad y QA**| Deficiente | ❌ |

---

## 🎯 1. Resumen Ejecutivo

El proyecto destaca por una arquitectura modular impecable, respetando el patrón `controller-service-repository`, lo cual es fundamental para construir productos escalables. La integración de un motor de IA local (Ollama) demuestra una visión técnica orientada a reducir costos operativos y mantener la privacidad, aportando un alto valor de negocio al automatizar la atención al cliente con datos reales.

Sin embargo, el sistema actual opera bajo el paradigma de "funciona en mi máquina". Para considerar este backend listo para un entorno de producción, es estrictamente necesario implementar prácticas de seguridad (protección de *endpoints* y secretos), observabilidad, contenerización y evolucionar el motor RAG hacia una base de datos vectorial real.

---

## 🟢 2. Análisis de Fortalezas (Lo que se hizo muy bien)

* **Arquitectura de Capas:** La separación en `api/`, `services/`, `repositories/`, `models/` y `core/` es un estándar de la industria. Esto facilitará enormemente la división de responsabilidades y la futura implementación de pruebas.
* **Stack Tecnológico Moderno:** El uso de `FastAPI` y `SQLAlchemy 2.0` es totalmente acertado para el ecosistema actual de Python, garantizando un buen rendimiento asíncrono.
* **Visión de Producto:** La implementación de un RAG, incluso en su fase inicial, resuelve un problema real de negocio, permitiendo escalar la atención humana de manera eficiente.

---

## 🔴 3. Áreas Críticas de Mejora (Riesgos de Ejecución)

<details>
<summary><b>⚠️ Seguridad y Vulnerabilidades Expuestas</b></summary>
<br>

* **El Problema:** La gestión de secretos y el control de tráfico son insuficientes. Existe riesgo de exponer el `.env` en *commits*, los *tokens* JWT carecen de mecanismos de revocación, y la falta de *rate-limiting* en *endpoints* públicos (login, chat) abre la puerta a ataques de fuerza bruta o saturación de la IA. Adicionalmente, hay riesgo latente de *Prompt Injection*.
* **La Solución:** Implementar `git-secrets`, configurar un *rate-limiter* (ej. `slowapi`), sanitizar estrictamente los *inputs* antes de enviarlos a Ollama y usar gestores de secretos para producción.
</details>

<details>
<summary><b>⚠️ Escalabilidad del Motor RAG y Datos</b></summary>
<br>

* **El Problema:** El uso de un `catalogo.json` en memoria es válido para un prototipo, pero colapsará con catálogos extensos. Además, sin índices vectoriales, la búsqueda semántica perderá precisión.
* **La Solución:** Dado que ya se usa PostgreSQL, el paso natural es **migrar a `pgvector`**. Se deben crear tablas vectoriales con índices (`hnsw` o `ivfflat`) y añadir una capa de caché (Redis) con TTL para consultas repetitivas.
</details>

<details>
<summary><b>⚠️ Ausencia de DevOps, CI/CD y Observabilidad</b></summary>
<br>

* **El Problema:** Las instrucciones de despliegue son manuales. No hay `Dockerfile`, `docker-compose.yml`, *pipelines* de CI/CD, ni un sistema de *logs* estructurados, lo que hace que diagnosticar latencias (App ↔ Ollama ↔ DB) sea imposible.
* **La Solución:** Contenerizar toda la infraestructura, configurar GitHub Actions para validación continua y adoptar librerías como `structlog` o `loguru`.
</details>

---

## 🛠️ 4. Oportunidades de Refactorización (Calidad de Código y QA)

* **Tipado Estricto y Linters:** Aunque FastAPI se basa en tipos, no hay evidencia del uso de `mypy` ni validación continua. Se debe integrar `ruff`/`flake8` y `black` mediante un *hook* de `pre-commit`.
* **Pruebas Automatizadas (Ausentes):** La carpeta `tests/` está vacía. Es innegociable contar con pruebas unitarias para `auth_service` y `rag_service`, además de pruebas de integración para los flujos críticos (login/chat) y *mocks* para el cliente de Ollama.
* **Privacidad (PII):** Es crítico implementar enmascaramiento de datos (PII masking) para evitar que información sensible del usuario se filtre en los *logs* o se envíe accidentalmente en los *prompts*.

---

## 📝 5. Plan de Acción (Roadmap de Correcciones)

Para consolidar este proyecto, el practicante debe ejecutar el siguiente plan por fases:

### Fase 1: Corto Plazo (1-2 semanas) - Estabilidad y Estándares
- [ ] Añadir `.gitignore` (verificando exclusión del `.env`) e implementar `git-secrets`.
- [ ] Configurar `pre-commit` con `black`, `ruff` e `isort`.
- [ ] Escribir los primeros *tests* unitarios básicos para `auth_service` y `chat_service`.
- [ ] Mejorar la documentación: Añadir `CONTRIBUTING.md`, `ARCHITECTURE.md` (con un diagrama de componentes) y `RUNNING.md`.

### Fase 2: Mediano Plazo (3-6 semanas) - Infraestructura y Datos
- [ ] **Dockerización:** Crear `Dockerfile` de la app y un `docker-compose.yml` que orqueste la App, PostgreSQL y Redis.
- [ ] **Migración RAG:** Reemplazar el JSON en memoria por tablas vectoriales usando PostgreSQL + `pgvector`.
- [ ] **Observabilidad:** Implementar *logging* estructurado y añadir *healthchecks* detallados (`/health`).

### Fase 3: Largo Plazo (3 meses) - Operación a Escala
- [ ] Implementar caché con Redis para respuestas frecuentes.
- [ ] Evaluar y documentar estrategias de escalado horizontal para Ollama (o migración a servicio gestionado).
- [ ] Añadir métricas básicas para monitoreo (Prometheus).

---

## Licencia

Este proyecto es privado y de uso exclusivo de SekaiTech.
