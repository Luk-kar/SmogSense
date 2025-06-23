## 🌫️ Project Overview

**A unified data processing pipeline** for air quality, health, social media, and geospatial data using Dagster orchestration. The solution integrates multi-source environmental data, applies validation and transformation, and delivers structured outputs for analysis with these capabilities:

- **End-to-end ETL workflow** with validation, transformation, and storage
- **Unified data integration** from environmental, health, social, and spatial sources
- **Scalable architecture** supporting continuous data processing

### 🔑 Key Features

- **Multi-source Integration**: Processes air quality (GIOS), health (GUS), social media (Twitter/X), administrative regions, and geospatial data
- **Automated Orchestration**: Uses `Dagster` for dependency-aware pipeline management
- **Data Lake Implementation**: Leverages `MinIO` for versioned intermediate storage
- **Structured Storage**: `PostgreSQL` database with normalized schemas
- **Analytical Optimization**: Database views for pre-calculated visualization metrics
- **Validation Framework**: Comprehensive data quality checks at all stages
- **Containerized Deployment**: Docker-based isolated environments per pipeline component

## 🏗️ Architecture

### Core Components

#### 🌐 Data Sources
- **[Air Quality (GIOS API):](https://powietrze.gios.gov.pl/pjp/content/api?lang=en)**  
  📊 **Annual Statistics**: Historical pollutant measurements  
  📡 **Sensor Data**: Station data and real-time readings  
  🗺️ **Map Pollution**: Geographic concentration distributions  
  🔢 **Aggregates**: Daily measurement composites  
  ⚠️ **Air Quality Index**: Health risk assessments  
- **[Health Statistics (GUS API):](https://stat.gov.pl/en/)**  
  💀 **Causes of Death**: Categorized mortality data  
  👥 **Population Metrics**: Regional demographic statistics  
- **[Social Media (Twitter/X API):](https://developer.x.com/en/docs/x-api)**  
  💬 Public sentiment and event-related data  
- **[Administrative/Geospatial Data:](https://www.gugik.gov.pl/pzgik)**  
  🏞️ Regional boundaries and administrative hierarchies  

 


#### 🔄 Processing Workflow
1. **Data Acquisition**: API-based raw data collection
2. **Processing & Validation**: Transformation with quality check
3. **Data Lake**: Stores intermediate data in MinIO
4. **Database Upload**: Persists processed data to PostgreSQL
5. **Data Unification**: Cross-source integration

## ⚙️ Configuration

### 🔧 Environment Setup
Managed through `Docker` build arguments and runtime environment variables:

```bash
# Core Services
POSTGRES_HOST_PORT=5432
DAGSTER_POSTGRES_USER=dagster_user
DAGSTER_POSTGRES_PASSWORD=your_password
DAGSTER_POSTGRES_DB=dagster_db

# Pipeline Services
AIR_QUALITY_PIPELINE_PORT=4000
HEALTH_PIPELINE_PORT=4001
SOCIAL_MEDIA_PIPELINE_PORT=4002
WAREHOUSE_PIPELINE_PORT=4003
TERRITORY_PIPELINE_PORT=4004
MODELS_PIPELINE_PORT=4005

# Resource Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT_URL=http://minio:9000
POSTGRES_HOST=postgres
POSTGRES_USER=warehouse_user
POSTGRES_PASSWORD=warehouse_password
POSTGRES_WAREHOUSE_DB=warehouse

# GitHub Integration
GITHUB_DATA_REPO=your-org/your-data-repo
GITHUB_MINIO_SERVICE_PATH=path/to/minio/service.yaml
GITHUB_MINIO_FILE_NAME=minio.yaml
GITHUB_POSTGRES_SERVICE_PATH=path/to/postgres/service.yaml
GITHUB_POSTGRES_FILE_NAME=postgres.yaml

# MLflow Configuration
MLFLOW_TRACKING_URI=http://mlflow:5000
```
### 🔀 Dynamic Configuration

- **Jinja2 templates** generate Dagster configs from environment variables
- **Generator Scripts**: 
  - [`dagster_generator.py`](./dagster_generator.py)
  - [`workspace_generator.py`](./workspace_generator.py) 
- **Template Files**:
  - [`dagster.yaml.jinja`](./dagster.yaml.jinja)
  - [`workspace.yaml.jinja`](./workspace.yaml.jinja)
  
## ✅ Data Quality & Validation

The pipeline includes comprehensive data validation:

### ✔️ Asset Checks
- **Structural Validation**: Ensures DataFrames match expected schemas
- **Consistency**: Cross-stage data alignment
- **Referential Integrity**: Foreign key validation
- **Completeness**: Mandatory field verification

### 🛡️ Processing Safeguards
- **Null Handling**: Proper treatment of missing values
- **Type Conversion**: Ensures correct data types
- **Duplicate Detection**: Identifies and handles duplicate records
- **Foreign Key Mapping**: Maintains relationships between entities

### 🔄 Pipelines Services  
Dagster orchestrates domain pipelines via dedicated isolated [gRPC servers](https://docs.dagster.io/deployment/code-locations/workspace-yaml#running-your-own-grpc-server):

| Pipeline              | Port | Functionality                     |
|-----------------------|------|-----------------------------------|
| **Air Quality**       | 4000 | GIOS API processing               |
| **Health Statistics** | 4001 | GUS health data handling          |
| **Social Media**      | 4002 | Twitter/X extraction              |
| **Data Warehouse**    | 4003 | Warehousing operations            |
| **Territory**         | 4004 | Geospatial processing             |
| **Model Deployment**  | 4005 | ML model management               |

**Orchestration Core**:
- **Dagster Webserver** (Port `5000`): Pipeline visualization and control
- **Dagster Daemon**: Scheduled execution backend

**Unified Architecture**:
1. Isolated container environments
2. Port-based gRPC communication
3. Shared PostgreSQL/MinIO services
4. Health-monitored connectivity

The modular design allows independent updates to pipelines without disrupting others.

## 🚀 Deployment

### 🐳 Docker Setup

The project uses Docker for deployment with separate containers for:

- **Dagster Webserver**: Monitoring interface
- **Dagster Daemon**: Background processing
- **PostgreSQL**: Primary datastore
- **MinIO**: Object storage for data lake

## 📊 Monitoring & Operations

- **Real-time Visualization**: Dagster UI for execution tracking
- **Asset Materialization**: Data state monitoring
- **Validation Reporting**: Automated quality alerts
- **Comprehensive Logging**: Debugging and audit trails

## 💻 Usage

### ▶️ Running the Pipeline
1. Start Docker containers
2. Access Dagster UI at `localhost:5000`
3. Select target asset groups
4. Monitor materialization progress
5. Review validation reports

### 📂 Data Access Points
- PostgreSQL direct querying
- Dagster materialized assets
- Apache Superset dashboards
- MinIO object browser

## 🔧 Development

**➕ Adding New Data Sources:**
1. Create module in `src/orchestration/dagster/my_project/` (e.g., `weather`)
2. Implement acquisition in `src/data_acquisition/`
3. Add transformation/validation logic
4. Define database models (if new entities)
5. Implement asset checks

**🧩 Dagster Component Relationships**:
- **[Code Location](https://docs.dagster.io/concepts/repositories-workspaces/workspaces)**: Container for organizing related assets, resources, and jobs into deployable units
- **[Assets](https://docs.dagster.io/concepts/assets)** (`@asset`): Functions that produce data objects (tables/files/models) and define dependencies
- **[Asset Checks](https://docs.dagster.io/concepts/asset-checks)**: Validation rules attached to assets that verify data quality after materialization (e.g., schema compliance, null checks)
- **[Resources](https://docs.dagster.io/concepts/resources)**: Shared clients for external services (DBs, APIs) configured at runtime
- **[Jobs](https://docs.dagster.io/concepts/jobs)**: Executable units that run selections of assets, triggered manually or automatically
- **[Schedules](https://docs.dagster.io/concepts/schedules-sensors/schedules)**: Automation rules that trigger job executions at specified intervals (e.g., cron)

**⏭️ Workflow**: 
1. Code Location organizes assets/resources →  
2. Assets depend on resources →  
3. Jobs group assets and checks →  
4. Schedules trigger jobs →  
5. Runs execute pipelines and validate outputs

---

**📚 Official Documentation**:
For more information, refer to the official documentation:
- [Dagster Documentation](https://docs.dagster.io/) - Orchestration framework
- [MinIO Documentation](https://min.io/docs/) - Object storage system
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Database system
- [Docker Documentation](https://docs.docker.com/) - Containerization platform