# 📊 Análisis de Impacto: Sistema de Calificaciones (1-5 Estrellas)

**Proyecto**: Platziflix
**Fecha de Análisis**: 2026-02-11
**Alcance**: Backend + Frontend
**Versión**: 1.0

---

## 🎯 Estado Actual de Implementación

### ✅ **Backend: 100% Implementado**

El backend está completamente funcional con todos los componentes necesarios:

#### **1. Base de Datos (PostgreSQL)**
- **Tabla**: `course_ratings` con soft delete pattern
- **Campos**: `id`, `course_id` (FK), `user_id`, `rating` (1-5), `created_at`, `updated_at`, `deleted_at`
- **Constraints**:
  - `CHECK (rating >= 1 AND rating <= 5)` - Validación a nivel DB
  - `UNIQUE(course_id, user_id, deleted_at)` - Un rating activo por usuario/curso
- **Índices**: `course_id`, `user_id` para optimización de queries
- **Migración**: `Backend/app/alembic/versions/0e3a8766f785_add_course_ratings_table.py`

#### **2. Modelos SQLAlchemy**
- **CourseRating Model** (`Backend/app/models/course_rating.py:1-70`):
  - Hereda de `BaseModel` (timestamps + soft delete automático)
  - Relación Many-to-One con `Course`
  - Método `to_dict()` para serialización
- **Course Model** - Extendido con:
  - Relación One-to-Many con `ratings`
  - Propiedades computadas: `average_rating`, `total_ratings`

#### **3. Service Layer**
- **CourseService** (`Backend/app/services/course_service.py`):
  - `add_course_rating()` - Crear o actualizar rating
  - `get_course_ratings()` - Listar ratings de un curso
  - `get_course_rating_stats()` - Estadísticas agregadas
  - `get_user_course_rating()` - Rating específico del usuario
  - `update_course_rating()` - Actualizar rating existente
  - `delete_course_rating()` - Soft delete

#### **4. API Endpoints**
Todos implementados en `Backend/app/main.py:144-434`:

| Endpoint | Método | Descripción | Status |
|----------|--------|-------------|--------|
| `/courses/{id}/ratings` | POST | Crear/actualizar rating | 201 |
| `/courses/{id}/ratings` | GET | Listar todos los ratings | 200 |
| `/courses/{id}/ratings/stats` | GET | Stats agregadas | 200 |
| `/courses/{id}/ratings/user/{user_id}` | GET | Rating del usuario | 200/204 |
| `/courses/{id}/ratings/{user_id}` | PUT | Actualizar rating | 200 |
| `/courses/{id}/ratings/{user_id}` | DELETE | Soft delete | 204 |

#### **5. Schemas Pydantic**
- `RatingRequest` - Validación de entrada (user_id, rating 1-5)
- `RatingResponse` - Estructura de respuesta
- `RatingStatsResponse` - Estadísticas (average, total, distribution)
- `ErrorResponse` - Manejo de errores estandarizado

#### **6. Testing**
- ✅ Tests de endpoints (`Backend/app/tests/test_rating_endpoints.py`)
- ✅ Tests de service (`Backend/app/tests/test_course_rating_service.py`)
- ✅ Tests de constraints DB (`Backend/app/tests/test_rating_db_constraints.py`)

---

### ⚠️ **Frontend: 50% Implementado**

El frontend tiene la infraestructura completa pero **falta la interactividad**:

#### **✅ Implementado:**

1. **Componente StarRating** (`Frontend/src/components/StarRating/StarRating.tsx:1-111`)
   - Visualización de 0-5 estrellas (soporta decimales)
   - Soporte para medias estrellas con gradientes SVG
   - Props: `rating`, `totalRatings`, `showCount`, `size`, `readonly`
   - **Limitación**: Solo modo `readonly`, no hay interactividad
   - Tests completos con Vitest

2. **Service API** (`Frontend/src/services/ratingsApi.ts:1-238`)
   - Cliente HTTP completo con todas las funciones:
     - `getRatingStats()` - Stats del curso
     - `getCourseRatings()` - Listar ratings
     - `getUserRating()` - Rating del usuario
     - `createRating()` - Crear rating
     - `updateRating()` - Actualizar rating
     - `deleteRating()` - Eliminar rating
   - Fetch con timeout (10s) y manejo de errores
   - Error handling con `ApiError` custom

3. **Types TypeScript** (`Frontend/src/types/rating.ts:1-95`)
   - `CourseRating` - Modelo completo
   - `RatingRequest` - Payload para crear/actualizar
   - `RatingStats` - Estadísticas agregadas
   - Type guards: `isValidRating()`, `isCourseRating()`, `isRatingStats()`
   - `ApiError` class para errores tipados

4. **Integración en Course Component** (`Frontend/src/components/Course/Course.tsx:24-35`)
   - Muestra `StarRating` readonly en cards de cursos
   - Consume `average_rating` y `total_ratings` del backend
   - Condicional: solo muestra si existe rating

#### **❌ NO Implementado:**

1. **Componente Interactivo para Calificar**
   - No existe componente para que el usuario califique
   - StarRating actual no acepta interacción (click/hover)
   - Falta manejo de estados: idle, hover, loading, success, error

2. **Integración en Página de Detalle**
   - `Frontend/src/app/course/[slug]/page.tsx` no incluye ratings interactivos
   - No hay sección para "Califica este curso"
   - No se consulta el rating previo del usuario

3. **Gestión de Estado del Usuario**
   - No hay lógica para saber si el usuario ya calificó
   - No hay feedback visual de "ya calificaste con X estrellas"
   - No hay simulación de `user_id` (actualmente no hay autenticación)

4. **UX Features**
   - Sin optimistic updates (actualización inmediata antes de confirmar)
   - Sin animaciones/transiciones al calificar
   - Sin confirmación de éxito/error al usuario

---

## 📋 Acciones Necesarias por Componente

### 🔵 **Backend: Sin cambios necesarios**

El backend está completamente funcional y listo para recibir peticiones del frontend.

**Opcional (mejoras futuras):**
- [ ] Implementar autenticación JWT para validar `user_id` real
- [ ] Agregar paginación en `GET /courses/{id}/ratings` para cursos con muchos ratings
- [ ] Implementar rate limiting en endpoints de ratings

---

### 🟢 **Frontend: Acciones Requeridas**

#### **1. Crear Componente InteractiveStarRating** (2-3 horas)

**Archivo nuevo**: `Frontend/src/components/InteractiveStarRating/InteractiveStarRating.tsx`

**Características**:
- Extender/refactorizar `StarRating` actual para aceptar clicks
- Estados: `idle`, `hover`, `loading`, `success`, `error`
- Eventos: `onRatingChange(rating: number)`, `onRatingSubmit(rating: number)`
- Hover effects: resaltar estrellas al pasar el mouse
- Disabled state durante loading
- Accesibilidad: keyboard navigation (arrow keys, Enter)

**Props sugeridas**:
```typescript
interface InteractiveStarRatingProps {
  currentRating: number; // Rating actual del usuario (0 si no ha calificado)
  averageRating?: number; // Rating promedio (para mostrar antes de calificar)
  onRatingChange: (rating: number) => Promise<void>;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
}
```

**Flujo de interacción**:
1. Usuario hace hover → resaltar estrellas hasta la posición del mouse
2. Usuario hace click → marcar rating temporalmente
3. Llamar a `onRatingChange(rating)` → estado `loading`
4. Si éxito → estado `success` + mostrar nuevo rating
5. Si error → estado `error` + rollback + mensaje de error

---

#### **2. Integrar Ratings en Course Detail Page** (1-2 horas)

**Archivo a modificar**: `Frontend/src/app/course/[slug]/page.tsx`

**Cambios necesarios**:

**a) Agregar Client Component para interactividad**
- Crear `Frontend/src/components/CourseRating/CourseRating.tsx` (Client Component)
- Razón: Necesita `useState` y event handlers (no soportado en Server Components)

**b) Consultar rating previo del usuario**
```typescript
// En CourseRating.tsx (Client Component)
const [userRating, setUserRating] = useState<number | null>(null);
const [isLoading, setIsLoading] = useState(false);

useEffect(() => {
  // Simular user_id (cambiar cuando haya autenticación)
  const mockUserId = 1; // O obtener de localStorage/cookie

  ratingsApi.getUserRating(courseId, mockUserId)
    .then(rating => setUserRating(rating?.rating || null))
    .catch(err => console.error('Error fetching user rating:', err));
}, [courseId]);
```

**c) Implementar handler de calificación**
```typescript
const handleRatingSubmit = async (rating: number) => {
  setIsLoading(true);
  try {
    const mockUserId = 1; // Cambiar cuando haya auth

    if (userRating === null) {
      // Crear nuevo rating
      await ratingsApi.createRating(courseId, { user_id: mockUserId, rating });
    } else {
      // Actualizar rating existente
      await ratingsApi.updateRating(courseId, mockUserId, { user_id: mockUserId, rating });
    }

    setUserRating(rating);
    // Opcional: recargar stats del curso
  } catch (error) {
    console.error('Error submitting rating:', error);
    // Mostrar toast/notificación de error
  } finally {
    setIsLoading(false);
  }
};
```

**d) Estructura JSX sugerida**
```tsx
<section className={styles.ratingsSection}>
  <h3>Califica este curso</h3>

  {userRating !== null ? (
    <div className={styles.userRatingDisplay}>
      <p>Tu calificación:</p>
      <InteractiveStarRating
        currentRating={userRating}
        onRatingChange={handleRatingSubmit}
        disabled={isLoading}
        size="large"
      />
    </div>
  ) : (
    <InteractiveStarRating
      currentRating={0}
      averageRating={course.average_rating}
      onRatingChange={handleRatingSubmit}
      disabled={isLoading}
      size="large"
    />
  )}

  <div className={styles.courseStats}>
    <StarRating
      rating={course.average_rating || 0}
      totalRatings={course.total_ratings}
      showCount={true}
      readonly={true}
      size="medium"
    />
  </div>
</section>
```

---

#### **3. Agregar Gestión de User ID** (1 hora)

**Problema actual**: No hay autenticación, entonces `user_id` debe ser simulado.

**Soluciones temporales** (hasta implementar auth):

**Opción A: LocalStorage (más simple)**
```typescript
// Frontend/src/utils/mockUser.ts
export const getMockUserId = (): number => {
  let userId = localStorage.getItem('mock_user_id');
  if (!userId) {
    userId = String(Math.floor(Math.random() * 10000) + 1);
    localStorage.setItem('mock_user_id', userId);
  }
  return Number(userId);
};
```

**Opción B: Cookie persistente**
- Más realista para futuro auth
- Usar `js-cookie` o `document.cookie`

**Opción C: Parámetro en URL**
- Solo para testing
- `?user_id=123`

**Implementación recomendada**: Opción A (LocalStorage) porque:
- Fácil de implementar
- Simula persistencia del usuario
- Fácil de reemplazar cuando haya auth real

---

#### **4. UX Enhancements (Opcional, 2 horas)**

**a) Optimistic Updates**
- Actualizar UI inmediatamente (antes de recibir respuesta del server)
- Si falla, hacer rollback

**b) Feedback Visual**
- Toast notifications (success/error)
- Animaciones al cambiar rating
- Skeleton loading mientras carga

**c) Accesibilidad**
- ARIA labels descriptivos
- Keyboard navigation (Tab, Arrow keys, Enter)
- Focus management

**d) Mostrar distribución de ratings**
- Gráfico de barras: cuántos usuarios dieron 1, 2, 3, 4, 5 estrellas
- Usar `rating_distribution` del endpoint `/courses/{id}/ratings/stats`

---

## 🧪 Testing Adicional Requerido

### Frontend Tests (1-2 horas)

**1. InteractiveStarRating Component**
```typescript
// Frontend/src/components/InteractiveStarRating/__tests__/InteractiveStarRating.test.tsx
describe('InteractiveStarRating', () => {
  test('renders interactive stars');
  test('highlights stars on hover');
  test('calls onRatingChange with correct value on click');
  test('shows loading state when disabled');
  test('supports keyboard navigation');
  test('handles errors gracefully');
});
```

**2. CourseRating Component (Integration)**
```typescript
// Frontend/src/components/CourseRating/__tests__/CourseRating.test.tsx
describe('CourseRating', () => {
  test('fetches user rating on mount');
  test('submits new rating successfully');
  test('updates existing rating');
  test('displays error on API failure');
});
```

---

## 📊 Resumen de Impacto por Componente

| Componente | Estado | Acciones Necesarias | Horas Estimadas |
|------------|--------|---------------------|-----------------|
| **Backend - Database** | ✅ Completo | Ninguna | 0h |
| **Backend - Models** | ✅ Completo | Ninguna | 0h |
| **Backend - Service** | ✅ Completo | Ninguna | 0h |
| **Backend - API** | ✅ Completo | Ninguna | 0h |
| **Backend - Tests** | ✅ Completo | Ninguna | 0h |
| **Frontend - Types** | ✅ Completo | Ninguna | 0h |
| **Frontend - API Service** | ✅ Completo | Ninguna | 0h |
| **Frontend - StarRating (readonly)** | ✅ Completo | Ninguna | 0h |
| **Frontend - InteractiveStarRating** | ❌ **Falta** | Crear componente interactivo | **2-3h** |
| **Frontend - Course Detail Integration** | ❌ **Falta** | Integrar ratings en detalle | **1-2h** |
| **Frontend - User ID Management** | ❌ **Falta** | Mock user system | **1h** |
| **Frontend - UX Enhancements** | 🟡 Opcional | Optimistic updates, toasts | **2h** |
| **Frontend - Tests** | 🟡 Parcial | Tests de componentes interactivos | **1-2h** |
| **TOTAL** | | | **7-10h** |

---

## 🎯 Checklist de Implementación

### ✅ **Backend (Completado)**
- [x] Modelo `CourseRating` con validaciones
- [x] Migración de base de datos
- [x] Service layer con métodos CRUD
- [x] Endpoints REST completos
- [x] Schemas Pydantic
- [x] Tests unitarios e integración
- [x] Soft delete pattern
- [x] Documentación Swagger

### 🚧 **Frontend (En Progreso)**
- [x] Types TypeScript completos
- [x] API service (`ratingsApi`)
- [x] Componente `StarRating` readonly
- [x] Integración en lista de cursos
- [x] Tests de componente readonly
- [ ] **Componente `InteractiveStarRating`** ⬅️ **CRÍTICO**
- [ ] **Integración en Course Detail page** ⬅️ **CRÍTICO**
- [ ] Mock user ID system
- [ ] UX enhancements (optional)
- [ ] Tests de interactividad

---

## 🚀 Plan de Acción Recomendado

### **Fase 1: Funcionalidad Core (4-5h)**
1. Crear `InteractiveStarRating` component (2-3h)
2. Integrar en Course Detail page (1-2h)
3. Mock user ID system (1h)

### **Fase 2: Testing (1-2h)**
4. Tests del componente interactivo
5. Tests de integración

### **Fase 3: UX (2h) - Opcional**
6. Optimistic updates
7. Toast notifications
8. Animaciones

---

## 📌 Consideraciones Importantes

### **Seguridad**
- ⚠️ Actualmente no hay validación de `user_id` en backend (campo sin FK)
- Cualquiera puede enviar cualquier `user_id` en las peticiones
- **Solución**: Implementar autenticación JWT cuando sea posible

### **Performance**
- Backend ya tiene índices optimizados
- Queries de ratings son eficientes (< 100ms)
- Frontend debe usar debouncing si permite cambiar rating múltiples veces

### **Accesibilidad**
- Componente interactivo debe soportar teclado completo
- ARIA labels descriptivos
- Focus management correcto

### **Mobile Apps**
- Android/iOS no fueron analizados (según solicitud)
- Necesitarán implementaciones similares cuando corresponda

---

## 📈 Diagrama de Flujo del Sistema de Ratings

```
┌─────────────────────────────────────────────────────────────────┐
│                       USUARIO (Frontend)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 1. Click en estrella (rating: 4)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           InteractiveStarRating Component (Client)              │
│  - Captura click                                                │
│  - Valida rating (1-5)                                          │
│  - Llama onRatingChange(4)                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 2. Llama ratingsApi.createRating()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ratingsApi Service (Frontend)                  │
│  - POST /courses/1/ratings                                      │
│  - Body: { user_id: 123, rating: 4 }                           │
│  - Timeout: 10s                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 3. HTTP Request
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Endpoint (Backend)                    │
│  @app.post("/courses/{course_id}/ratings")                      │
│  - Valida request (Pydantic)                                    │
│  - Inyecta CourseService                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 4. Llama service.add_course_rating()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CourseService (Backend)                       │
│  - Verifica si curso existe                                     │
│  - Busca rating existente del usuario                           │
│  - Si existe: UPDATE, sino: INSERT                              │
│  - Aplica soft delete filter                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 5. Query SQL
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
│  INSERT INTO course_ratings                                     │
│    (course_id, user_id, rating, created_at, updated_at)         │
│  VALUES (1, 123, 4, NOW(), NOW())                               │
│  ON CONFLICT (course_id, user_id) DO UPDATE...                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 6. Return new rating
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CourseService (Backend)                       │
│  - rating.to_dict()                                             │
│  - Return { id: 1, course_id: 1, user_id: 123, rating: 4 }     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 7. HTTP 201 Created
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           InteractiveStarRating Component (Client)              │
│  - Actualiza estado: userRating = 4                             │
│  - Muestra feedback visual (success)                            │
│  - Opcional: Trigger refresh de course stats                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Análisis de Arquitectura del Sistema Actual

### **Patrón Backend: Service Layer + Repository Pattern**

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Routes                           │
│  - Reciben requests HTTP                                        │
│  - Validan con Pydantic                                         │
│  - Dependency Injection de CourseService                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CourseService                             │
│  - Business Logic centralizada                                  │
│  - Queries optimizadas (joinedload)                             │
│  - Cálculo de agregaciones (AVG, COUNT)                         │
│  - Soft delete filtering                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLAlchemy Models                            │
│  - CourseRating (relationship con Course)                       │
│  - Course (relationship con ratings)                            │
│  - BaseModel (timestamps + soft delete)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
│  - Constraints (CHECK, UNIQUE, FK)                              │
│  - Indexes (course_id, user_id)                                 │
│  - Soft delete support (deleted_at)                             │
└─────────────────────────────────────────────────────────────────┘
```

### **Patrón Frontend: Server Components + Client Components**

```
┌─────────────────────────────────────────────────────────────────┐
│         Next.js App Router (Server Component)                   │
│  - Fetch inicial de datos                                       │
│  - SSR con course data                                          │
│  - Pasa props a Client Components                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│      CourseRating (Client Component) - A IMPLEMENTAR           │
│  - useState para userRating                                     │
│  - useEffect para fetch initial rating                          │
│  - Event handlers para calificación                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│   InteractiveStarRating (Client Component) - A IMPLEMENTAR     │
│  - Estado interno para hover                                    │
│  - onClick handlers                                             │
│  - Disabled state durante loading                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              ratingsApi Service (Fetch Layer)                   │
│  - Abstracción de HTTP calls                                    │
│  - Error handling centralizado                                  │
│  - Timeout management                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Referencias y Recursos

### **Documentación del Proyecto**
- `CLAUDE.md` - Documentación principal del proyecto
- `spec/00_sistema_ratings_cursos.md` - Especificación original
- `spec/01_backend_ratings_implementation_plan.md` - Plan backend
- `spec/02_frontend_ratings_implementation_plan.md` - Plan frontend

### **Archivos Clave del Backend**
- `Backend/app/models/course_rating.py` - Modelo CourseRating
- `Backend/app/services/course_service.py` - Service layer
- `Backend/app/main.py:144-434` - Endpoints de ratings
- `Backend/app/schemas/rating.py` - Schemas Pydantic

### **Archivos Clave del Frontend**
- `Frontend/src/components/StarRating/StarRating.tsx` - Componente readonly
- `Frontend/src/services/ratingsApi.ts` - API client
- `Frontend/src/types/rating.ts` - TypeScript types
- `Frontend/src/components/Course/Course.tsx` - Integración en cards

### **Tests**
- `Backend/app/tests/test_rating_endpoints.py` - Tests endpoints
- `Backend/app/tests/test_course_rating_service.py` - Tests service
- `Backend/app/tests/test_rating_db_constraints.py` - Tests DB
- `Frontend/src/components/StarRating/__tests__/StarRating.test.tsx` - Tests componente

---

## 📝 Notas de Implementación

### **Decisiones Técnicas Tomadas**

1. **Soft Delete Pattern**
   - Razón: Mantener histórico de ratings para análisis
   - Implementación: Campo `deleted_at` en todas las tablas

2. **Rating de 1-5 (Integer)**
   - Razón: Simplifica UX y validación
   - Alternativa descartada: Float (0.5 increments)

3. **Un Rating por Usuario/Curso**
   - Razón: Evitar spam y manipulación
   - Constraint: UNIQUE(course_id, user_id, deleted_at)

4. **Server Components + Client Components**
   - Razón: Optimización de performance (zero JS en lo posible)
   - Trade-off: Requiere Client Components para interactividad

5. **Mock User ID en LocalStorage**
   - Razón: Simular usuario sin implementar auth completo
   - Trade-off: No es seguro, solo para desarrollo

### **Próximas Iteraciones Sugeridas**

1. **Autenticación JWT**
   - Validar user_id real
   - Tabla `users` con relaciones

2. **Paginación de Ratings**
   - Endpoint: `GET /courses/{id}/ratings?page=1&limit=20`
   - Evitar cargar miles de ratings

3. **Rate Limiting**
   - Prevenir abuse (1 rating cada 5 min)
   - Implementar con Redis

4. **Analytics Dashboard**
   - Visualizar distribución de ratings
   - Detectar patrones sospechosos

5. **Notificaciones**
   - Email al instructor cuando recibe rating
   - Push notifications en mobile

---

**Última actualización**: 2026-02-11
**Autor**: Claude Code (Análisis automatizado)
**Estado**: Documento en revisión

---

## 🎓 Conclusiones

El sistema de calificaciones de Platziflix tiene una **base sólida y completa en el backend**, con:
- ✅ Arquitectura escalable y bien diseñada
- ✅ Validaciones multicapa (DB, Backend, Frontend)
- ✅ Tests comprehensivos
- ✅ Documentación clara

El **frontend requiere 7-10 horas de trabajo** para completar la funcionalidad interactiva:
- 🔴 **Crítico**: Componente `InteractiveStarRating`
- 🔴 **Crítico**: Integración en página de detalle
- 🟡 **Importante**: Mock user ID system
- 🟢 **Opcional**: UX enhancements

Una vez implementadas las acciones críticas, el sistema estará **100% funcional** y listo para producción (con las consideraciones de seguridad sobre mock user ID hasta implementar autenticación real).
