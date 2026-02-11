# Platziflix - Proyecto Multi-plataforma

## Visión General

Platziflix es una plataforma de cursos online con **arquitectura multi-plataforma** que incluye:
- **Backend**: API REST con FastAPI + PostgreSQL
- **Frontend**: Aplicación web con Next.js 15 + React 19
- **Mobile**: Apps nativas Android (Kotlin + Jetpack Compose) e iOS (Swift + SwiftUI)

**Arquitectura**: Microservicios desacoplados con API REST como única fuente de datos.

---

## Stack Tecnológico Completo

### Backend (FastAPI + Python)
- **Framework**: FastAPI ≥0.104.0
- **Runtime**: Python 3.11-slim
- **Base de datos**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Driver DB**: psycopg2-binary ≥2.9.0
- **Migraciones**: Alembic ≥1.13.0
- **Validación**: Pydantic ≥2.0.0 + pydantic-settings
- **Servidor**: Uvicorn[standard] ≥0.24.0
- **Testing**: Pytest ≥7.0.0 + httpx + pytest-asyncio
- **Container**: Docker + Docker Compose
- **Package Manager**: UV (reemplazo de pip)
- **Puerto**: 8000
- **Docs**: FastAPI Swagger UI en `/docs`

### Frontend (Next.js + React)
- **Framework**: Next.js 15.3.3 (App Router)
- **UI Library**: React 19.0.0
- **Lenguaje**: TypeScript 5 (strict mode)
- **Estilos**: SCSS + CSS Modules
- **Testing**: Vitest 3.2.3 + React Testing Library 16.3.0
- **HTTP Client**: Fetch API (nativa)
- **Fonts**: Geist Sans & Geist Mono (variable fonts)
- **Build Tool**: Turbopack (desarrollo)
- **Package Manager**: Yarn
- **Puerto**: 3000

### Mobile Android
- **Lenguaje**: Kotlin
- **UI Framework**: Jetpack Compose + Material 3
- **HTTP Client**: Retrofit 2.9.0 + OkHttp 4.12.0
- **JSON Parser**: Gson 2.10.1
- **Async**: Coroutines 1.7.3 + Flow
- **Image Loading**: Coil 2.5.0
- **Architecture**: MVVM + MVI + Clean Architecture
- **Testing**: JUnit + Coroutines Test
- **DI**: Manual (AppModule)

### Mobile iOS
- **Lenguaje**: Swift
- **UI Framework**: SwiftUI
- **HTTP Client**: URLSession (nativo)
- **JSON Parser**: Codable (nativo)
- **Async**: async/await + Task (nativo)
- **Reactive**: Combine (nativo)
- **Image Loading**: AsyncImage (nativo)
- **Architecture**: MVVM + Repository Pattern + Clean Architecture
- **Testing**: XCTest (pendiente implementar)
- **DI**: Initializer-based

---

## Estructura del Proyecto

```
claude-code/
├── Backend/
│   ├── app/
│   │   ├── core/              # Configuración (config.py)
│   │   ├── db/                # Database setup + seeding
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── base.py        # BaseModel con timestamps + soft delete
│   │   │   ├── course.py
│   │   │   ├── teacher.py
│   │   │   ├── lesson.py
│   │   │   ├── course_teacher.py
│   │   │   └── course_rating.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── rating.py
│   │   ├── services/          # Business logic layer
│   │   │   └── course_service.py
│   │   ├── alembic/           # Database migrations
│   │   │   ├── versions/
│   │   │   └── env.py
│   │   ├── tests/             # Unit + integration tests
│   │   └── main.py            # FastAPI app
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── Makefile               # Comandos de desarrollo
│   └── pyproject.toml         # Dependencias UV
│
├── Frontend/
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx       # Home (catálogo)
│   │   │   ├── course/[slug]/ # Detalle de curso
│   │   │   └── classes/[class_id]/ # Reproductor
│   │   ├── components/        # React components
│   │   │   ├── Course/
│   │   │   ├── CourseDetail/
│   │   │   ├── VideoPlayer/
│   │   │   └── StarRating/    # Sistema de estrellas
│   │   ├── services/
│   │   │   └── ratingsApi.ts  # API client
│   │   ├── types/             # TypeScript types
│   │   │   ├── index.ts
│   │   │   └── rating.ts
│   │   ├── styles/            # SCSS global
│   │   │   ├── vars.scss      # Variables de color
│   │   │   └── reset.scss
│   │   └── test/              # Test setup
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── package.json
│
└── Mobile/
    ├── PlatziFlixAndroid/
    │   └── app/src/main/java/com/espaciotiago/platziflixandroid/
    │       ├── data/
    │       │   ├── entities/     # DTOs
    │       │   ├── mappers/      # DTO → Domain
    │       │   ├── network/      # Retrofit + NetworkModule
    │       │   └── repositories/ # Repository implementations
    │       ├── domain/
    │       │   ├── models/       # Domain models
    │       │   └── repositories/ # Repository interfaces
    │       ├── presentation/
    │       │   └── courses/
    │       │       ├── components/
    │       │       ├── screen/
    │       │       ├── state/    # UI State
    │       │       └── viewmodel/
    │       ├── di/               # Dependency Injection
    │       └── ui/theme/         # Material 3 theme
    │
    └── PlatziFlixiOS/
        └── PlatziFlixiOS/
            ├── Data/
            │   ├── Entities/     # DTOs
            │   ├── Mapper/       # DTO → Domain
            │   └── Repositories/ # Repository implementations
            ├── Domain/
            │   ├── Models/       # Domain models
            │   └── Repositories/ # Repository protocols
            ├── Presentation/
            │   ├── ViewModels/   # @MainActor ViewModels
            │   └── Views/        # SwiftUI views
            ├── Services/
            │   ├── NetworkService.swift
            │   ├── NetworkManager.swift
            │   └── APIEndpoint.swift
            └── ContentView.swift
```

---

## Modelo de Datos (PostgreSQL)

### BaseModel (Común a todas las tablas)
```python
id: Integer (PK)
created_at: DateTime (default=utcnow)
updated_at: DateTime (onupdate=utcnow)
deleted_at: DateTime (nullable)  # Soft delete pattern
```

### Course (courses)
```python
id: Integer (PK)
name: String(255)
description: Text
thumbnail: String(500)  # URL de imagen
slug: String(255)       # Unique, indexed (SEO)
created_at, updated_at, deleted_at

# Relaciones:
teachers: Many-to-Many (via course_teachers)
lessons: One-to-Many
ratings: One-to-Many (via course_ratings)

# Propiedades computadas:
average_rating: float   # Promedio de ratings activos
total_ratings: int      # Cantidad de ratings activos
```

### Teacher (teachers)
```python
id: Integer (PK)
name: String(255)
email: String(255)  # Unique, indexed
created_at, updated_at, deleted_at

# Relaciones:
courses: Many-to-Many (via course_teachers)
```

### Lesson (lessons)
```python
id: Integer (PK)
course_id: Integer (FK → courses.id, indexed)
name: String(255)
description: Text
slug: String(255)
video_url: String(500)  # URL a YouTube/Vimeo
created_at, updated_at, deleted_at

# Relaciones:
course: Many-to-One
```

### CourseTeacher (course_teachers)
```python
course_id: Integer (FK → courses.id, PK)
teacher_id: Integer (FK → teachers.id, PK)
# Composite PK: (course_id, teacher_id)
```

### CourseRating (course_ratings) ⭐ NUEVO
```python
id: Integer (PK)
course_id: Integer (FK → courses.id, indexed)
user_id: Integer (indexed, sin FK - futuro: tabla users)
rating: Integer  # CHECK: 1 <= rating <= 5
created_at, updated_at, deleted_at

# Constraints:
UNIQUE(course_id, user_id, deleted_at)
  → Permite 1 rating ACTIVO por user+course
  → Permite histórico de ratings eliminados

# Relaciones:
course: Many-to-One
```

---

## API Endpoints

### Core Endpoints
| Método | Endpoint | Descripción | Status |
|--------|----------|-------------|--------|
| GET | `/` | Bienvenida | 200 |
| GET | `/health` | Health check + DB connectivity | 200 |
| GET | `/courses` | Lista todos los cursos con stats | 200 |
| GET | `/courses/{slug}` | Detalle de curso por slug | 200/404 |
| GET | `/classes/{class_id}` | Datos de clase/lección | 200/404 |

### Rating Endpoints ⭐ NUEVO
| Método | Endpoint | Descripción | Status |
|--------|----------|-------------|--------|
| POST | `/courses/{id}/ratings` | Crear o actualizar rating | 201/404/400 |
| GET | `/courses/{id}/ratings` | Listar todos los ratings | 200/404 |
| GET | `/courses/{id}/ratings/stats` | Stats agregadas (avg, total, distribution) | 200/404 |
| GET | `/courses/{id}/ratings/user/{user_id}` | Rating específico del usuario | 200/204 |
| PUT | `/courses/{id}/ratings/{user_id}` | Actualizar rating existente | 200/404/400 |
| DELETE | `/courses/{id}/ratings/{user_id}` | Soft delete de rating | 204/404 |

### Ejemplos de Response

**GET /courses:**
```json
[
  {
    "id": 1,
    "name": "Curso de React",
    "description": "...",
    "thumbnail": "https://...",
    "slug": "curso-de-react",
    "average_rating": 4.35,
    "total_ratings": 142
  }
]
```

**GET /courses/{slug}:**
```json
{
  "id": 1,
  "name": "Curso de React",
  "description": "...",
  "thumbnail": "...",
  "slug": "curso-de-react",
  "teacher_id": [1, 2],
  "classes": [
    {"id": 1, "name": "Introducción", "slug": "...", "description": "..."}
  ],
  "average_rating": 4.35,
  "total_ratings": 142,
  "rating_distribution": {"1": 5, "2": 10, "3": 25, "4": 50, "5": 52}
}
```

---

## Arquitectura por Capa

### Backend - Service Layer Pattern

```
FastAPI Routes (main.py)
    ↓ Dependency Injection
CourseService (services/course_service.py)
    ↓ Query optimization + Business logic
SQLAlchemy Models (models/*.py)
    ↓ ORM
PostgreSQL Database
```

**Características:**
- Service Layer centraliza lógica de negocio
- Dependency Injection con FastAPI Dependencies
- Queries optimizadas con joinedload (evita N+1)
- Soft delete en todas las queries
- Validaciones a nivel servicio
- Agregaciones SQL (COUNT, AVG, GROUP BY)

### Frontend - Server Components Pattern

```
User Request
    ↓
Next.js App Router (app/*/page.tsx)
    ↓ Server Component
fetch() API call
    ↓
Backend API (localhost:8000)
    ↓
Response JSON → TypeScript types
    ↓
React Component render
```

**Características:**
- Server Components por defecto (zero JS al cliente)
- Client Components solo cuando necesario (error.tsx)
- TypeScript strict para type safety
- CSS Modules para encapsulación de estilos
- StarRating component con SVG gradientes
- ratingsApi service con timeout y error handling

### Mobile Android - MVVM + MVI + Clean Architecture

```
User Interaction (Compose UI)
    ↓
CourseListViewModel (MVI Events)
    ↓ viewModelScope.launch
CourseRepository interface
    ↓
RemoteCourseRepository
    ↓ Retrofit + Coroutines
ApiService (Retrofit interface)
    ↓ HTTP
Backend API (10.0.2.2:8000)
    ↓
Response JSON → CourseDTO
    ↓ CourseMapper
Domain Model (Course)
    ↓ StateFlow emission
UI Recomposition
```

**Características:**
- Clean Architecture (Data/Domain/Presentation)
- MVVM + MVI para gestión de estado
- StateFlow para reactive UI
- Retrofit + OkHttp con timeouts (30s)
- Mapper pattern (DTO → Domain)
- Dependency Injection manual (AppModule)
- Jetpack Compose declarativo

### Mobile iOS - MVVM + Repository Pattern + Clean Architecture

```
User Interaction (SwiftUI)
    ↓
CourseListViewModel (ObservableObject)
    ↓ Task { await }
CourseRepository protocol
    ↓
RemoteCourseRepository
    ↓ async/await
NetworkService (URLSession)
    ↓ HTTP
Backend API (localhost:8000)
    ↓
Response JSON → CourseDTO (Codable)
    ↓ CourseMapper
Domain Model (Course)
    ↓ @Published update
SwiftUI View re-render
```

**Características:**
- Clean Architecture (Data/Domain/Presentation)
- MVVM con @MainActor para thread safety
- @Published para reactive updates
- URLSession nativo con async/await
- Codable para JSON parsing
- Mapper pattern (DTO → Domain)
- Combine para debouncing de búsqueda
- SwiftUI declarativo + Design System

---

## Flujo de Datos End-to-End

### Ejemplo: Cargar lista de cursos

```
1. USER INTERACTION
   - Web: Navega a localhost:3000
   - Android: Abre app → CourseListScreen
   - iOS: Abre app → CourseListView

2. CLIENT INICIALIZATION
   - Web: Server Component ejecuta fetch()
   - Android: ViewModel.loadCourses() → viewModelScope
   - iOS: ViewModel.loadCourses() → Task { await }

3. HTTP REQUEST
   GET /courses
   - Web: http://localhost:8000/courses
   - Android: http://10.0.2.2:8000/courses (emulador)
   - iOS: http://localhost:8000/courses (simulador)

4. BACKEND PROCESSING
   FastAPI Endpoint
   ├─ Dependency: get_course_service(db)
   ├─ Service: courseService.get_all_courses()
   ├─ Query: SELECT courses + joinedload(ratings)
   ├─ Compute: average_rating, total_ratings
   └─ Return: List[CourseDTO]

5. RESPONSE MAPPING
   - Web: JSON → TypeScript Course[]
   - Android: JSON → CourseDTO[] → CourseMapper → Course[]
   - iOS: JSON → CourseDTO[] → CourseMapper → [Course]

6. STATE UPDATE
   - Web: React render (Server Component)
   - Android: StateFlow.value = newState → Recomposition
   - iOS: @Published courses = [...] → View re-render

7. UI RENDER
   - Web: Grid con Course cards
   - Android: LazyColumn con CourseCard
   - iOS: ScrollView con CourseCardView
```

---

## Patrones Arquitectónicos Utilizados

### 1. Clean Architecture (3 Capas)
- **Presentation**: UI + ViewModels/Controllers
- **Domain**: Models + Repository Interfaces + Business Rules
- **Data**: Repository Implementations + DTOs + API Clients

### 2. MVVM (Model-View-ViewModel)
- **Backend**: No aplica (API REST)
- **Frontend**: Server Components (sin VM necesario)
- **Android**: ViewModel + StateFlow
- **iOS**: ViewModel + @Published

### 3. MVI (Model-View-Intent) - Android
- **Intent**: Eventos explícitos (CourseListUiEvent)
- **Model**: Estado UI (CourseListUiState)
- **View**: Compose UI que reacciona al estado

### 4. Repository Pattern
- Abstrae la fuente de datos
- Interface en Domain, implementación en Data
- Permite testing con mocks

### 5. Mapper Pattern
- Separa DTOs (API) de Domain Models
- Transformaciones centralizadas
- DTO → Domain mapping

### 6. Service Layer Pattern (Backend)
- Lógica de negocio centralizada
- Reutilizable desde múltiples endpoints
- Validaciones y agregaciones

### 7. Dependency Injection
- **Backend**: FastAPI Dependencies
- **Android**: Manual con AppModule
- **iOS**: Initializer-based

### 8. Soft Delete Pattern (Backend)
- `deleted_at` timestamp en todos los modelos
- Queries filtran `WHERE deleted_at IS NULL`
- Preserva histórico y permite auditoría

---

## Configuración y URLs

### URLs de Desarrollo

| Plataforma | URL Backend | Notas |
|------------|-------------|-------|
| Backend API | `http://localhost:8000` | Docker Compose |
| Frontend Web | `http://localhost:3000` | Yarn dev |
| Android Emulator | `http://10.0.2.2:8000` | IP especial de emulador |
| Android Physical | `http://192.168.1.X:8000` | Cambiar a IP local |
| iOS Simulator | `http://localhost:8000` | Localhost funciona |
| iOS Physical | `http://192.168.1.X:8000` | Cambiar a IP local |

### Base de Datos (Docker)
```yaml
Host: db (en Docker) o localhost (externo)
Port: 5432
User: platziflix_user
Password: platziflix_password
Database: platziflix_db
```

### Variables de Entorno

**Backend (.env):**
```bash
DATABASE_URL=postgresql://platziflix_user:platziflix_password@db:5432/platziflix_db
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Mobile:**
- Android: Hardcoded en `NetworkModule.kt` (cambiar según necesidad)
- iOS: Hardcoded en `CourseAPIEndpoints.swift` (cambiar según necesidad)

---

## Comandos de Desarrollo

### Backend
```bash
cd Backend

# Docker Compose
make start              # Iniciar API + DB (docker-compose up -d)
make stop               # Detener containers
make restart            # Reiniciar containers
make logs               # Ver logs en tiempo real
make logs-api           # Logs solo de API
make logs-db            # Logs solo de DB

# Database
make migrate            # Aplicar migraciones pendientes
make create-migration   # Crear nueva migración (autogenerate)
make seed               # Poblar datos de prueba
make seed-fresh         # Limpiar DB + repoblar
make db-shell           # Entrar a psql

# Testing
make test               # Ejecutar tests
make test-cov           # Tests con coverage

# Limpieza
make clean              # Limpiar containers y volúmenes
```

### Frontend
```bash
cd Frontend

yarn dev                # Servidor desarrollo (localhost:3000)
yarn build              # Build de producción
yarn start              # Servidor producción
yarn lint               # Linter (ESLint)
yarn test               # Tests (Vitest)
yarn test:watch         # Tests en modo watch
```

### Mobile Android
```bash
cd Mobile/PlatziFlixAndroid

./gradlew build         # Compilar
./gradlew test          # Tests unitarios
./gradlew assembleDebug # Generar APK debug
./gradlew installDebug  # Instalar en dispositivo
```

### Mobile iOS
```bash
cd Mobile/PlatziFlixiOS

open PlatziFlixiOS.xcodeproj  # Abrir en Xcode
# Compilar y ejecutar desde Xcode (Cmd+R)
```

---

## Testing

### Backend (Pytest)
- **Ubicación**: `Backend/app/tests/`
- **Coverage**: Endpoints, Services, DB constraints
- **Ejecutar**: `make test`
- **Tests implementados**:
  - ✅ Rating endpoints (HTTP)
  - ✅ CourseService unit tests
  - ✅ Database constraints validation

### Frontend (Vitest + RTL)
- **Ubicación**: `Frontend/src/**/*.test.tsx`
- **Setup**: `src/test/setup.ts` (jsdom + @testing-library/jest-dom)
- **Ejecutar**: `yarn test`
- **Tests implementados**:
  - ✅ StarRating component (exhaustivo)
  - ✅ VideoPlayer component
  - ✅ Course component
  - ✅ ClassPage component

### Mobile Android (JUnit)
- **Ubicación**: `app/src/test/`
- **Framework**: JUnit + Coroutines Test
- **Tests implementados**:
  - ✅ CourseListViewModel (5 tests)
  - Estado inicial, carga exitosa, errores, refresh, limpieza

### Mobile iOS (XCTest)
- **Estado**: Pendiente implementar
- **Framework**: XCTest nativo

---

## Funcionalidades Implementadas

### ✅ Backend
- [x] CRUD de cursos
- [x] Sistema de ratings (crear, leer, actualizar, eliminar)
- [x] Stats de ratings (promedio, total, distribución)
- [x] Soft delete en todos los modelos
- [x] Health checks (API + DB)
- [x] Migraciones automáticas (Alembic)
- [x] Seeding de datos de prueba
- [x] Docker Compose para desarrollo
- [x] Tests unitarios y de integración
- [x] Swagger UI documentation

### ✅ Frontend
- [x] Catálogo de cursos con grid responsivo
- [x] Detalle de curso con lecciones
- [x] Reproductor de video HTML5
- [x] Sistema de estrellas (StarRating readonly)
- [x] Server Components (Next.js 15)
- [x] TypeScript strict
- [x] CSS Modules + SCSS
- [x] Tests de componentes

### ✅ Mobile Android
- [x] Lista de cursos con Compose
- [x] Arquitectura Clean + MVVM + MVI
- [x] Retrofit + Coroutines
- [x] Material Design 3
- [x] Manejo de 4 estados UI (loading, success, error, empty)
- [x] Refresh manual
- [x] Tests de ViewModel

### ✅ Mobile iOS
- [x] Lista de cursos con SwiftUI
- [x] Arquitectura Clean + MVVM
- [x] URLSession + async/await
- [x] Búsqueda con debounce (Combine)
- [x] Pull-to-refresh
- [x] Dark mode support
- [x] Design System

---

## Funcionalidades Pendientes

### 🚧 Backend
- [ ] Autenticación (JWT)
- [ ] Tabla `users` (actualmente user_id no tiene FK)
- [ ] Paginación en endpoints
- [ ] Rate limiting
- [ ] Logging estructurado

### 🚧 Frontend
- [ ] Integración de ratings interactivos
- [ ] Autenticación de usuarios
- [ ] Favoritos/Bookmarks
- [ ] Búsqueda de cursos
- [ ] Filtros por categoría/profesor
- [ ] Progressive Web App (PWA)

### 🚧 Mobile Android
- [ ] Navegación a detalle de curso
- [ ] Reproducción de videos
- [ ] Sistema de ratings interactivo
- [ ] Caché local con Room
- [ ] Paginación infinita
- [ ] Autenticación

### 🚧 Mobile iOS
- [ ] Navegación a detalle de curso
- [ ] Reproducción de videos
- [ ] Sistema de ratings interactivo
- [ ] Caché local con Core Data
- [ ] Paginación infinita
- [ ] Autenticación
- [ ] Tests unitarios (XCTest)

---

## Consideraciones de Desarrollo

### Reglas Generales

1. **Docker obligatorio** para el backend (DB + API)
2. **TypeScript strict** en Frontend (no usar `any`)
3. **Testing requerido** para nuevas funcionalidades
4. **Migraciones automáticas** para cambios de DB (Alembic)
5. **API REST** como única fuente de datos para Frontend/Mobile
6. **Soft delete** obligatorio (nunca DELETE directo)
7. **Validaciones** en backend (Pydantic) y frontend (TypeScript)

### Convenciones de Naming

- **Python (Backend)**: `snake_case` para variables, funciones, archivos
- **TypeScript/JavaScript (Frontend)**: `camelCase` para variables, `PascalCase` para componentes
- **Kotlin (Android)**: `camelCase` para variables, `PascalCase` para clases
- **Swift (iOS)**: `camelCase` para variables, `PascalCase` para tipos

### Comandos de Backend (IMPORTANTE)

⚠️ **Cualquier comando que necesites ejecutar para el Backend debe ser dentro del contenedor de Docker API.**

Antes de ejecutar comandos:
1. Certifica que el contenedor esté funcionando: `make start`
2. Revisa el archivo `Makefile` con los comandos disponibles
3. Usa los comandos del Makefile en lugar de ejecutar directamente

**Ejemplo CORRECTO:**
```bash
make migrate          # En lugar de: docker exec -it api alembic upgrade head
make seed             # En lugar de: docker exec -it api python -m app.db.seed
make test             # En lugar de: docker exec -it api pytest
```

### Flujo de Desarrollo de Nuevas Features

1. **Backend**:
   - Crear modelo en `models/` (con soft delete)
   - Crear migración: `make create-migration`
   - Aplicar migración: `make migrate`
   - Crear schema en `schemas/`
   - Crear servicio en `services/`
   - Crear endpoint en `main.py`
   - Escribir tests en `tests/`
   - Ejecutar tests: `make test`

2. **Frontend**:
   - Crear tipos en `types/`
   - Crear servicio API en `services/` (si necesario)
   - Crear componente en `components/`
   - Escribir tests
   - Integrar en página de `app/`

3. **Mobile**:
   - Crear DTO en `data/entities/`
   - Crear mapper en `data/mappers/`
   - Actualizar repository
   - Actualizar ViewModel
   - Crear/actualizar componentes UI
   - Escribir tests

---

## Observaciones Importantes

### ✅ Fortalezas del Proyecto

1. **Arquitectura limpia y escalable** en todas las capas
2. **Separación de responsabilidades** clara (DTOs vs Models)
3. **Type-safety** en todos los lenguajes
4. **Patrones consistentes** entre plataformas
5. **Testing implementado** en backend y frontend
6. **Docker Compose** facilita desarrollo
7. **Soft delete** permite auditoría
8. **API bien documentada** (Swagger)

### ⚠️ Áreas de Mejora

1. **Tabla `Class` duplicada**: Parece redundante con `Lesson` en backend (verificar)
2. **Sin autenticación**: `user_id` en ratings no tiene FK (futuro: tabla `users`)
3. **Navegación incompleta**: Mobile apps solo tienen lista de cursos
4. **Sin caché local**: Móviles no persisten datos offline
5. **Hardcoded URLs**: Deberían usar variables de entorno
6. **Tests iOS**: No hay tests unitarios aún
7. **Sin paginación**: Endpoints retornan todos los registros

### 🚀 Próximos Pasos Recomendados

**Corto plazo:**
1. Implementar navegación completa en mobile apps
2. Integrar ratings interactivos en Frontend/Mobile
3. Agregar autenticación básica (JWT)

**Mediano plazo:**
4. Caché local (Room/Core Data)
5. Paginación en endpoints + infinite scroll
6. Tests E2E (Playwright/Detox)
7. CI/CD con GitHub Actions

**Largo plazo:**
8. PWA (Progressive Web App)
9. Notificaciones push
10. Análisis de datos (progreso de cursos)

---

## Recursos y Documentación

- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend Redoc**: http://localhost:8000/redoc
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Jetpack Compose**: https://developer.android.com/jetpack/compose
- **SwiftUI**: https://developer.apple.com/xcode/swiftui/

---

## Troubleshooting

### Backend no inicia
```bash
# Ver logs
make logs

# Limpiar y reiniciar
make clean
make start
```

### Errores de migración
```bash
# Ver estado actual
make db-shell
# En psql: \dt para ver tablas

# Resetear DB (⚠️ CUIDADO: borra datos)
make seed-fresh
```

### Frontend no conecta con Backend
- Verificar que Backend esté en puerto 8000: `make logs-api`
- Verificar `NEXT_PUBLIC_API_URL` en `.env.local`

### Mobile no conecta con Backend
- **Android Emulator**: Usar `http://10.0.2.2:8000`
- **Android Physical**: Cambiar a IP local en `NetworkModule.kt`
- **iOS Simulator**: Usar `http://localhost:8000`
- **iOS Physical**: Cambiar a IP local en `CourseAPIEndpoints.swift`
- Verificar que el dispositivo esté en la misma red

---

**Última actualización**: 2026-02-11
**Versión del documento**: 2.0

Esta memoria contiene toda la información necesaria para continuar el desarrollo del proyecto Platziflix. Consúltala antes de hacer cambios significativos en cualquier capa del sistema.
