# Plan de Implementacion: Sistema de Ratings Interactivo - Frontend

## Fecha: 2026-02-11
## Version: 1.0
## Estado: Pendiente de implementacion

---

## 1. Resumen Ejecutivo

### Problema
La pagina de detalle de curso (`/course/[slug]`) no permite a los usuarios calificar cursos de forma interactiva. Actualmente solo existe un componente `StarRating` en modo readonly que muestra promedios. El backend esta 100% implementado con todos los endpoints de ratings funcionales.

### Objetivo
Implementar un sistema de calificacion interactivo (1-5 estrellas) en la pagina de detalle del curso, donde los usuarios puedan:
- Ver el promedio y distribucion de calificaciones
- Enviar su propia calificacion haciendo click en estrellas
- Actualizar o eliminar su calificacion existente
- Ver feedback visual inmediato (optimistic updates)

### Alcance
- Incluido: Componentes interactivos, integracion con API, tests, gestion de mock user
- Excluido: Autenticacion real (se usara mock user_id), registro de usuarios, persistencia de sesion

---

## 2. Analisis del Estado Actual

### 2.1 Discrepancias Detectadas entre Backend y Frontend

**Discrepancia de tipos en CourseDetail**: El tipo `CourseDetail` en `Frontend/src/types/index.ts` no incluye los campos de ratings (`average_rating`, `total_ratings`, `rating_distribution`) que el backend ya retorna en `GET /courses/{slug}`. El tipo tampoco tiene los campos `teacher_id` que el backend retorna.

**Discrepancia en la interfaz CourseDetailComponent**: El componente `CourseDetail.tsx` usa `course.title` y `course.teacher`, pero el backend retorna `course.name` y `course.teacher_id` (un array de IDs). El tipo `CourseDetail` hereda de `Course` que tiene `name`, no `title`. Esto indica que o bien hay un mapping intermedio, o el componente tiene un bug latente.

**RatingStats incompleto**: El tipo `RatingStats` en `Frontend/src/types/rating.ts` no incluye `rating_distribution` que el backend retorna en `/courses/{course_id}/ratings/stats`.

**getUserRating usa endpoint diferente**: El `ratingsApi.getUserRating` hace GET a `/courses/{courseId}/ratings/${userId}`, pero el backend define el endpoint como `/courses/{course_id}/ratings/user/{user_id}`. Hay una discrepancia en la ruta.

### 2.2 Inventario de Archivos Existentes Relevantes

| Archivo | Estado | Notas |
|---------|--------|-------|
| `Frontend/src/components/StarRating/StarRating.tsx` | Readonly solamente | Necesita version interactiva separada |
| `Frontend/src/components/StarRating/StarRating.module.scss` | Funcional | Necesita estilos para hover/click/interactive |
| `Frontend/src/services/ratingsApi.ts` | Completo | Bug en getUserRating (ruta incorrecta) |
| `Frontend/src/types/rating.ts` | Parcial | Falta rating_distribution en RatingStats |
| `Frontend/src/types/index.ts` | Parcial | Falta campos de rating en CourseDetail |
| `Frontend/src/components/CourseDetail/CourseDetail.tsx` | Server Component | Necesita integracion de ratings |
| `Frontend/src/app/course/[slug]/page.tsx` | Server Component | Necesita pasar datos de rating |
| `Frontend/src/styles/vars.scss` | Completo | Paleta de colores definida |

### 2.3 Patrones del Proyecto Identificados

1. Server Components por defecto: Las paginas (`page.tsx`) son `async` Server Components que hacen fetch directo
2. Client Components con "use client": Solo cuando hay interactividad (ej: `error.tsx`)
3. CSS Modules + SCSS: Todos los componentes usan `ComponentName.module.scss` con import de `vars.scss`
4. Componentes funcionales con FC o arrow functions: Sin uso de class components
5. Importaciones con alias `@/`: Configurado en tsconfig.json
6. Testing con Vitest + RTL: Setup en `src/test/setup.ts` con jsdom
7. Estructura de carpetas: `components/NombreComponente/NombreComponente.tsx` + `.module.scss` + `__tests__/`
8. Color tokens via SCSS function: `color('primary')`, `color('text-primary')`, etc.
9. Design tokens constantes: border-radius 18px para cards, 12px para botones, box-shadow `0 6px 24px rgba(0,0,0,0.10)`, font-weight 800 para titulos
10. No hay state management global: Ni Context API ni Zustand, cada componente maneja su propio estado

---

## 3. Arquitectura de la Solucion

### 3.1 Diagrama de Componentes

```
page.tsx (Server Component)
  |-- fetch /courses/{slug} --> datos del curso + rating stats
  |-- CourseDetailComponent course={data}  (Server Component)
        |-- StarRating readonly  (Server Component - promedio existente)
        |-- CourseRatingSection  (Client Component - NUEVO)
              |-- InteractiveStarRating  (Client Component - NUEVO)
              |-- RatingDistribution  (Client Component - NUEVO)
              |-- Feedback message  (interno)
```

### 3.2 Principio de Diseno: Boundary Server/Client

La estrategia es mantener la mayor cantidad posible de logica en Server Components y crear un "boundary" claro donde se necesita interactividad:

- Server Side: Fetch de datos del curso, rendering del detalle, promedio readonly
- Client Side: Solo la seccion de "Califica este curso" (hover, click, submit, estados de carga)

Esto minimiza el JavaScript enviado al cliente y mantiene la consistencia con el patron existente del proyecto.

### 3.3 Flujo de Datos

```
1. CARGA INICIAL (Server Side):
   page.tsx --> fetch /courses/{slug} --> courseData (incluye average_rating, total_ratings, rating_distribution)
   page.tsx --> render CourseDetailComponent course={courseData}
   CourseDetailComponent --> render CourseRatingSection courseId={id} initialStats={stats}

2. CARGA DEL RATING DEL USUARIO (Client Side):
   CourseRatingSection monta --> useEffect --> ratingsApi.getUserRating(courseId, MOCK_USER_ID)
   Si tiene rating --> mostrar "Tu calificacion: X estrellas" con opcion de editar/eliminar
   Si no tiene --> mostrar "Califica este curso" con estrellas interactivas

3. ENVIO DE RATING (Client Side):
   Usuario click en estrella --> optimistic update UI
   ratingsApi.createRating(courseId, { user_id, rating })
   Si exito --> confirmar UI + actualizar stats via ratingsApi.getRatingStats(courseId)
   Si error --> revert UI + mostrar error message

4. ACTUALIZACION (Client Side):
   Usuario cambia rating --> optimistic update
   ratingsApi.createRating(courseId, { user_id, rating })  (POST maneja create/update)
   Actualizar stats

5. ELIMINACION (Client Side):
   Usuario click "Eliminar" --> confirmar
   ratingsApi.deleteRating(courseId, userId)
   Reset UI a estado sin rating + actualizar stats
```

---

## 4. Plan de Implementacion Detallado

### Fase 0: Correcciones y Preparacion de Tipos (Pre-requisito)

#### Paso 0.1: Corregir tipos en `Frontend/src/types/rating.ts`

**Archivo**: `/home/damian/projects/claude-code/Frontend/src/types/rating.ts`

**Cambio**: Agregar `rating_distribution` a `RatingStats` para que coincida con lo que retorna el backend.

```typescript
// ANTES:
export interface RatingStats {
  average_rating: number;
  total_ratings: number;
}

// DESPUES:
export interface RatingStats {
  average_rating: number;
  total_ratings: number;
  rating_distribution?: Record<string, number>;
}
```

Justificacion: El endpoint `GET /courses/{id}/ratings/stats` retorna `rating_distribution` como parte de `RatingStatsResponse`. Se hace opcional porque `getRatingStats` en `ratingsApi.ts` retorna un fallback sin distribucion cuando hay 404. Ademas, los datos que llegan desde `/courses/{slug}` en la carga inicial del Server Component ya incluyen `rating_distribution`.

#### Paso 0.2: Actualizar tipos en `Frontend/src/types/index.ts`

**Archivo**: `/home/damian/projects/claude-code/Frontend/src/types/index.ts`

**Cambio**: Extender `CourseDetail` con los campos de rating que el backend ya retorna.

```typescript
// ANTES:
export interface CourseDetail extends Course {
  description: string;
  classes: Class[];
}

// DESPUES:
export interface CourseDetail extends Course {
  description: string;
  classes: Class[];
  teacher_id?: number[];
  rating_distribution?: Record<string, number>;
}
```

Nota: `average_rating` y `total_ratings` ya estan en `Course` como opcionales, asi que `CourseDetail` los hereda. Solo falta `rating_distribution` y `teacher_id`.

#### Paso 0.3: Corregir ruta en `Frontend/src/services/ratingsApi.ts`

**Archivo**: `/home/damian/projects/claude-code/Frontend/src/services/ratingsApi.ts`

**Cambio**: Corregir la URL de `getUserRating` para que coincida con el endpoint real del backend.

```typescript
// ANTES (linea 143):
const url = `${API_BASE_URL}/courses/${courseId}/ratings/${userId}`;

// DESPUES:
const url = `${API_BASE_URL}/courses/${courseId}/ratings/user/${userId}`;
```

Justificacion: El endpoint del backend es `GET /courses/{course_id}/ratings/user/{user_id}` (definido en `main.py:294`), no `GET /courses/{course_id}/ratings/{user_id}`.

---

### Fase 1: Componente InteractiveStarRating

#### Paso 1.1: Crear componente `InteractiveStarRating`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/InteractiveStarRating/InteractiveStarRating.tsx`

Este es un componente Client Component (`"use client"`) independiente del `StarRating` readonly existente. La decision de NO modificar el `StarRating` existente es intencional: el componente readonly es un Server Component puro, simple y bien testeado. Agregar interactividad requiere `"use client"`, lo que cambiaria su naturaleza y afectaria todos los lugares donde se usa en modo readonly (como las cards de cursos en la homepage).

**Props**:

```typescript
interface InteractiveStarRatingProps {
  currentRating: number;            // 0 = sin rating, 1-5 = rating actual
  onRate: (rating: number) => void; // Callback cuando usuario selecciona rating
  disabled?: boolean;                // Deshabilitar durante submit
  size?: 'medium' | 'large';        // Tamano visual
}
```

**Comportamiento**:
- Renderiza 5 estrellas SVG (reutilizando el mismo path SVG del StarRating existente)
- Hover: Al pasar el mouse sobre una estrella, todas las estrellas hasta esa posicion se iluminan (preview)
- Click: Llama `onRate(starNumber)` con el valor 1-5
- Estado seleccionado: Si `currentRating > 0`, las estrellas hasta ese valor estan llenas
- Focus/Keyboard: Las estrellas son `<button>` elements con soporte de Tab + Enter/Space
- Disabled: En estado disabled, no responde a hover ni click (se muestra opaco)
- El hover state sobrescribe visualmente el currentRating para dar preview

**Accesibilidad**:
- Cada estrella es un `<button>` con `aria-label="Calificar {n} de 5 estrellas"`
- El contenedor tiene `role="radiogroup"` con `aria-label="Califica este curso"`
- La estrella seleccionada tiene `aria-checked="true"`
- Soporte completo de teclado (Tab para navegar, Enter/Space para seleccionar)
- Focus visible con outline

#### Paso 1.2: Crear estilos `InteractiveStarRating.module.scss`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/InteractiveStarRating/InteractiveStarRating.module.scss`

Estilos clave:

```scss
@import '../../styles/vars.scss';

.container {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.starButton {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  display: inline-flex;
  color: #4a4a4a;
  transition: transform 0.15s ease, color 0.15s ease;

  &:hover {
    transform: scale(1.15);
  }

  &:focus-visible {
    outline: 2px solid color('primary');
    outline-offset: 2px;
    border-radius: 4px;
  }

  &.filled {
    color: #ffc107;
  }

  &.hovered {
    color: #ffdb4d;
  }

  &.disabled {
    cursor: not-allowed;
    opacity: 0.5;
    &:hover {
      transform: none;
    }
  }
}

.medium svg {
  width: 24px;
  height: 24px;
}

.large svg {
  width: 32px;
  height: 32px;
}
```

---

### Fase 2: Componente RatingDistribution

#### Paso 2.1: Crear componente `RatingDistribution`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/RatingDistribution/RatingDistribution.tsx`

Este es un componente visual que muestra la distribucion de ratings como barras horizontales (similar a Amazon/Google Play). Se implementa como Client Component ya que se incluira dentro de CourseRatingSection.

**Props**:

```typescript
interface RatingDistributionProps {
  distribution: Record<string, number>;
  totalRatings: number;
}
```

**Renderizado**:
- 5 filas (de 5 estrellas a 1 estrella, descendente)
- Cada fila: label "5" con icono estrella | barra de progreso | numero/porcentaje
- Barra proporcional al porcentaje del total
- Colores coherentes con la paleta existente (primary para barras llenas, light-gray para fondo)

#### Paso 2.2: Crear estilos `RatingDistribution.module.scss`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/RatingDistribution/RatingDistribution.module.scss`

---

### Fase 3: Componente CourseRatingSection (Orquestador)

#### Paso 3.1: Crear componente `CourseRatingSection`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/CourseRatingSection/CourseRatingSection.tsx`

Este es el componente Client Component principal que orquesta toda la logica de ratings. Es `"use client"` porque gestiona estado, efectos secundarios y llamadas a la API.

**Props**:

```typescript
interface CourseRatingSectionProps {
  courseId: number;
  initialStats: {
    averageRating: number;
    totalRatings: number;
    ratingDistribution: Record<string, number>;
  };
}
```

**Estado interno**:

```typescript
const MOCK_USER_ID = getCurrentUserId(); // desde config/user.ts

const [userRating, setUserRating] = useState<number>(0);
const [stats, setStats] = useState(initialStats);
const [submitting, setSubmitting] = useState(false);
const [loadingUserRating, setLoadingUserRating] = useState(true);
const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
const [feedbackType, setFeedbackType] = useState<'success' | 'error'>('success');
```

**Logica principal**:

```
useEffect (mount):
  1. Llamar ratingsApi.getUserRating(courseId, MOCK_USER_ID)
  2. Si retorna rating -> setUserRating(rating.rating)
  3. Si retorna null -> setUserRating(0)
  4. setLoadingUserRating(false)

handleRate(newRating):
  1. Guardar previousRating = userRating
  2. Optimistic update: setUserRating(newRating)
  3. setSubmitting(true)
  4. try:
     a. ratingsApi.createRating(courseId, { user_id: MOCK_USER_ID, rating: newRating })
     b. Refrescar stats: ratingsApi.getRatingStats(courseId)
     c. setStats(newStats)
     d. setFeedbackMessage("Calificacion guardada")
     e. setFeedbackType('success')
  5. catch:
     a. Revert: setUserRating(previousRating)
     b. setFeedbackMessage("Error al guardar calificacion")
     c. setFeedbackType('error')
  6. finally:
     a. setSubmitting(false)
     b. setTimeout -> setFeedbackMessage(null), 3000

handleDelete():
  1. Guardar previousRating = userRating
  2. Optimistic: setUserRating(0)
  3. setSubmitting(true)
  4. try:
     a. ratingsApi.deleteRating(courseId, MOCK_USER_ID)
     b. Refrescar stats
     c. setFeedbackMessage("Calificacion eliminada")
  5. catch:
     a. Revert: setUserRating(previousRating)
     b. setFeedbackMessage("Error al eliminar")
  6. finally: cleanup
```

**Renderizado**:

```
section.ratingSection
  h2: "Calificaciones"

  div.ratingOverview
    -- Lado izquierdo: promedio grande + estrellas readonly --
    div.averageDisplay
      span.averageNumber: stats.averageRating.toFixed(1)
      StarRating rating={stats.averageRating} size="medium" readonly
      span.totalCount: "{stats.totalRatings} calificaciones"

    -- Lado derecho: distribucion --
    RatingDistribution
      distribution={stats.ratingDistribution}
      totalRatings={stats.totalRatings}

  div.userRatingSection
    if loadingUserRating:
      p: "Cargando tu calificacion..."
    else:
      h3: userRating > 0 ? "Tu calificacion" : "Califica este curso"
      InteractiveStarRating
        currentRating={userRating}
        onRate={handleRate}
        disabled={submitting}
        size="large"
      if userRating > 0:
        button.deleteButton onClick={handleDelete} disabled={submitting}:
          "Eliminar calificacion"

  -- Feedback message (success/error) --
  if feedbackMessage:
    div.feedback[feedbackType] role="status" aria-live="polite":
      feedbackMessage
```

#### Paso 3.2: Crear estilos `CourseRatingSection.module.scss`

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/CourseRatingSection/CourseRatingSection.module.scss`

Estilos clave siguiendo patrones existentes del proyecto:

```scss
@import '../../styles/vars.scss';

.ratingSection {
  background: color('white');
  border-radius: 18px;
  padding: 2.5rem;
  box-shadow: 0 6px 24px rgba(0,0,0,0.05);
  border: 2px solid color('light-gray');
  margin-bottom: 2rem;
}

.sectionTitle {
  font-size: 2rem;
  font-weight: 800;
  color: color('text-primary');
  margin-bottom: 2rem;
  text-align: center;
}

.ratingOverview {
  display: flex;
  gap: 3rem;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid color('light-gray');

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1.5rem;
  }
}

.averageDisplay {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 120px;
}

.averageNumber {
  font-size: 3.5rem;
  font-weight: 900;
  color: color('text-primary');
  line-height: 1;
}

.totalCount {
  font-size: 0.9rem;
  color: color('text-secondary');
  font-weight: 500;
}

.userRatingSection {
  text-align: center;
  padding: 1.5rem 0;
}

.userRatingTitle {
  font-size: 1.3rem;
  font-weight: 700;
  color: color('text-primary');
  margin-bottom: 1rem;
}

.deleteButton {
  background: none;
  border: 1px solid color('light-gray');
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: color('text-secondary');
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.2s;

  &:hover {
    border-color: color('primary');
    color: color('primary');
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.feedback {
  text-align: center;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-top: 1rem;
  animation: fadeIn 0.3s ease;

  &.success {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
    border: 1px solid rgba(40, 167, 69, 0.2);
  }

  &.error {
    background: rgba(255, 45, 45, 0.1);
    color: color('primary');
    border: 1px solid color('primary-border');
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

### Fase 4: Integracion en la Pagina de Detalle

#### Paso 4.1: Modificar `CourseDetailComponent`

**Archivo**: `/home/damian/projects/claude-code/Frontend/src/components/CourseDetail/CourseDetail.tsx`

**Cambios**:
1. Importar `CourseRatingSection`
2. Pasar datos de rating iniciales como props
3. Agregar la seccion de ratings entre la info del curso y la lista de clases

```typescript
// Agregar import:
import { CourseRatingSection } from '@/components/CourseRatingSection/CourseRatingSection';

// En el render, agregar despues del div.header y antes de div.classesSection:
{typeof course.average_rating === 'number' && (
  <CourseRatingSection
    courseId={course.id}
    initialStats={{
      averageRating: course.average_rating ?? 0,
      totalRatings: course.total_ratings ?? 0,
      ratingDistribution: course.rating_distribution ?? {},
    }}
  />
)}
```

Nota sobre hidratacion: `CourseDetailComponent` es un Server Component. Al incrustar `CourseRatingSection` (un Client Component) dentro de el, Next.js maneja automaticamente el boundary: renderiza el Server Component en el servidor y envia el Client Component como un "island" de interactividad.

#### Paso 4.2: No se necesitan cambios en `page.tsx`

La pagina `course/[slug]/page.tsx` ya hace fetch de los datos del curso que incluyen `average_rating`, `total_ratings` y `rating_distribution` desde el backend. El tipo `CourseDetail` corregido en Fase 0 asegura type safety.

---

### Fase 5: Constante Mock User

#### Paso 5.1: Crear archivo de configuracion de usuario mock

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/config/user.ts`

```typescript
/**
 * Mock user configuration
 * TODO: Reemplazar con autenticacion real cuando se implemente
 */
export const MOCK_USER_ID = 1;

/**
 * Get current user ID
 * Currently returns mock user. Replace with auth when implemented.
 */
export function getCurrentUserId(): number {
  return MOCK_USER_ID;
}
```

Justificacion: Centralizar el mock user_id en un solo archivo facilita la futura migracion a autenticacion real. Cuando se implemente JWT/auth, solo se cambia este archivo.

---

## 5. Archivos a Crear (Resumen)

| # | Archivo | Tipo | Descripcion |
|---|---------|------|-------------|
| 1 | `src/config/user.ts` | Config | Mock user ID centralizado |
| 2 | `src/components/InteractiveStarRating/InteractiveStarRating.tsx` | Client Component | Estrellas clickeables con hover |
| 3 | `src/components/InteractiveStarRating/InteractiveStarRating.module.scss` | Estilos | Hover, focus, disabled states |
| 4 | `src/components/RatingDistribution/RatingDistribution.tsx` | Component | Barras de distribucion |
| 5 | `src/components/RatingDistribution/RatingDistribution.module.scss` | Estilos | Barras horizontales |
| 6 | `src/components/CourseRatingSection/CourseRatingSection.tsx` | Client Component | Orquestador de ratings |
| 7 | `src/components/CourseRatingSection/CourseRatingSection.module.scss` | Estilos | Layout de seccion |

## 6. Archivos a Modificar (Resumen)

| # | Archivo | Cambio |
|---|---------|--------|
| 1 | `src/types/rating.ts` | Agregar `rating_distribution` a `RatingStats` |
| 2 | `src/types/index.ts` | Agregar `rating_distribution` y `teacher_id` a `CourseDetail` |
| 3 | `src/services/ratingsApi.ts` | Corregir URL de `getUserRating` (agregar `/user/`) |
| 4 | `src/components/CourseDetail/CourseDetail.tsx` | Integrar `CourseRatingSection` |

---

## 7. Plan de Testing

### 7.1 Tests para InteractiveStarRating

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/InteractiveStarRating/__tests__/InteractiveStarRating.test.tsx`

Casos de test:

```
describe('InteractiveStarRating')

  describe('Rendering')
    - renders 5 star buttons
    - renders with no stars filled when currentRating is 0
    - renders correct number of filled stars based on currentRating
    - applies medium size class by default
    - applies large size class when specified

  describe('Interaction')
    - calls onRate with correct value when star is clicked
    - calls onRate(3) when third star is clicked
    - calls onRate(1) when first star is clicked
    - calls onRate(5) when fifth star is clicked
    - does not call onRate when disabled

  describe('Hover behavior')
    - highlights stars on hover (visual preview)
    - removes highlight on mouse leave
    - does not highlight when disabled

  describe('Keyboard accessibility')
    - each star button is focusable via Tab
    - calls onRate on Enter key press
    - calls onRate on Space key press
    - star buttons have correct aria-labels

  describe('Accessibility')
    - container has role="radiogroup"
    - container has descriptive aria-label
    - selected star has aria-checked="true"
    - unselected stars have aria-checked="false"
```

### 7.2 Tests para RatingDistribution

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/RatingDistribution/__tests__/RatingDistribution.test.tsx`

Casos de test:

```
describe('RatingDistribution')

  describe('Rendering')
    - renders 5 rows (one per star level)
    - displays star labels (5, 4, 3, 2, 1) in descending order
    - displays correct count for each level
    - renders progress bars

  describe('Calculations')
    - calculates correct percentage widths for bars
    - handles zero total ratings (all bars at 0%)
    - handles all ratings at one level (one bar at 100%)

  describe('Edge cases')
    - handles empty distribution object
    - handles missing keys in distribution
```

### 7.3 Tests para CourseRatingSection

**Archivo nuevo**: `/home/damian/projects/claude-code/Frontend/src/components/CourseRatingSection/__tests__/CourseRatingSection.test.tsx`

Casos de test:

```
describe('CourseRatingSection')

  describe('Initial load')
    - renders section title
    - displays initial average rating
    - displays initial total ratings count
    - renders RatingDistribution with initial data
    - shows loading state while fetching user rating
    - displays InteractiveStarRating after loading

  describe('User has existing rating')
    - shows "Tu calificacion" when user has rated
    - pre-selects user current rating in InteractiveStarRating
    - shows delete button when user has rating

  describe('User has no rating')
    - shows "Califica este curso" when user has not rated
    - InteractiveStarRating shows 0 selected stars
    - does not show delete button

  describe('Submit rating')
    - disables InteractiveStarRating while submitting
    - performs optimistic update on star click
    - shows success feedback after successful submit
    - reverts optimistic update on API error
    - shows error feedback on API failure
    - updates stats after successful submit

  describe('Delete rating')
    - calls deleteRating API on delete button click
    - resets user rating to 0 after deletion
    - updates stats after deletion
    - shows success feedback after deletion
    - reverts on delete error

  describe('Feedback messages')
    - shows success message and auto-hides after 3 seconds
    - shows error message on failure
```

### 7.4 Configuracion de Mocks para Tests

Los tests del `CourseRatingSection` necesitaran mockear `ratingsApi`:

```typescript
vi.mock('@/services/ratingsApi', () => ({
  ratingsApi: {
    getUserRating: vi.fn(),
    createRating: vi.fn(),
    deleteRating: vi.fn(),
    getRatingStats: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(message, status, code) {
      super(message);
      this.status = status;
      this.code = code;
    }
  }
}));
```

---

## 8. Orden de Implementacion Recomendado

El orden esta disenado para permitir testing incremental. Cada paso produce algo testeable de forma independiente.

```
PASO  ARCHIVO/TAREA                                    DEPENDENCIA   ESTIMACION
----  ------------------------------------------------ ------------- ----------
 1    Corregir types/rating.ts                          Ninguna       5 min
 2    Corregir types/index.ts                           Ninguna       5 min
 3    Corregir services/ratingsApi.ts (URL bug)         Ninguna       5 min
 4    Crear config/user.ts                              Ninguna       5 min
 5    Crear InteractiveStarRating + estilos             Ninguna       45 min
 6    Crear tests InteractiveStarRating                 Paso 5        30 min
 7    Crear RatingDistribution + estilos                Ninguna       30 min
 8    Crear tests RatingDistribution                    Paso 7        20 min
 9    Crear CourseRatingSection + estilos                Pasos 4-7     60 min
10    Crear tests CourseRatingSection                    Paso 9        45 min
11    Integrar en CourseDetailComponent                  Pasos 1-9     15 min
12    Test manual end-to-end con backend corriendo       Paso 11       15 min
```

Estimacion total: aproximadamente 4.5 horas de trabajo

---

## 9. Consideraciones de UX

### 9.1 Optimistic Updates
Cuando el usuario hace click en una estrella, el UI se actualiza inmediatamente sin esperar la respuesta del servidor. Esto proporciona feedback instantaneo. Si la API falla, se revierte al estado anterior con un mensaje de error.

### 9.2 Feedback Visual
- Feedback de exito: banner verde con "Calificacion guardada" que desaparece en 3 segundos
- Feedback de error: banner rojo con mensaje descriptivo
- Estado de carga: estrellas deshabilitadas con opacity reducida durante el submit
- Hover preview: las estrellas se iluminan en un tono mas claro al pasar el mouse, dando preview de la calificacion

### 9.3 Prevencion de Clicks Multiples
El estado `submitting` deshabilita las estrellas y el boton de eliminar durante la llamada API, previniendo doble submit.

### 9.4 Transiciones
- Fade-in del mensaje de feedback con animacion CSS
- Scale en hover de estrellas (1.15x)
- Transiciones de color suaves (0.15s) en las estrellas

---

## 10. Consideraciones de Accesibilidad

### 10.1 Estructura Semantica
- `<section>` para la seccion de ratings con `aria-labelledby`
- `role="radiogroup"` para el grupo de estrellas
- `role="radio"` para cada estrella individual
- `aria-checked` para indicar seleccion
- `aria-disabled` cuando esta deshabilitado

### 10.2 Navegacion por Teclado
- Tab: navegar entre estrellas
- Enter/Space: seleccionar estrella
- Las estrellas son `<button>` nativos, no `<span>` con onClick
- Focus visible con outline (`:focus-visible`)

### 10.3 Screen Readers
- Cada estrella: `aria-label="Calificar {n} de 5 estrellas"`
- Grupo: `aria-label="Califica este curso"`
- Feedback: `role="status"` con `aria-live="polite"` para anuncios
- Rating actual: `aria-label="Tu calificacion actual: {n} de 5 estrellas"`

### 10.4 Contraste de Colores
- Estrellas llenas (#ffc107 amarillo) sobre fondo blanco: ratio 1.74 (decorativo, no texto)
- Texto de feedback: colores con contraste suficiente (#28a745 verde, color('primary') rojo)
- Estrellas vacias (#4a4a4a) sobre fondo blanco: ratio 7.0+ (cumple WCAG AA)

---

## 11. Consideraciones Tecnicas

### 11.1 Rendimiento
- `CourseRatingSection` solo se carga en la pagina de detalle (no en el home)
- Solo 1 llamada API adicional al montar (`getUserRating`). Los stats iniciales vienen del Server Component
- No se usa polling ni WebSocket. Los stats se refrescan solo despues de una accion del usuario
- Las animaciones CSS son GPU-accelerated (transform, opacity)

### 11.2 Manejo de Errores
- Network timeouts: ratingsApi ya maneja con 10s timeout
- API errors: se capturan y muestran al usuario con mensaje descriptivo
- Optimistic revert: cualquier error revierte el UI al estado anterior
- Si falla la carga del rating del usuario, se asume sin rating (degradacion graceful)

### 11.3 Consistencia con Patrones Existentes
- CSS Modules con `@import '../../styles/vars.scss'` y uso de `color()` function
- Mismos border-radius (18px cards, 12px buttons, 8px inputs)
- Mismos box-shadow patterns
- Mismos font-weights (900 numeros grandes, 800 titulos, 700 subtitulos, 600 labels, 500 texto)
- Mismas transiciones (`transition: all 0.2s`)

### 11.4 Limitaciones Conocidas
1. Sin autenticacion: Se usa MOCK_USER_ID = 1, lo que significa que todos los usuarios del frontend comparten el mismo rating. Esto es temporal.
2. Sin persistencia de sesion: Si el usuario recarga la pagina, se vuelve a consultar el rating del mock user.
3. Stats no se actualizan en real-time: Los stats solo se refrescan cuando el usuario actual califica. Otros usuarios calificando no se reflejan hasta recargar.
4. Sin validacion client-side de curso existente: Se confia en que el courseId es valido porque viene del Server Component.

---

## 12. Consideraciones de Seguridad

### 12.1 Estado Actual (Sin Auth)
- El `user_id` se envia en el body del request, cualquiera podria suplantar a otro usuario
- Esto es aceptable para la fase actual de desarrollo pero NO para produccion
- El backend no valida autenticacion, solo que el user_id sea un entero positivo

### 12.2 Mitigaciones Futuras (Cuando se Implemente Auth)
- Reemplazar `MOCK_USER_ID` por token JWT decodificado
- El backend deberia extraer `user_id` del token, no del body
- Agregar middleware de autenticacion en los endpoints de ratings
- Eliminar `user_id` del `RatingRequest` (se obtiene del token)

---

## 13. Diagrama de Archivos Final

```
Frontend/src/
  config/
    user.ts                                          [NUEVO]
  types/
    index.ts                                         [MODIFICAR]
    rating.ts                                        [MODIFICAR]
  services/
    ratingsApi.ts                                    [MODIFICAR]
  components/
    StarRating/                                      [SIN CAMBIOS]
      StarRating.tsx
      StarRating.module.scss
      __tests__/StarRating.test.tsx
    InteractiveStarRating/                           [NUEVO]
      InteractiveStarRating.tsx
      InteractiveStarRating.module.scss
      __tests__/InteractiveStarRating.test.tsx
    RatingDistribution/                              [NUEVO]
      RatingDistribution.tsx
      RatingDistribution.module.scss
      __tests__/RatingDistribution.test.tsx
    CourseRatingSection/                              [NUEVO]
      CourseRatingSection.tsx
      CourseRatingSection.module.scss
      __tests__/CourseRatingSection.test.tsx
    CourseDetail/
      CourseDetail.tsx                                [MODIFICAR]
      CourseDetail.module.scss                        [SIN CAMBIOS]
  app/
    course/[slug]/
      page.tsx                                       [SIN CAMBIOS]
```

---

## 14. Criterios de Aceptacion

### Funcionales
- [ ] El usuario puede ver el promedio de calificaciones y la distribucion en la pagina de detalle
- [ ] El usuario puede calificar un curso haciendo click en una estrella (1-5)
- [ ] Al hacer hover sobre las estrellas, se muestra un preview visual
- [ ] Si el usuario ya califico, su calificacion aparece preseleccionada
- [ ] El usuario puede actualizar su calificacion haciendo click en otra estrella
- [ ] El usuario puede eliminar su calificacion con el boton "Eliminar calificacion"
- [ ] Despues de calificar/actualizar/eliminar, las estadisticas se actualizan
- [ ] Se muestra feedback visual de exito/error tras cada accion

### Tecnicos
- [ ] Todos los nuevos componentes tienen tests unitarios con cobertura mayor al 80%
- [ ] No hay errores de TypeScript (strict mode)
- [ ] Los estilos siguen las convenciones del proyecto (CSS Modules, SCSS, color tokens)
- [ ] Los Client Components usan "use client" directive
- [ ] La pagina de detalle sigue funcionando como Server Component
- [ ] Las llamadas API usan el servicio ratingsApi existente
- [ ] El bug en getUserRating (URL) esta corregido

### Accesibilidad
- [ ] Las estrellas interactivas son navegables por teclado (Tab + Enter/Space)
- [ ] Los screen readers anuncian correctamente el estado de las estrellas
- [ ] Los mensajes de feedback son anunciados por screen readers (aria-live)
- [ ] Hay focus visible en todos los elementos interactivos

### UX
- [ ] Optimistic updates proporcionan feedback instantaneo
- [ ] El estado disabled previene doble submit
- [ ] Las animaciones son suaves y no distrayentes
- [ ] El layout es responsive (funciona en movil y desktop)
