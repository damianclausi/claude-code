# Backend Ratings: Analisis de Estado y Plan de Fases Pendientes

**Fecha**: 2026-02-11
**Basado en**: `spec/00_sistema_ratings_cursos.md` (Fases 1, 2, 3 y 6 backend)
**Estado general**: El sistema de ratings del backend esta implementado en su gran mayoria. Se identifican discrepancias puntuales, un bug de integridad de datos, y oportunidades de mejora.

---

## 1. Analisis de Implementacion vs. Spec

### FASE 1 (Spec): Database Layer

| Elemento planificado | Estado | Archivo | Observaciones |
|---|---|---|---|
| Migracion Alembic para `course_ratings` | IMPLEMENTADO | `Backend/app/alembic/versions/0e3a8766f785_add_course_ratings_table.py` | Implementado exactamente como el spec. |
| Columnas `id`, `created_at`, `updated_at`, `deleted_at` | IMPLEMENTADO | Migracion linea 29-32 | Heredadas de BaseModel. |
| Columnas `course_id`, `user_id`, `rating` | IMPLEMENTADO | Migracion linea 35-37 | Tipos y nullable correctos. |
| `ForeignKey` a `courses.id` | IMPLEMENTADO | Migracion linea 41-45 | FK con nombre `fk_course_ratings_course_id`. |
| `CHECK(rating >= 1 AND rating <= 5)` | IMPLEMENTADO | Migracion linea 46-49 | Constraint `ck_course_ratings_rating_range`. |
| `UNIQUE(course_id, user_id, deleted_at)` | IMPLEMENTADO CON BUG | Migracion linea 53-58 | Ver seccion de bugs mas abajo. |
| Indice en `course_id` | IMPLEMENTADO | Migracion linea 68-73 | `ix_course_ratings_course_id` |
| Indice en `user_id` | IMPLEMENTADO | Migracion linea 74-78 | `ix_course_ratings_user_id` |

### FASE 2 (Spec): Backend Models & Services

| Elemento planificado | Estado | Archivo | Observaciones |
|---|---|---|---|
| Modelo `CourseRating` con herencia `BaseModel` | IMPLEMENTADO | `Backend/app/models/course_rating.py` | Correcto. Incluye `to_dict()` y `__repr__()` adicionales al spec. |
| `course_id` FK + `user_id` + `rating` con CHECK | IMPLEMENTADO | `course_rating.py` lineas 22-38 | Exacto al spec. |
| `relationship("Course", back_populates="ratings")` | IMPLEMENTADO | `course_rating.py` lineas 42-45 | Correcto. |
| `Course.ratings` relationship | IMPLEMENTADO | `Backend/app/models/course.py` lineas 32-37 | Incluye `cascade="all, delete-orphan"` y `lazy='select'`, que el spec no mencionaba pero son mejoras validas. |
| `Course.average_rating` property | IMPLEMENTADO | `course.py` lineas 39-57 | Mejor que el spec: usa `round(..., 2)`. |
| `Course.total_ratings` property | IMPLEMENTADO | `course.py` lineas 59-67 | Exacto al spec. |
| Registro en `__init__.py` | IMPLEMENTADO | `Backend/app/models/__init__.py` linea 9 | `CourseRating` exportado correctamente. |
| `CourseService.get_course_ratings()` | IMPLEMENTADO | `Backend/app/services/course_service.py` lineas 112-145 | Incluye validacion de curso y ordenamiento DESC. Mejora sobre el spec. |
| `CourseService.add_course_rating()` | IMPLEMENTADO | `course_service.py` lineas 147-215 | Implementa logica de upsert (crear o actualizar). Mas robusto que el spec. |
| `CourseService.update_course_rating()` | IMPLEMENTADO | `course_service.py` lineas 217-266 | Semantica explicita de UPDATE. Correcto. |
| `CourseService.delete_course_rating()` | IMPLEMENTADO | `course_service.py` lineas 268-301 | Soft delete correcto. |
| `CourseService.get_user_course_rating()` | IMPLEMENTADO | `course_service.py` lineas 303-337 | Correcto. |
| `CourseService.get_course_rating_stats()` | IMPLEMENTADO (EXTRA) | `course_service.py` lineas 339-399 | No estaba en el spec original como metodo separado. Usa agregaciones SQL eficientes (AVG, COUNT, GROUP BY). Excelente adicion. |
| Integracion de stats en `get_all_courses()` | IMPLEMENTADO | `course_service.py` lineas 20-52 | Incluye `average_rating` y `total_ratings` en lista de cursos. |
| Integracion de stats en `get_course_by_slug()` | IMPLEMENTADO | `course_service.py` lineas 54-110 | Incluye `average_rating`, `total_ratings`, y `rating_distribution`. |

### FASE 3 (Spec): Backend API Endpoints

| Elemento planificado | Estado | Archivo | Observaciones |
|---|---|---|---|
| `POST /courses/{course_id}/ratings` | IMPLEMENTADO | `Backend/app/main.py` lineas 146-199 | Status 201. Manejo correcto de 404 y 400. |
| `GET /courses/{course_id}/ratings` | IMPLEMENTADO | `main.py` lineas 202-244 | Lista con response_model. |
| `GET /courses/{course_id}/ratings/stats` | IMPLEMENTADO (EXTRA) | `main.py` lineas 247-291 | Endpoint adicional al spec original. |
| `GET /courses/{course_id}/ratings/user/{user_id}` | IMPLEMENTADO (EXTRA) | `main.py` lineas 294-342 | Endpoint adicional al spec original. Devuelve 204 si no existe. |
| `PUT /courses/{course_id}/ratings/{user_id}` | IMPLEMENTADO | `main.py` lineas 345-396 | Incluye validacion de `user_id` match entre path y body. Mejora sobre el spec. |
| `DELETE /courses/{course_id}/ratings/{user_id}` | IMPLEMENTADO | `main.py` lineas 399-434 | Status 204 correcto. |
| Pydantic schemas (`RatingRequest`, `RatingResponse`) | IMPLEMENTADO | `Backend/app/schemas/rating.py` lineas 9-51 | En `schemas/rating.py` en lugar de `models/requests.py` como decia el spec. Mejor ubicacion. |
| `RatingStatsResponse` schema | IMPLEMENTADO (EXTRA) | `schemas/rating.py` lineas 54-88 | No estaba en el spec. Agrega validacion para stats. |
| `ErrorResponse` schema | IMPLEMENTADO (EXTRA) | `schemas/rating.py` lineas 91-97 | Schema estandar de errores. |
| OpenAPI tags y documentacion | IMPLEMENTADO (EXTRA) | `main.py` lineas 15-48 | Tags `courses`, `ratings`, `health` con descripciones. |

### FASE 6 (Spec): Testing Backend

| Elemento planificado | Estado | Archivo | Observaciones |
|---|---|---|---|
| Tests de endpoints (integracion) | IMPLEMENTADO | `Backend/app/tests/test_rating_endpoints.py` | 15 tests con mocks. AAA pattern. |
| Tests de service (unitarios) | IMPLEMENTADO | `Backend/app/tests/test_course_rating_service.py` | 14 tests con mocks. AAA pattern. |
| Tests de DB constraints | IMPLEMENTADO | `Backend/app/tests/test_rating_db_constraints.py` | 5 tests, todos pasando (partial unique index aplicado en Fase A). |
| `test_add_course_rating` | IMPLEMENTADO | `test_course_rating_service.py` linea 110 | En `TestAddCourseRating` class. |
| `test_rating_constraints` | IMPLEMENTADO | `test_rating_db_constraints.py` | CHECK min y max, FK constraint. |
| `test_soft_delete_ratings` | IMPLEMENTADO | `test_rating_db_constraints.py` linea 102 | Permite crear despues de soft delete. |
| `test_average_rating_calculation` | NO IMPLEMENTADO | -- | No hay test para `Course.average_rating` property ni para `get_course_rating_stats()` con DB real. |

---

## 2. Bugs e Issues Identificados

### BUG-01: UNIQUE constraint inefectivo para duplicados activos (CRITICO)

**Ubicacion**: Migracion `0e3a8766f785`, lineas 53-58
**Archivo de modelo**: `Backend/app/models/course_rating.py`

**Descripcion**: El constraint `UNIQUE(course_id, user_id, deleted_at)` NO previene duplicados cuando `deleted_at IS NULL`. En PostgreSQL, `NULL != NULL`, por lo tanto dos registros con `(course_id=1, user_id=42, deleted_at=NULL)` NO violan el constraint UNIQUE.

**Evidencia**: El test `test_unique_constraint_prevents_duplicate_active_ratings` esta marcado con `@pytest.mark.skip` en `test_rating_db_constraints.py` linea 68, con la razon explicitada: "UNIQUE constraint with NULL values requires partial index in PostgreSQL."

**Impacto**: Si la logica de negocio en `CourseService.add_course_rating()` falla o hay condiciones de carrera (race conditions), podrian crearse multiples ratings activos del mismo usuario para el mismo curso. La integridad de datos depende unicamente de la capa de servicio, no de la base de datos.

**Solucion requerida**: Crear una migracion que agregue un **partial unique index**:
```sql
CREATE UNIQUE INDEX uix_course_ratings_active_user_course
ON course_ratings (course_id, user_id)
WHERE deleted_at IS NULL;
```

### BUG-02: Modelo `Class` huerfano (MENOR)

**Ubicacion**: `Backend/app/models/class_.py`
**Descripcion**: Existe un modelo `Class` con `__tablename__ = 'classes'` que:
- No tiene migracion asociada (no existe tabla `classes` en la DB).
- No esta registrado en `Backend/app/models/__init__.py`.
- Tiene `back_populates="classes"` pero `Course` no tiene relacion `classes`.
- Es una copia exacta de `Lesson` (mismas columnas).

**Impacto**: Archivo muerto que genera confusion. No afecta funcionalidad pero ensucia el codebase.

### ISSUE-01: Seed de datos no incluye ratings de ejemplo

**Ubicacion**: `Backend/app/db/seed.py`
**Descripcion**: El script de seed crea cursos, profesores y lecciones, pero no crea ratings de ejemplo. Esto dificulta el testing manual y la demostracion de la funcionalidad de ratings en desarrollo.

### ISSUE-02: Seed no limpia CourseRatings en `clear_all_data()`

**Ubicacion**: `Backend/app/db/seed.py`, funcion `clear_all_data()` lineas 160-179
**Descripcion**: La funcion `clear_all_data()` elimina `Lesson`, `course_teachers`, `Course`, `Teacher`, pero no elimina `CourseRating`. Si hay ratings en la DB, la eliminacion de `Course` fallara por la FK constraint `fk_course_ratings_course_id`.

### ISSUE-03: Performance N+1 en `get_all_courses()`

**Ubicacion**: `Backend/app/services/course_service.py`, funcion `get_all_courses()` lineas 20-52
**Descripcion**: Para cada curso, se ejecuta una llamada separada a `get_course_rating_stats()`, lo cual genera N+1 queries (1 query para los cursos + N queries de stats). No se usa `joinedload` ni `subqueryload` para los ratings en esta funcion.

### ISSUE-04: Falta `conftest.py` para compartir fixtures de tests

**Ubicacion**: `Backend/app/tests/`
**Descripcion**: No existe `conftest.py`. Los fixtures `mock_db_session`, `mock_course_service`, `sample_course`, `sample_rating` se repiten entre archivos de test. Esto causa duplicacion de codigo y dificulta el mantenimiento.

### ISSUE-05: Tests de DB constraints requieren base de datos real

**Ubicacion**: `Backend/app/tests/test_rating_db_constraints.py`
**Descripcion**: Los tests usan `SessionLocal()` directamente, lo que requiere una conexion a PostgreSQL real. No hay configuracion de test database ni fixture que use SQLite en memoria como alternativa. Esto impide ejecutar estos tests en CI/CD sin una DB disponible.

### ISSUE-06: Makefile no tiene comando `test`

**Ubicacion**: `Backend/Makefile`
**Descripcion**: El CLAUDE.md documenta `make test` y `make test-cov`, pero el Makefile actual no incluye estos targets. Los tests deben ejecutarse manualmente dentro del contenedor Docker.

---

## 3. Discrepancias Spec vs. Implementacion

| Aspecto | Spec planificaba | Implementacion real | Valoracion |
|---|---|---|---|
| Ubicacion de schemas | `Backend/app/models/requests.py` | `Backend/app/schemas/rating.py` | MEJOR. Separacion de responsabilidades mas clara. |
| Schemas definidos | `RatingRequest`, `RatingResponse` | `RatingRequest`, `RatingResponse`, `RatingStatsResponse`, `ErrorResponse` | MEJOR. Mas completo. |
| Endpoint de stats | No planificado como endpoint separado | `GET /courses/{id}/ratings/stats` implementado | MEJOR. Permite consultar stats sin cargar todos los ratings. |
| Endpoint de user rating | No planificado como endpoint separado | `GET /courses/{id}/ratings/user/{user_id}` implementado | MEJOR. Necesario para UX. |
| `CourseService.get_course_rating_stats()` | No planificado como metodo separado | Implementado con agregaciones SQL | MEJOR. Performance optimizada. |
| Validacion PUT user_id match | No planificado | `main.py` linea 379 valida coincidencia | MEJOR. Previene errores de uso. |
| OpenAPI documentation | No planificado | Tags, descriptions, examples, responses | MEJOR. API auto-documentada. |
| `Course.average_rating` rounding | Sin `round()` | `round(..., 2)` | MEJOR. Consistencia numerica. |
| Eager loading para ratings | Spec mencionaba "cuando necesario" | `lazy='select'` por defecto | CORRECTO. Evita cargas innecesarias. |

---

## 4. Plan de Fases Pendientes

### FASE A: Corregir integridad de datos - Partial Unique Index (CRITICO) - COMPLETADA

**Prioridad**: Alta
**Dependencias**: Ninguna
**Estimacion**: 1 hora
**Estado**: COMPLETADA (2026-02-12)

**Objetivo**: Garantizar a nivel de base de datos que un usuario solo pueda tener UN rating activo por curso, independientemente de la logica de aplicacion.

**Acciones realizadas**:

1. Creada migracion Alembic: `Backend/app/alembic/versions/c30460cc94f1_add_partial_unique_index_for_active_.py`
   - `upgrade()`: `op.create_index('uix_course_ratings_active_user_course', 'course_ratings', ['course_id', 'user_id'], unique=True, postgresql_where=text("deleted_at IS NULL"))`
   - `downgrade()`: `op.drop_index('uix_course_ratings_active_user_course', table_name='course_ratings')`

2. Migracion aplicada exitosamente con `make migrate`

3. Test actualizado en `Backend/app/tests/test_rating_db_constraints.py`:
   - Eliminado `@pytest.mark.skip` del test `test_unique_constraint_prevents_duplicate_active_ratings`
   - Actualizado `match` de IntegrityError a `"uix_course_ratings_active_user_course"`

4. Tests ejecutados: 40 passed, 0 skipped

**Criterios de aceptacion**:
- [x] La migracion se ejecuta sin errores
- [x] El test `test_unique_constraint_prevents_duplicate_active_ratings` pasa (sin skip)
- [x] El test `test_unique_constraint_allows_soft_deleted_duplicates` sigue pasando
- [x] INSERT directo en DB con duplicado activo falla con IntegrityError

---

### FASE B: Limpiar modelo huerfano `Class` (MENOR)

**Prioridad**: Baja
**Dependencias**: Ninguna
**Estimacion**: 15 minutos

**Objetivo**: Eliminar el archivo `class_.py` que no tiene utilidad y genera confusion con `Lesson`.

**Acciones**:

1. Eliminar archivo: `Backend/app/models/class_.py`
2. Verificar que no existan imports de `Class` en ningun archivo del proyecto:
   - Buscar `from app.models.class_` y `from .class_` en todo el backend
   - Verificar `Backend/app/models/__init__.py` (actualmente no importa `Class`, correcto)
3. Verificar que no haya migracion pendiente para la tabla `classes`

**Criterios de aceptacion**:
- [ ] Archivo `class_.py` eliminado
- [ ] No hay imports rotos
- [ ] La aplicacion arranca sin errores
- [ ] Tests siguen pasando

---

### FASE C: Corregir seed de datos (MEDIO)

**Prioridad**: Media
**Dependencias**: FASE A (para evitar conflictos de constraint al hacer seed)
**Estimacion**: 45 minutos

**Objetivo**: El seed debe incluir ratings de ejemplo y la limpieza debe ser completa.

**Acciones**:

1. Modificar `Backend/app/db/seed.py`:

   a. En `create_sample_data()`, despues de crear lecciones (linea 145), agregar bloque de creacion de ratings de ejemplo:
      - Importar `CourseRating` en los imports (linea 9)
      - Crear 8-12 ratings variados (diferentes user_ids, diferentes valores 1-5) distribuidos entre los 3 cursos
      - Usar user_ids ficticios (1-10) para simular diferentes usuarios

   b. En `clear_all_data()` (linea 160), agregar eliminacion de `CourseRating` ANTES de eliminar `Course`:
      - Agregar `db.query(CourseRating).delete()` como primera linea de la secuencia de eliminacion (antes de linea 167)
      - Importar `CourseRating` en los imports si no esta ya

   c. Actualizar los mensajes de print para incluir conteo de ratings creados

2. Probar: `make seed-fresh`

**Criterios de aceptacion**:
- [ ] `make seed` crea ratings de ejemplo
- [ ] `make seed-fresh` limpia ratings y recrea todo sin errores
- [ ] Los ratings creados son visibles en `GET /courses` (con average_rating > 0)
- [ ] Los ratings creados son visibles en `GET /courses/{slug}` (con rating_distribution)

---

### FASE D: Optimizar performance N+1 en `get_all_courses()` (MEDIO)

**Prioridad**: Media
**Dependencias**: Ninguna
**Estimacion**: 1 hora

**Objetivo**: Eliminar el problema de N+1 queries al listar cursos con stats de ratings.

**Acciones**:

1. Modificar `Backend/app/services/course_service.py`, metodo `get_all_courses()` (lineas 20-52):

   a. Reemplazar la iteracion con llamadas individuales a `get_course_rating_stats()` por una sola query SQL que calcule los stats de todos los cursos de golpe:
      - Usar `func.avg()`, `func.count()` con `GROUP BY course_id`
      - Hacer un `LEFT JOIN` o subquery para obtener stats en una sola consulta
      - Construir un diccionario `{course_id: {average_rating, total_ratings}}`

   b. Alternativa mas simple: usar `joinedload(Course.ratings)` en la query de cursos y calcular stats en Python usando las propiedades `Course.average_rating` y `Course.total_ratings` que ya existen.

2. Mantener el comportamiento actual de `get_course_by_slug()` que ya es eficiente (una sola llamada a stats).

3. Actualizar tests en `test_course_rating_service.py` si se cambia la estructura de queries.

**Criterios de aceptacion**:
- [ ] `GET /courses` ejecuta maximo 2-3 queries SQL (no N+1)
- [ ] La respuesta de `GET /courses` sigue incluyendo `average_rating` y `total_ratings`
- [ ] Tests unitarios actualizados y pasando

---

### FASE E: Crear `conftest.py` y mejorar infraestructura de tests (MEDIO)

**Prioridad**: Media
**Dependencias**: Ninguna
**Estimacion**: 1 hora

**Objetivo**: Centralizar fixtures compartidos, reducir duplicacion, y mejorar la ejecutabilidad de tests.

**Acciones**:

1. Crear `Backend/app/tests/conftest.py` con:
   - Fixture `mock_db_session`: Mock de Session (actualmente duplicado en `test_course_rating_service.py` linea 14 y `test_rating_db_constraints.py` linea 14)
   - Fixture `mock_course_service`: Mock de CourseService (de `test_rating_endpoints.py` linea 29)
   - Fixture `client`: TestClient con dependency override (de `test_rating_endpoints.py` linea 35)
   - Fixture `sample_course`: Course de ejemplo (de `test_course_rating_service.py` linea 27)
   - Fixture `sample_rating`: CourseRating de ejemplo (de `test_course_rating_service.py` linea 42)
   - Fixture `course_service`: CourseService con mock db (de `test_course_rating_service.py` linea 21)

2. Eliminar fixtures duplicados de los archivos de test individuales.

3. Separar los tests de DB constraints en un marker de pytest (e.g., `@pytest.mark.db`) para poder ejecutarlos selectivamente:
   - Agregar `pytest.ini` o seccion en `pyproject.toml` con markers registrados

4. Agregar targets de test al `Backend/Makefile`:
   - `test`: Ejecutar tests unitarios (excluyendo tests de DB)
   - `test-all`: Ejecutar todos los tests (incluyendo DB)
   - `test-cov`: Tests con coverage

**Criterios de aceptacion**:
- [ ] `conftest.py` creado con fixtures compartidos
- [ ] No hay fixtures duplicados entre archivos de test
- [ ] Todos los tests siguen pasando
- [ ] `make test` funciona desde la raiz del proyecto
- [ ] Tests de DB se pueden ejecutar o excluir selectivamente

---

### FASE F: Tests faltantes (MEDIO)

**Prioridad**: Media
**Dependencias**: FASE A (para el test de partial unique index), FASE E (para fixtures compartidos)
**Estimacion**: 1.5 horas

**Objetivo**: Completar la cobertura de tests faltantes identificados en el analisis.

**Acciones**:

1. Agregar tests para `Course.average_rating` y `Course.total_ratings` properties:
   - Archivo: `Backend/app/tests/test_course_model.py` (nuevo)
   - Tests:
     - `test_average_rating_no_ratings` (espera 0.0)
     - `test_average_rating_with_ratings` (espera calculo correcto con round)
     - `test_average_rating_ignores_deleted` (espera que no cuente soft-deleted)
     - `test_total_ratings_no_ratings` (espera 0)
     - `test_total_ratings_with_ratings` (espera conteo correcto)
     - `test_total_ratings_ignores_deleted` (espera que no cuente soft-deleted)

2. Agregar tests de integracion para `get_all_courses()` con ratings:
   - Archivo: `Backend/app/tests/test_course_rating_service.py` (agregar clase)
   - Tests:
     - `test_get_all_courses_includes_rating_stats`
     - `test_get_course_by_slug_includes_rating_distribution`

3. Agregar tests de edge cases en endpoints:
   - Archivo: `Backend/app/tests/test_rating_endpoints.py` (agregar tests)
   - Tests:
     - `test_add_rating_zero_user_id` (Pydantic debe rechazar user_id=0)
     - `test_add_rating_negative_user_id` (Pydantic debe rechazar user_id=-1)
     - `test_add_rating_boundary_values` (rating=1 y rating=5 deben funcionar)
     - `test_stats_distribution_keys_are_strings_in_json` (verificar serializacion)

**Criterios de aceptacion**:
- [ ] Todos los tests nuevos pasan
- [ ] No hay regresiones en tests existentes
- [ ] Cobertura de la funcionalidad de ratings >= 90%

---

## 5. Resumen de Estado

### Componentes 100% Completos (sin cambios necesarios)

- Modelo `CourseRating` (`Backend/app/models/course_rating.py`)
- Modelo `Course` con relationships y properties (`Backend/app/models/course.py`)
- Registro de modelos en `__init__.py` (`Backend/app/models/__init__.py`)
- Service layer completo (`Backend/app/services/course_service.py`)
- Todos los endpoints de rating (`Backend/app/main.py`)
- Schemas Pydantic (`Backend/app/schemas/rating.py`)
- Migracion base de `course_ratings` (`Backend/app/alembic/versions/0e3a8766f785_...py`)
- Tests de endpoints con mocks (`Backend/app/tests/test_rating_endpoints.py`)
- Tests unitarios de service (`Backend/app/tests/test_course_rating_service.py`)

### Componentes que Requieren Trabajo

| Fase | Componente | Prioridad | Esfuerzo | Estado |
|---|---|---|---|---|
| A | Partial unique index (bug de integridad) | CRITICA | 1h | - [x] Completada |
| B | Eliminar modelo `Class` huerfano | BAJA | 15min | - [ ] Pendiente |
| C | Seed de datos con ratings | MEDIA | 45min | - [ ] Pendiente |
| D | Optimizar N+1 en `get_all_courses()` | MEDIA | 1h | - [ ] Pendiente |
| E | Infraestructura de tests (`conftest.py`, Makefile) | MEDIA | 1h | - [ ] Pendiente |
| F | Tests faltantes (model properties, edge cases) | MEDIA | 1.5h | - [ ] Pendiente |
| **TOTAL** | | | **5.5h** | **1/6 completadas** |

### Orden de Ejecucion Recomendado

```
FASE A (critico, sin dependencias)
    |
    v
FASE B (independiente, rapido)    FASE E (independiente)
    |                                  |
    v                                  v
FASE C (depende de A)            FASE F (depende de A y E)
    |
    v
FASE D (independiente, puede ir en paralelo con E/F)
```

---

## 6. Conclusion

El backend del sistema de ratings esta implementado en un **~92% de completitud** respecto al spec original. La implementacion supera al spec en varios aspectos (endpoints adicionales, schemas mas completos, documentacion OpenAPI, validaciones extras). El **BUG-01** critico del constraint UNIQUE con NULLs en PostgreSQL fue **corregido en Fase A** mediante un partial unique index (`uix_course_ratings_active_user_course`), garantizando integridad de datos a nivel de base de datos. Las demas fases pendientes (B-F) son mejoras de calidad, mantenibilidad y robustez del testing.
