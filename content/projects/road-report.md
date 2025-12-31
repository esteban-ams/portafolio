---
title: Road Report
slug: road-report
technologies:
  - Flutter
  - FastAPI
  - PostgreSQL
  - Geolocator
  - Riverpod
github: https://github.com/estebanmartinezsoto/road-report
demo: null
featured: true
image: /static/images/road-report.jpg
excerpt: Aplicacion movil para reportar infracciones de transporte publico. Grabacion de rutas GPS con deteccion de exceso de velocidad, captura de evidencia multimedia, y sistema de validacion inteligente con scoring automatico.
---

# Road Report

Aplicacion movil ciudadana para reportar infracciones de transporte publico en tiempo real. El sistema captura evidencia georeferenciada y valida automaticamente los reportes usando multiples fuentes de datos.

## Contexto

El transporte publico en muchas ciudades latinoamericanas presenta problemas de seguridad: exceso de velocidad, paradas en lugares prohibidos, y comportamiento temerario. Los ciudadanos no tenian una forma efectiva de reportar estas situaciones con evidencia verificable.

## Funcionalidades

### Grabacion de Rutas GPS

La app captura continuamente la posicion del usuario mientras viaja:

```dart
class RouteRecorder {
  final List<RoutePoint> _points = [];
  StreamSubscription? _subscription;

  void startRecording() {
    _subscription = Geolocator.getPositionStream(
      locationSettings: LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10, // metros
      ),
    ).listen((position) {
      _points.add(RoutePoint(
        lat: position.latitude,
        lng: position.longitude,
        speed: position.speed, // m/s
        timestamp: DateTime.now(),
      ));

      // Detectar exceso de velocidad
      if (position.speed > SPEED_LIMIT_MPS) {
        _triggerSpeedAlert(position);
      }
    });
  }
}
```

### Deteccion de Exceso de Velocidad

| Zona | Limite | Alerta |
|------|--------|--------|
| Urbana | 50 km/h | Amarilla |
| Escolar | 30 km/h | Roja |
| Autopista | 120 km/h | Amarilla |

El sistema compara la velocidad actual contra limites conocidos de la zona y genera alertas automaticas que el usuario puede confirmar como reporte.

### Captura de Evidencia

- **Fotos**: Captura de patente, interior del vehiculo
- **Video**: Clips cortos de situaciones peligrosas
- **Audio**: Grabacion de ambiente
- **Metadata**: GPS, timestamp, velocidad, direccion

### Sistema de Scoring

Cada reporte recibe un puntaje de confiabilidad basado en:

```python
def calculate_report_score(report: Report) -> float:
    score = 0.0

    # Evidencia multimedia
    if report.has_photo: score += 20
    if report.has_video: score += 30

    # Consistencia GPS
    if report.route_data:
        gps_quality = calculate_gps_consistency(report.route_data)
        score += gps_quality * 20

    # Historico del usuario
    user_reliability = get_user_reliability_score(report.user_id)
    score += user_reliability * 15

    # Corroboracion
    similar_reports = find_similar_reports(report)
    if len(similar_reports) > 0:
        score += min(len(similar_reports) * 5, 15)

    return min(score, 100)
```

## Arquitectura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Flutter    │────▶│   FastAPI    │────▶│  PostgreSQL  │
│     App      │     │   Backend    │     │   + PostGIS  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       └────────────▶│     S3       │
         (media)     │   Storage    │
                     └──────────────┘
```

### Backend FastAPI

```python
@router.post("/reports")
async def create_report(
    report: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Crear reporte
    db_report = Report(**report.dict(), user_id=current_user.id)
    db.add(db_report)
    db.commit()

    # Procesar en background
    background_tasks.add_task(
        process_report_score,
        report_id=db_report.id
    )
    background_tasks.add_task(
        check_similar_reports,
        report_id=db_report.id
    )

    return db_report
```

### Estado con Riverpod

```dart
final activeRouteProvider = StateNotifierProvider<RouteNotifier, RouteState>(
  (ref) => RouteNotifier(),
);

final nearbyReportsProvider = FutureProvider.family<List<Report>, LatLng>(
  (ref, location) async {
    final api = ref.read(apiProvider);
    return api.getNearbyReports(location, radiusKm: 1);
  },
);
```

## Desafios Tecnicos

### Precision GPS en Movimiento

El GPS puede ser impreciso en vehiculos en movimiento. Implementamos:
- Filtro de Kalman para suavizar la ruta
- Descarte de puntos con precision > 20 metros
- Interpolacion para gaps de senal

### Consumo de Bateria

La grabacion continua de GPS consume bateria. Optimizaciones:
- Distance filter de 10m (no cada segundo)
- Batch upload cuando hay WiFi
- Modo "dormido" cuando no hay movimiento

### Validacion de Reportes Falsos

Para evitar reportes maliciosos:
- Scoring automatico basado en multiples factores
- Verificacion cruzada con otros usuarios
- Historico de confiabilidad por usuario
- Moderacion manual para reportes con score bajo

## Resultados

- **500+** usuarios activos en beta
- **2,000+** reportes procesados
- **85%** de reportes con score > 70
- **< 5%** de reportes identificados como falsos
