# 🌫️🔧 SmogSense

A modular `data platform` integrating for `end-to-end analytics`, `data pipelines` orchestration, `machine learning models registry` and observability in local open-source environments.<br>

The example setup for the commercial cloud is here:<br>[./server_deployment/README](./server_deployment/README)

Each service is deployed via <img src="doc/images/logo/docker_logo.png" alt="Docker logo" width="20"/> [`docker`](https://www.docker.com/):

**📊 Analytics:**
- <img src="doc/images/logo/postgres_logo.png" alt="pgAdmin logo" width="20"/> [pgAdmin:](https://www.pgadmin.org)<br>*PostgreSQL database web management tool.*<br>[*`http://localhost:5050`*](http://localhost:5050)
- <img src="doc/images/logo/superset_logo.png" alt="Superset logo" width="20"/> [Superset:](https://superset.apache.org)<br>*Data visualization and dashboarding platform.*<br>[*`http://localhost:8090`*](http://localhost:8090)
*

**🧪 Data Science:**
- <img src="doc/images/logo/jupyterlab_logo.png" alt="JupyterLab logo" width="20"/> [JupyterLab:](https://jupyter.org)<br>*Interactive data analysis notebooks.*<br>[*`http://localhost:8888`*](http://localhost:8888)


**📈 Monitoring Resources:**<br>
*[Documentation](https://github.com/Luk-kar/dockprom-and-logs)*
- <img src="doc/images/logo/grafana_logo.png" alt="Grafana logo" width="20"/> [Grafana:](https://grafana.com/)<br>*Visualize metrics and build dashboards.*<br>[*`http://localhost:3000`*](http://localhost:3000)

- <img src="doc/images/logo/prometheus_logo.png" alt="Prometheus logo" width="20"/> [Prometheus:](https://prometheus.io/)<br>*Metrics collection and time-series storage.*<br>
- <img src="doc/images/logo/loki_logo.png" alt="Loki logo" width="20"/> [Loki:](https://grafana.com/oss/loki/)<br>*Centralized log aggregation and querying.*<br>
- <img src="doc/images/logo/alert_manager_logo.png" alt="Caddy logo" width="20"/> [Alertmanager:](https://prometheus.io/docs/alerting/latest/alertmanager/)<br>*Manage and route monitoring alerts.*<br>
- <img src="doc/images/logo/prometheus_logo.png" alt="Promtail logo" width="20"/> [Promtail:](https://grafana.com/docs/loki/latest/send-data/promtail/)<br>*Collect and forward container logs.*<br>
- <img src="doc/images/logo/caddy_logo.png" alt="Dagster logo" width="20"/> [Caddy:](https://caddyserver.com/)<br>*Secure reverse proxy and gateway.*<br>

**🔗 Orchestration Data Pipelines:**
- <img src="doc/images/logo/dagster_logo.png" alt="PostgreSQL logo" width="20"/> [Dagster:](https://dagster.io/)<br>*Orchestrate and schedule data pipelines.*<br>[*`http://localhost:5000`*](http://localhost:5000)

**🗄️ Database:**
- <img src="doc/images/logo/postgres_logo.png" alt="MinIO logo" width="20"/> [PostgreSQL:](https://www.postgresql.org/)<br>*Relational database for structured data.*<br>*`via client, not web: localhost:5432`*
  
**🪣 Unstructured Data Storage / Datalake**:
- <img src="doc/images/logo/MINIO_logo.png" alt="MLflow logo" width="20"/> [MinIO:](https://min.io/)<br>*S3-compatible object data storage.*<br>
  - *API: `http://localhost:9000`*
  - *Web: [`http://localhost:9001`](http://localhost:9001)*
  
**🤖 Machine Learning Models Registry:**
- <img src="doc/images/logo/mlflow_logo.svg" alt="MLflow logo" width="20"/> [MLflow:](https://mlflow.org/)<br>*Track and manage ML models.*<br>[*`http://localhost:5005`*](http://localhost:5005)

**⚡ In-Memory, Key-Value, Database:**
- <img src="doc/images/logo/redis_logo.png" alt=" Redis logo" width="20"/> [Redis:](https://redis.io/)<br>*Fast in-memory cache and queue.*<br>

**💬 (Optional) Team Collaboration:**
- <img src="doc/images/logo/mattermost_logo.png" alt="Mattermost logo" width="20"/> [Mattermost:](https://mattermost.com/)<br>*Team chat and collaboration platform.*<br>[*`http://localhost:8065`*](http://localhost:8065)

---

<img src="doc/images/usage/system_collage.png" alt="System architecture collage" />

*e.g. of the most important services:<br>dagster, superset, pgadmin, minio, mlflow, jupyterlab:*

---
For cloud deployments, the system is provisioned and configured using <img src="doc/images/logo/terraform_logo.png" alt="terraform logo" width="20"/> Terraform (`infrastructure as code`) and <img src="doc/images/logo/ansible_logo.svg" alt="terraform logo" width="20"/> Ansible (`configuration management automation`) to automate virtual machine setup, service installation, and network security on <img src="doc/images/logo/azure_logo.svg" alt="Azure logo" width="20"/> `Azure` cloud.

While the project is intended to run as a proof of concept on a single machine, services can be distributed across multiple machines by adapting the implementation to use <img src="doc/images/logo/docker_swarm_logo.png" alt="Docker Swarm logo" width="20"/> `Docker Swarm` or <img src="doc/images/logo/kubernetes_logo.png" alt="Kubernetes logo" width="20"/> `Kubernetes`.


## 📦 Requirements

For services deployment:
- <img src="doc/images/logo/docker_logo.png" alt="Docker logo" width="20"/>  [`docker-compose.yml`](docker-compose.yml)
  
For cloud deployment:
- <img src="doc/images/logo/terraform_logo.png" alt="terraform logo" width="20"/> `Terraform`
- <img src="doc/images/logo/ansible_logo.svg" alt="terraform logo" width="20"/>  `Ansible`
- <img src="doc/images/logo/azure_logo.svg" alt="Azure logo" width="20"/> `Azure` *(account or any other provider)*

Project's scripts were run on <img src="doc/images/logo/ubuntu_logo.svg" alt="Ubuntu logo" width="20"/> [`Ubuntu`](https://ubuntu.com/) <img src="doc/images/logo/linux_logo.svg" alt="Linux logo" width="20"/> [`Linux`](https://www.youtube.com/watch?v=rrB13utjYV4)

## ⚙️🔨 Installation and Usage

**A.** For 🖥️ local use:<br>
   1. **Clone the repository**
       ```bash
       git clone hhttps://github.com/Luk-kar/SmogSense.git
       cd SmogSense
       ```

   2. **Configure environment variables**  
      Copy the example file and edit it with your credentials and model settings: 
      ```bash
      cp .env.example .env
      # Open .env in your editor and adjust passwords, users or ports etc.
      ```
   3. **Start services with Docker Compose**  
      ```bash
      docker-compose up --build -d
      ```
  - <img src="doc/images/logo/postgres_logo.png" alt="PostgreSQL logo" width="20"/> **PostgreSQL** will initialize the specified databases.
  - <img src="doc/images/logo/postgres_logo.png" alt="pgAdmin logo" width="20"/> **pgAdmin** will be available for database management.
  - <img src="doc/images/logo/MINIO_logo.png" alt="MinIO logo" width="20"/> **MinIO** will serve as S3-compatible object storage.
  - <img src="doc/images/logo/superset_logo.png" alt="Superset logo" width="20"/> **Superset** will be available for data visualization.
  - <img src="doc/images/logo/jupyterlab_logo.png" alt="JupyterLab logo" width="20"/> **JupyterLab** will be available for interactive notebooks.
  - <img src="doc/images/logo/mlflow_logo.svg" alt="MLflow logo" width="20"/> **MLflow** will be available for model management.
  - <img src="doc/images/logo/redis_logo.png" alt="Redis logo" width="20"/> **Redis** will be available for caching and queues.
  - <img src="doc/images/logo/dagster_logo.png" alt="Dagster logo" width="20"/> **Dagster** will orchestrate data pipelines.
  - <img src="doc/images/logo/grafana_logo.png" alt="Grafana logo" width="20"/> <img src="doc/images/logo/prometheus_logo.png" alt="Prometheus logo" width="20"/> <img src="doc/images/logo/loki_logo.png" alt="Loki logo" width="20"/> <img src="doc/images/logo/alert_manager_logo.png" alt="Alertmanager logo" width="20"/> <img src="doc/images/logo/prometheus_logo.png" alt="Promtail logo" width="20"/> **Monitoring stack** (Prometheus, Grafana, Loki, Alertmanager, Promtail, cAdvisor, Node Exporter, Pushgateway, Caddy) will be available for observability.
  - <img src="doc/images/logo/mattermost_logo.png" alt="Mattermost logo" width="20"/> **(Optional) Mattermost** will be available for team collaboration.

      ---
      
      Not all services have to be run at once, for example to run only dagster warehouse pipeline you run:
      ```
      docker compose up dagster_code_warehouse dagster_daemon dagster_webserver
      ```

   4. **Verify everything is running**  
      ```bash
      docker ps
      # You should see:
       # smogsense_postgres, smogsense_pgadmin, smogsense_minio... etc
      ```

   5. **Access the application**  
      Open your browser and navigate to  <img src="doc/images/logo/dagster_logo.png" alt="PostgreSQL logo" width="20"/> `Dagster` webserver:  
      ```
      http://localhost:5000
      ```
       And run the example tasks:
       - `upload_example_project_data_to_minio`
       - `restore_example_project_database`
   6. **Stop all services**
      ```bash
      docker compose stop
      ```
   7. **Remove all services from the machine**
      ```bash
      docker compose down
      ```
      **B.** For ☁️ cloud use:<br>
      [server_deployment/README.md](server_deployment/README.md)

## <img src="doc/images/logo/dagster_logo.png" alt="PostgreSQL logo" width="25"/> Data Pipeline

### 🌐 Data Sources

- [**GIOS API:**]((https://powietrze.gios.gov.pl/pjp/content/api)) Air quality data (stations, measurements, air quality index)
- [**Statistical API (GUS BDL):**]((https://bdl.stat.gov.pl/bdl/start)) Health and demographic statistics
- [**Custom JSON endpoint:**](https://gist.githubusercontent.com/Luk-kar/3aefd3f77d288ada85b5f44422b711d8/raw/b0793391ab0478e0d92052d204e7af493a7ecc92/poland_woj.json) Geospatial data for provinces
- [**Twitter (X) API:**](https://twikit.readthedocs.io/en/latest/twikit.html) Social media data (limited by rate and access policies)
  
### 🔄 Pipelines services

![data flow](./doc/images/dagster_pipelines/data_flow.png)

### ✅ Tests

Most assets include automated tests. The Dagster's [checks](https://dagster.io/blog/dagster-asset-checks) that execute after each task completes, ensuring data quality and pipeline reliability.

For examples, see the validation logic in:  
**[air_quality/assets/annual_statistics/validations](src/orchestration/dagster/my_project/air_quality/assets/annual_statistics/validations)**

### 🏗️ Dagster services setup

[**README**](src/orchestration/dagster/README)

## 🔧 Configuration

All settings are loaded from the [`.env`](.env.example) file, which contains environment variables organized by service.<br><br>⚠️ **Important security considerations**:
- **Production warning**: Avoid storing sensitive data in environment variables. Use a dedicated secrets management system instead.
- **Security tags**:
  - `#SECRECTS`: Variables requiring secure handling (passwords, API keys)
  - `#WARNING`: Critical configuration needing attention

## ✅ Testing
Testing is automated using shell scripts and Python modules, with dedicated test suites for data acquisition features such as `air quality` and `health data`. 

Test files are organized by functionality, and you can run all tests at once or target specific modules using the provided scripts.

```sh
tests/run_tests_data_air_quality.sh
```
## 💡 Notes

TODO

## 🧩 Possible Further Development

Integrate <img src="doc/images/logo/jenkins_logo.png" alt="Jenkins logo" width="15"/> [Jenkins](https://www.jenkins.io/) to automate the building, testing, and deployment of data pipelines as part of a CI/CD (Continuous Integration and Continuous Deployment) workflow.

**Key Benefits and Features:**

- **Automated Testing:** Jenkins can automatically trigger test suites whenever code changes are committed, ensuring consistent and rapid feedback on pipeline quality.
- **Pipeline Orchestration:** Define complex workflows using Jenkins Pipelines (written as code in a `Jenkinsfile`), enabling repeatable and version-controlled automation of build, test, and deployment steps.
- **Reporting and Notifications:** Generate detailed test reports, visualize trends, and send alerts (via email, Mattermost/Slack, etc.) for build or test failures.
- **Integration Flexibility:** Leverage thousands of plugins to connect with source control (GitHub, Bitbucket), testing frameworks (unittest), containerization tools (Docker, Kubernetes), and collaboration platforms.

**Example Workflow:**

1. **Code Commit:** Developer pushes changes to the repository.
2. **Trigger Build:** Jenkins detects the change and checks out the latest code.
3. **Run Tests:** Jenkins executes automated tests for the data pipelines.
4. **Report Results:** Test results and logs are displayed and archived.
5. **Deploy:** If tests pass, Jenkins can automatically deploy updated pipelines to development or production environments.

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.