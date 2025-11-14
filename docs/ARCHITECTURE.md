# System Architecture

Comprehensive architecture documentation for the Biometric Security Research System v2.0.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Performance Architecture](#performance-architecture)
- [Deployment Architecture](#deployment-architecture)

---

## Overview

The Biometric Security Research System is designed with a modular, layered architecture that separates concerns and promotes extensibility.

### Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: Easy to add new attack methods or defenses
3. **Security-First**: Defense-in-depth security model
4. **Performance**: Optimized for resource-constrained environments
5. **Testability**: All components are independently testable
6. **Configuration-Driven**: Behavior controlled by configuration

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface Layer                     │
│  ┌──────────────┐              ┌──────────────┐             │
│  │   main.py    │              │cli_enhanced.py│             │
│  │  (Standard)  │              │   (v2.0)      │             │
│  └──────────────┘              └──────────────┘             │
└────────────────┬────────────────────┬─────────────────────────┘
                 │                    │
┌────────────────┴────────────────────┴─────────────────────────┐
│                   Core Application Layer                       │
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Biometric │  │ Attacks  │  │ Defenses │  │Evaluation│      │
│  │          │  │          │  │          │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              Reporting & Visualization                │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────┬───────────────────────┬────────────────────────┘
                 │                       │
┌────────────────┴───────────────────────┴────────────────────────┐
│                  Infrastructure Layer                            │
│                                                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │Configuration│Security    │Performance  │  Logging    │       │
│  │  (config)  │  (utils/   │  (utils/    │  (utils/    │       │
│  │            │  security) │ performance)│   logger)   │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└─────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                     Data & Model Layer                           │
│                                                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  Enrolled │ │  Attack   │ │  Results  │ │  Models   │       │
│  │  Users    │ │  Samples  │ │           │ │           │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Biometric Authentication Module

```
biometric/
├── face_recognition.py
│   ├── FaceAuthenticator
│   │   ├── __init__()
│   │   ├── enroll_user()
│   │   ├── authenticate()
│   │   ├── save_model()
│   │   └── load_model()
│   └── RealtimeFaceAuth
│       └── run()
│
└── fingerprint_matcher.py
    └── FingerprintMatcher
        ├── enroll_fingerprint()
        ├── match_fingerprint()
        ├── save_database()
        └── load_database()
```

**Responsibilities:**
- Biometric data enrollment
- User authentication
- Model persistence
- Real-time processing

**Dependencies:**
- DeepFace (face recognition)
- OpenCV (image processing)
- NumPy (numerical operations)

### 2. Attack Simulation Module

```
attacks/
├── presentation_attacks.py
│   └── PresentationAttacks
│       ├── photo_attack()
│       ├── video_replay_attack()
│       ├── mask_attack_simulation()
│       ├── degraded_quality_attack()
│       └── synthetic_fingerprint()
│
├── adversarial_attacks.py
│   └── AdversarialAttacker
│       ├── generate_adversarial_patch()
│       ├── generate_fgsm_attack()
│       ├── generate_glasses_attack()
│       ├── generate_pixel_attack()
│       └── generate_morphing_attack()
│
└── deepfake_generator.py
    └── LightweightDeepfake
        └── simple_face_swap()
```

**Responsibilities:**
- Attack sample generation
- Multiple attack methods
- Batch attack processing
- Attack customization

**Design Patterns:**
- Factory pattern for attack generation
- Strategy pattern for attack types

### 3. Defense Module

```
defenses/
└── liveness_detection.py
    ├── LivenessDetector
    │   ├── detect_blink()
    │   ├── texture_analysis()
    │   ├── active_flash_test()
    │   ├── depth_analysis()
    │   └── color_diversity_analysis()
    │
    └── AntiSpoofingSystem
        ├── comprehensive_check()
        └── batch_test()
```

**Responsibilities:**
- Liveness detection
- Anti-spoofing checks
- Multi-method scoring
- Batch evaluation

**Design Patterns:**
- Composite pattern for multiple checks
- Strategy pattern for detection methods

### 4. Evaluation Module

```
evaluation/
└── vulnerability_tester.py
    └── VulnerabilityTester
        ├── test_genuine_users()
        ├── test_presentation_attacks()
        ├── test_with_antispoofing()
        ├── calculate_metrics()
        └── run_full_assessment()
```

**Responsibilities:**
- Security testing
- Metrics calculation
- Report generation
- Assessment orchestration

### 5. Reporting Module

```
reporting/
├── report_generator.py (v1.0)
└── enhanced_report.py (v2.0)
    └── EnhancedReportGenerator
        ├── generate_interactive_dashboard()
        ├── _create_metrics_gauges()
        ├── _create_attack_success_chart()
        └── _create_confusion_matrix()
```

**Responsibilities:**
- Report generation
- Data visualization
- Interactive dashboards
- Executive summaries

### 6. Utilities Module

```
utils/
├── logger.py
│   ├── SecurityLogger
│   ├── get_logger()
│   ├── log_execution_time()
│   └── LogContext
│
├── security.py
│   ├── InputValidator
│   ├── RateLimiter
│   ├── SecureDataHandler
│   └── AuditLogger
│
└── performance.py
    ├── PerformanceMonitor
    ├── LRUCache
    ├── EmbeddingCache
    └── optimize_memory()
```

**Responsibilities:**
- Cross-cutting concerns
- Logging and monitoring
- Security enforcement
- Performance optimization

---

## Data Flow

### User Enrollment Flow

```
User Input (Images)
    │
    ├──> InputValidator.validate_file_path()
    │
    ├──> RateLimiter.is_allowed()
    │
    ├──> FaceAuthenticator.enroll_user()
    │    │
    │    ├──> extract_face_embedding()
    │    │    │
    │    │    └──> DeepFace.represent()
    │    │
    │    └──> Store in enrolled_users{}
    │
    ├──> FaceAuthenticator.save_model()
    │
    └──> AuditLogger.log_enrollment()
```

### Authentication Flow

```
User Input (Test Image)
    │
    ├──> InputValidator.validate_file_path()
    │
    ├──> RateLimiter.is_allowed()
    │
    ├──> EmbeddingCache.get_embedding()
    │    │
    │    ├──> [Cache Hit] Return cached embedding
    │    │
    │    └──> [Cache Miss] FaceAuthenticator.extract_face_embedding()
    │         │
    │         └──> EmbeddingCache.put_embedding()
    │
    ├──> Compare with enrolled_users
    │    │
    │    └──> Calculate similarity scores
    │
    ├──> Apply threshold
    │
    ├──> AuditLogger.log_authentication_attempt()
    │
    └──> Return (user_id, score)
```

### Attack Generation Flow

```
Genuine Image
    │
    ├──> PresentationAttacks or AdversarialAttacker
    │    │
    │    ├──> Apply attack transformations
    │    │    │
    │    │    ├──> Texture simulation
    │    │    ├──> Artifact addition
    │    │    ├──> Quality degradation
    │    │    └──> Adversarial perturbations
    │    │
    │    └──> Save attack sample
    │
    └──> Return attack image path
```

### Vulnerability Testing Flow

```
Test Data
    │
    ├──> VulnerabilityTester.run_full_assessment()
    │    │
    │    ├──> test_genuine_users()
    │    │    └──> Calculate FRR
    │    │
    │    ├──> Generate attacks
    │    │
    │    ├──> test_presentation_attacks()
    │    │    └──> Calculate FAR
    │    │
    │    ├──> test_with_antispoofing()
    │    │    └──> Calculate detection rate
    │    │
    │    └──> calculate_metrics()
    │         └──> Calculate EER, accuracy
    │
    ├──> Save results to JSON
    │
    └──> EnhancedReportGenerator.generate_interactive_dashboard()
```

---

## Security Architecture

### Defense in Depth

```
Layer 1: Input Validation
    ├── File path validation
    ├── File size limits
    ├── Extension whitelisting
    └── User ID sanitization

Layer 2: Rate Limiting
    ├── Per-user limits
    ├── Time windows
    └── Automatic blocking

Layer 3: Authentication & Authorization
    ├── Biometric verification
    ├── Multi-factor support (future)
    └── Session management

Layer 4: Data Protection
    ├── Encryption at rest
    ├── Secure file deletion
    └── Constant-time comparisons

Layer 5: Audit & Monitoring
    ├── Comprehensive logging
    ├── Security event tracking
    └── Compliance reporting
```

### Security Components Interaction

```
Request → InputValidator → RateLimiter → Core Function
                ↓              ↓              ↓
           [Validated]    [Not blocked]   [Logged]
                                           ↓
                                    AuditLogger
```

---

## Performance Architecture

### Caching Strategy

```
Request for Embedding
    │
    ├──> LRU Cache Lookup
    │    │
    │    ├──> [Hit] Return cached (< 10ms)
    │    │
    │    └──> [Miss] Compute embedding (~ 500ms)
    │         │
    │         └──> Store in cache
    │
    └──> Return embedding
```

**Cache Configuration:**
- Max size: 1000 embeddings
- Eviction: Least Recently Used (LRU)
- Hit rate target: > 80%

### Memory Management

```
Operation Start
    │
    ├──> PerformanceMonitor.check_memory_limit()
    │    │
    │    ├──> [Under limit] Proceed
    │    │
    │    └──> [Over limit] optimize_memory()
    │         │
    │         └──> Force garbage collection
    │
    └──> Process operation
```

### Resource Limits

- Memory limit: 4GB (configurable)
- CPU cores: 1-2 (configurable)
- Batch size: 1 (configurable)
- Frame skip: 5 frames (real-time)

---

## Deployment Architecture

### Standalone Deployment

```
┌────────────────────────────────┐
│     Host Machine (8GB RAM)      │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Python Virtual Env       │  │
│  │                          │  │
│  │  ┌────────────────────┐  │  │
│  │  │ Application        │  │  │
│  │  │ - biometric/       │  │  │
│  │  │ - attacks/         │  │  │
│  │  │ - defenses/        │  │  │
│  │  └────────────────────┘  │  │
│  │                          │  │
│  │  ┌────────────────────┐  │  │
│  │  │ Data Storage       │  │  │
│  │  │ - enrolled_users/  │  │  │
│  │  │ - results/         │  │  │
│  │  └────────────────────┘  │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### Docker Deployment

```
┌────────────────────────────────┐
│     Docker Host                 │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Docker Container         │  │
│  │  (biometric-security)     │  │
│  │                          │  │
│  │  ┌────────────────────┐  │  │
│  │  │ Application        │  │  │
│  │  └────────────────────┘  │  │
│  │           │              │  │
│  │           ├──> Volume Mounts│
│  │           │              │  │
│  └───────────┼──────────────┘  │
│              │                 │
│  ┌───────────┴──────────────┐  │
│  │  Host Volumes            │  │
│  │  - data/                 │  │
│  │  - logs/                 │  │
│  │  - biometric/models/     │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### Network Architecture (Future Web Interface)

```
┌──────────┐
│ Browser  │
└────┬─────┘
     │ HTTPS
┌────┴─────────┐
│ Load Balancer │
└────┬─────────┘
     │
     ├──> ┌──────────────┐
     │    │  Web Server  │
     │    │  (Flask/     │
     │    │   FastAPI)   │
     │    └──────┬───────┘
     │           │
     │    ┌──────┴───────┐
     │    │  Application │
     │    │   (Core)     │
     │    └──────┬───────┘
     │           │
     │    ┌──────┴───────┐
     │    │  Data Layer  │
     │    │  (Files/DB)  │
     │    └──────────────┘
```

---

## Configuration Architecture

```
Environment Variables
       │
       ├──> .env file
       │
       ↓
SystemConfig
       │
       ├──> BiometricConfig
       ├──> LivenessConfig
       ├──> AttackConfig
       ├──> SecurityConfig
       ├──> PerformanceConfig
       ├──> LoggingConfig
       └──> PathsConfig
```

---

## Extension Points

### Adding New Attack Methods

1. Create new class in `attacks/`
2. Implement attack generation methods
3. Add to `cli_enhanced.py` options
4. Add tests in `tests/`

### Adding New Biometric Modalities

1. Create new module in `biometric/`
2. Implement enrollment/authentication
3. Update `VulnerabilityTester`
4. Add CLI commands

### Adding New Defense Mechanisms

1. Add method to `LivenessDetector`
2. Update `AntiSpoofingSystem.comprehensive_check()`
3. Add weight in scoring
4. Update reports

---

## Technology Stack

**Core:**
- Python 3.8+
- OpenCV 4.8+
- NumPy 1.24+

**ML/AI:**
- TensorFlow 2.16+
- DeepFace 0.0.79+
- scikit-learn 1.3+

**Visualization:**
- Plotly 5.18+
- Matplotlib 3.8+
- Seaborn 0.13+

**Infrastructure:**
- Docker
- GitHub Actions
- pytest

---

## Design Decisions

### Why Modular Architecture?
- Easy to test individual components
- Simple to add new features
- Clear separation of concerns
- Better maintainability

### Why Configuration-Driven?
- No code changes for parameter tuning
- Environment-specific settings
- Easy A/B testing
- Better security (no hardcoded values)

### Why Multi-Layer Security?
- Defense in depth
- Multiple checkpoints
- Graceful degradation
- Compliance requirements

### Why Performance Monitoring?
- Resource-constrained environments
- Early problem detection
- Optimization insights
- Capacity planning

---

For implementation details, see [API_REFERENCE.md](API_REFERENCE.md).
