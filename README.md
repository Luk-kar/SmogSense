# 🌫️🔧 SmogSense

A modular data platform integrating for end-to-end analytics, data pipelines orchestration, machine learning models registry and observability in local open-source environments.<br>
The example setup for the commercial cloud is here: [./server_deployment/README](./server_deployment/README)

Each service is deployed via <img src="doc/images/logo/docker_logo.png" alt="Docker logo" width="20"/> [`docker`](https://www.docker.com/):

**📊 Analytics:**
- <img src="doc/images/logo/postgres_logo.png" alt="pgAdmin logo" width="20"/> [pgAdmin:](https://www.pgadmin.org)<br>*PostgreSQL database web management tool.*
- <img src="doc/images/logo/superset_logo.png" alt="Superset logo" width="20"/> [Superset:](https://superset.apache.org)<br>*Data visualization and dashboarding platform.*

**🧪 Data Science:**
- <img src="doc/images/logo/jupyterlab_logo.png" alt="JupyterLab logo" width="20"/> [JupyterLab:](https://jupyter.org)<br>*Interactive data analysis notebooks.*

**📈 Monitoring Resources:**<br>
*[Documentation](https://github.com/Luk-kar/dockprom-and-logs)*
- <img src="doc/images/logo/prometheus_logo.png" alt="Prometheus logo" width="20"/> [Prometheus:](https://prometheus.io/)<br>*Metrics collection and time-series storage.*
- <img src="doc/images/logo/grafana_logo.png" alt="Grafana logo" width="20"/> [Grafana:](https://grafana.com/)<br>*Visualize metrics and build dashboards.*
- <img src="doc/images/logo/loki_logo.png" alt="Loki logo" width="20"/> [Loki:](https://grafana.com/oss/loki/)<br>*Centralized log aggregation and querying.*
- <img src="doc/images/logo/alert_manager_logo.png" alt="Caddy logo" width="20"/> [Alertmanager:](https://prometheus.io/docs/alerting/latest/alertmanager/)<br>*Manage and route monitoring alerts.*
- <img src="doc/images/logo/prometheus_logo.png" alt="Promtail logo" width="20"/> [Promtail:](https://grafana.com/docs/loki/latest/send-data/promtail/)<br>*Collect and forward container logs.*
- <img src="doc/images/logo/caddy_logo.png" alt="Dagster logo" width="20"/> [Caddy:](https://caddyserver.com/)<br>*Secure reverse proxy and gateway.*

**🔗 Orchestration Data Pipelines:**
- <img src="doc/images/logo/dagster_logo.png" alt="PostgreSQL logo" width="20"/> [Dagster:](https://dagster.io/)<br>*Orchestrate and schedule data pipelines.*

**🗄️ Database:**
- <img src="doc/images/logo/postgres_logo.png" alt="MinIO logo" width="20"/> [PostgreSQL:](https://www.postgresql.org/)<br>*Relational database for structured data.*
  
**🪣 Unstructured Data Storage / Datalake**:
- <img src="doc/images/logo/MINIO_logo.png" alt="MLflow logo" width="20"/> [MinIO:](https://min.io/)<br>*S3-compatible object data storage.*

**🤖 Machine Learning Models Registry:**
- <img src="doc/images/logo/mlflow_logo.svg" alt="MLflow logo" width="20"/> [MLflow:](https://mlflow.org/)<br>*Track and manage ML models.*

**⚡ In-Memory, Key-Value, Database:**
- <img src="doc/images/logo/redis_logo.png" alt=" Redis logo" width="20"/> [Redis:](https://redis.io/)<br>*Fast in-memory cache and queue.*

**💬 (Optional) Team Collaboration:**
- <img src="doc/images/logo/mattermost_logo.png" alt="Mattermost logo" width="20"/> [Mattermost:](https://mattermost.com/)<br>*Team chat and collaboration platform.*

---

*examples of services:*<br>
*dagster, pgadmin, minio, mlflow, superset, jupyterlab*
<img src="doc/images/usage/system_collage.png" alt="System architecture collage" />

---

The system is designed to streamline the entire deployment lifecycle, from cloud resource provisioning to application configuration and monitoring, with support for cloud providers, automated server setup, and comprehensive management tools for deployments. 

While the project is intended to run as a proof of concept on a single machine, services can be distributed across multiple machines by adapting the implementation to use <img src="doc/images/logo/docker_swarm_logo.png" alt="Docker Swarm logo" width="20"/> `Docker Swarm` or <img src="doc/images/logo/kubernetes_logo.png" alt="Kubernetes logo" width="20"/> `Kubernetes`.

For demonstration purposes, the system supports deployment on cloud platform <img src="doc/images/logo/azure_logo.svg" alt="Azure logo" width="20"/> Azure.

## 📦 Requirements

*Look at requirements.txt, docker ubuntu

## ⚙️🔨 Installation and Usage

Key features of the deployment system include:
- **Infrastructure as Code**: Automated cloud resource provisioning using Terraform
- **Configuration Management**: Server setup and application deployment using Ansible playbooks
- **Multi-Role Architecture**: Modular deployment with specialized roles for different system components
- **Remote Access**: Built-in support for SSH and remote desktop connectivity
- **Resource Monitoring**: Comprehensive system monitoring for disk, RAM, and CPU usage
- **Service Management**: Automated container orchestration using Docker and Docker Compose

## Data Pipeline example

## 🔧 Configuration

## ✅ Testing

## 💡 Notes

## 🧩 Contributing

## 🏗️ System Architecture

The deployment system follows a layered architecture approach with clear separation of concerns:

**Infrastructure Layer (Terraform):**
- Cloud resource provisioning and management
- Virtual machine creation and networking setup
- Security group and access control configuration

**Configuration Layer (Ansible):**
- Automated server setup and package installation
- Application deployment and service configuration
- Environment-specific variable management

**Application Layer:**
- Containerized service deployment
- Service orchestration and management
- Monitoring and logging integration

The system is built for scalability and maintainability, allowing teams to efficiently manage complex deployments across different environments while maintaining consistency and reliability.