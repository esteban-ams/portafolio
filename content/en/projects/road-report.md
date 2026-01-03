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
excerpt: Mobile app for reporting public transport violations. GPS route recording with speeding detection, multimedia evidence capture, and intelligent validation system with automatic scoring.
---

# Road Report

Citizen mobile app for reporting public transport violations in real time. The system captures georeferenced evidence and automatically validates reports using multiple data sources.

## Context

Public transport in many Latin American cities has safety issues: speeding, stops in prohibited areas, and reckless behavior. Citizens didn't have an effective way to report these situations with verifiable evidence.

## Features

### GPS Route Recording

The app continuously captures user position while traveling:

```dart
class RouteRecorder {
  final List<RoutePoint> _points = [];
  StreamSubscription? _subscription;

  void startRecording() {
    _subscription = Geolocator.getPositionStream(
      locationSettings: LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10, // meters
      ),
    ).listen((position) {
      _points.add(RoutePoint(
        lat: position.latitude,
        lng: position.longitude,
        speed: position.speed, // m/s
        timestamp: DateTime.now(),
      ));

      // Detect speeding
      if (position.speed > SPEED_LIMIT_MPS) {
        _triggerSpeedAlert(position);
      }
    });
  }
}
```

### Speeding Detection

| Zone | Limit | Alert |
|------|-------|-------|
| Urban | 50 km/h | Yellow |
| School | 30 km/h | Red |
| Highway | 120 km/h | Yellow |

The system compares current speed against known zone limits and generates automatic alerts that the user can confirm as a report.

### Evidence Capture

- **Photos**: License plate capture, vehicle interior
- **Video**: Short clips of dangerous situations
- **Audio**: Ambient recording
- **Metadata**: GPS, timestamp, speed, direction

### Scoring System

Each report receives a reliability score based on:

```python
def calculate_report_score(report: Report) -> float:
    score = 0.0

    # Multimedia evidence
    if report.has_photo: score += 20
    if report.has_video: score += 30

    # GPS consistency
    if report.route_data:
        gps_quality = calculate_gps_consistency(report.route_data)
        score += gps_quality * 20

    # User history
    user_reliability = get_user_reliability_score(report.user_id)
    score += user_reliability * 15

    # Corroboration
    similar_reports = find_similar_reports(report)
    if len(similar_reports) > 0:
        score += min(len(similar_reports) * 5, 15)

    return min(score, 100)
```

## Architecture

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

### FastAPI Backend

```python
@router.post("/reports")
async def create_report(
    report: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create report
    db_report = Report(**report.dict(), user_id=current_user.id)
    db.add(db_report)
    db.commit()

    # Process in background
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

### State with Riverpod

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

## Technical Challenges

### GPS Precision in Motion

GPS can be imprecise in moving vehicles. We implemented:
- Kalman filter to smooth the route
- Discard points with precision > 20 meters
- Interpolation for signal gaps

### Battery Consumption

Continuous GPS recording consumes battery. Optimizations:
- Distance filter of 10m (not every second)
- Batch upload when on WiFi
- "Sleep" mode when no movement

### False Report Validation

To avoid malicious reports:
- Automatic scoring based on multiple factors
- Cross-verification with other users
- Reliability history per user
- Manual moderation for low-score reports

## Results

- **500+** active users in beta
- **2,000+** reports processed
- **85%** of reports with score > 70
- **< 5%** of reports identified as false
