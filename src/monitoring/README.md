# dockprom-and-logs

A monitoring solution for Docker hosts and containers with [Prometheus](https://prometheus.io/), [Grafana](http://grafana.org/), [cAdvisor](https://github.com/google/cadvisor),
[NodeExporter](https://github.com/prometheus/node_exporter), [Loki](https://grafana.com/oss/loki/), [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/), and alerting with [AlertManager](https://github.com/prometheus/alertmanager).


This is a fork of the [stefanprodan/dockprom](https://github.com/stefanprodan/dockprom) project with a focus on adding Docker logs functionality through Loki and Promtail integration.

## Key Changes From Original Project

This fork enhances the original dockprom project with the following improvements:

1. **Log Management**: Added Grafana Loki and Promtail for centralized log collection, storage, and visualization
2. **Docker Logs Dashboard**: Created a dedicated Grafana dashboard for Docker container logs
3. **Project Structure**: Reorganized into a more maintainable `src/monitoring/` directory structure
4. **Environment Variables**: Added comprehensive `.env` configuration for easier customization
5. **Improved Deployment**: Enhanced docker-compose configuration with build contexts and healthchecks

## Install

Clone this repository on your Docker host, cd into the directory and run compose up:

```bash
docker compose up -d prometheus loki promtail alertmanager nodeexporter cadvisor grafana pushgateway caddy
```

## Architecture and Components

Containers:

* Prometheus (metrics database) `http://:9090`
* Prometheus-Pushgateway (push acceptor for ephemeral and batch jobs) `http://:9091`
* AlertManager (alerts management) `http://:9093`
* Grafana (visualize metrics and logs) `http://:3000`
* NodeExporter (host metrics collector)
* cAdvisor (containers metrics collector)
* Loki (log aggregation system)
* Promtail (log collector)
* Caddy (reverse proxy and basic auth provider for the components)

**Caddy v2 does not accept plaintext passwords. It MUST be provided as a hash value. The above password hash corresponds to ADMIN_PASSWORD 'admin'. To know how to generate hash password, refer [Updating Caddy to v2](#Updating-Caddy-to-v2)**

Prerequisites:

* Docker Engine >= 1.13
* Docker Compose >= 1.11

## Updating Caddy to v2

Perform a `docker run --rm caddy caddy hash-password --plaintext 'ADMIN_PASSWORD'` in order to generate a hash for your new password.
ENSURE that you replace `ADMIN_PASSWORD` with new plain text password and `ADMIN_PASSWORD_HASH` with the hashed password references in [docker-compose.yml](./docker-compose.yml) for the caddy container.

## Grafana Setup

Navigate to `http://:3000` and login with user ***admin*** password ***admin***. You can change the credentials in the .env file or by supplying the `GRAFANA_ADMIN_USERNAME` and `GRAFANA_ADMIN_PASSWORD` environment variables on compose up.

## Dashboards


### Docker Logs Dashboard

![Logs Dashboard](./screens/Grafana_Docker_Logs.png):

Provides centralized visibility into container log activity, enabling monitoring of log volumes, real-time log streams, and filtering by log level or container for efficient troubleshooting and analysis

* Log volume metrics showing error, warning, and total log counts
* Real-time log viewer with filtering capabilities
* Error and warning log highlighting
* Container-specific log filtering

### Docker Containers Dashboard

![Containers Dashboard](./screens/Grafana_Docker_Containers.png)

Shows key metrics for monitoring running containers:

* Total containers CPU load, memory and storage usage
* Running containers graph, system load graph, IO usage graph
* Container CPU usage graph
* Container memory usage graph
* Container cached memory usage graph
* Container network inbound usage graph
* Container network outbound usage graph

### Docker Host Dashboard

![Host Dashboard](./screens/Grafana_Docker_Host.png)

Monitoring the resource usage of your server:

* Server uptime, CPU idle percent, number of CPU cores, available memory, swap and storage
* System load average graph, running and blocked by IO processes graph, interrupts graph
* CPU usage graph by mode (guest, idle, iowait, irq, nice, softirq, steal, system, user)
* Memory usage graph by distribution (used, free, buffers, cached)
* IO usage graph (read Bps, read Bps and IO time)
* Network usage graph by device (inbound Bps, Outbound Bps)
* Swap usage and activity graphs

### Monitor Services Dashboard

![Monitor Services](./screens/Grafana_Prometheus.png)

Shows key metrics for monitoring the containers that make up the monitoring stack:

* Prometheus container uptime, monitoring stack total memory usage, Prometheus local storage memory chunks and series
* Container CPU usage graph
* Container memory usage graph
* Prometheus chunks to persist and persistence urgency graphs
* Prometheus chunks ops and checkpoint duration graphs
* Prometheus samples ingested rate, target scrapes and scrape duration graphs
* Prometheus HTTP requests graph
* Prometheus alerts graph
* 
## Define alerts

Three alert groups have been setup within the [alert.rules](https://github.com/stefanprodan/dockprom/blob/master/prometheus/alert.rules) configuration file:

* Monitoring services alerts [targets](https://github.com/stefanprodan/dockprom/blob/master/prometheus/alert.rules#L2-L11)
* Docker Host alerts [host](https://github.com/stefanprodan/dockprom/blob/master/prometheus/alert.rules#L13-L40)
* Docker Containers alerts [containers](https://github.com/stefanprodan/dockprom/blob/master/prometheus/alert.rules#L42-L69)

You can modify the alert rules and reload them by making a HTTP POST call to Prometheus:

```bash
curl -X POST http://admin:admin@<host-ip>:9090/-/reload
```

***Monitoring services alerts***

Trigger an alert if any of the monitoring targets (node-exporter and cAdvisor) are down for more than 30 seconds:

```yaml
- alert: monitor_service_down
    expr: up == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "Monitor service non-operational"
      description: "Service {{ $labels.instance }} is down."
```

***Docker Host alerts***

Trigger an alert if the Docker host CPU is under high load for more than 30 seconds:

```yaml
- alert: high_cpu_load
    expr: node_load1 > 1.5
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Server under high load"
      description: "Docker host is under high load, the avg load 1m is at {{ $value}}. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}."
```

Modify the load threshold based on your CPU cores.

Trigger an alert if the Docker host memory is almost full:

```yaml
- alert: high_memory_load
    expr: (sum(node_memory_MemTotal_bytes) - sum(node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes) ) / sum(node_memory_MemTotal_bytes) * 100 > 85
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Server memory is almost full"
      description: "Docker host memory usage is {{ humanize $value}}%. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}."
```

Trigger an alert if the Docker host storage is almost full:

```yaml
- alert: high_storage_load
    expr: (node_filesystem_size_bytes{fstype="aufs"} - node_filesystem_free_bytes{fstype="aufs"}) / node_filesystem_size_bytes{fstype="aufs"}  * 100 > 85
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Server storage is almost full"
      description: "Docker host storage usage is {{ humanize $value}}%. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}."
```

***Docker Containers alerts***


Trigger an alert if a container is using more than 10% of total CPU cores for more than 30 seconds:

```yaml
- alert: jenkins_high_cpu
    expr: sum(rate(container_cpu_usage_seconds_total{name="jenkins"}[1m])) / count(node_cpu_seconds_total{mode="system"}) * 100 > 10
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Jenkins high CPU usage"
      description: "Jenkins CPU usage is {{ humanize $value}}%."
```

Trigger an alert if a container is using more than 1.2GB of RAM for more than 30 seconds:

```yaml
- alert: jenkins_high_memory
    expr: sum(container_memory_usage_bytes{name="jenkins"}) > 1200000000
    for: 30s
    labels:
      severity: warning
    annotations:
      summary: "Jenkins high memory usage"
      description: "Jenkins memory consumption is at {{ humanize $value}}."
```

The AlertManager service handles alerts from Prometheus using [Mattermost's Slack-compatible webhooks](https://developers.mattermost.com/integrate/webhooks/incoming/). To configure:

**Create Webhook in Mattermost:**

- Navigate to **Product Menu > Integrations > Incoming Webhooks**
- Click **Add Incoming Webhook** and copy the generated URL ([official guide](https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/))

**Configure Environment Variables in `.env`:**
```bash
MM_ALERT_CHANNEL_NAME=alerts
MM_WEBHOOK_ID=xxx-generatedkey-xxx  # From webhook URL
```

**Update AlertManager Config with Mattermost settings:**
```yaml
route:
  receiver: "mattermost"
  group_wait: 30s
  group_interval: 5m

receivers:
  - name: "mattermost"
    slack_configs:
      - channel: "${MM_ALERT_CHANNEL_NAME}"
        api_url: "http://mattermost:8065/hooks/${MM_WEBHOOK_ID}"
        title: "[{{ .Status | toUpper }}] {{ .CommonLabels.alertname }}"
        text: |-
          {{ range .Alerts }}
          **Description**: {{ .Annotations.description }}
          **Host**: {{ .Labels.instance }}
          {{ end }}
```

## Setup Alerting with Mattermost Integration

The AlertManager service handles alerts from Prometheus using [Mattermost's Slack-compatible webhooks](https://developers.mattermost.com/integrate/webhooks/incoming/). To configure:

**Create Webhook in Mattermost:**

- Navigate to **Product Menu > Integrations > Incoming Webhooks**
- Click **Add Incoming Webhook** and copy the generated URL ([official guide](https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/))

**Configure Environment Variables in `.env`:**
```bash
MM_ALERT_CHANNEL_NAME=alerts
MM_WEBHOOK_ID=xxx-generatedkey-xxx  # From webhook URL
```

**Update AlertManager Config with Mattermost settings:**
```yaml
route:
  receiver: "mattermost"
  group_wait: 30s
  group_interval: 5m

receivers:
  - name: "mattermost"
    slack_configs:
      - channel: "${MM_ALERT_CHANNEL_NAME}"
        api_url: "http://mattermost:8065/hooks/${MM_WEBHOOK_ID}"
        title: "[{{ .Status | toUpper }}] {{ .CommonLabels.alertname }}"
        text: |-
          {{ range .Alerts }}
          **Description**: {{ .Annotations.description }}
          **Host**: {{ .Labels.instance }}
          {{ end }}
```

[Webhook URLs](https://developers.mattermost.com/integrate/webhooks/incoming/) contain sensitive credentials-treat as secrets. Channel names must use hyphens instead of spaces (e.g. `#prod-alerts`).

---

![Slack Notifications](https://raw.githubusercontent.com/stefanprodan/dockprom/master/screens/Slack_Notifications.png)

## Sending metrics to the Pushgateway

The [pushgateway](https://github.com/prometheus/pushgateway) is used to collect data from batch jobs or from services.

To push data, simply execute:

```bash
echo "some_metric 3.14" | curl --data-binary @- http://user:password@localhost:9091/metrics/job/some_job
```

Please replace the `user:password` part with your user and password set in the initial configuration (default: `admin:admin`).

## Updating Grafana to v5.2.2

[In Grafana versions >= 5.1 the id of the grafana user has been changed](http://docs.grafana.org/installation/docker/#migration-from-a-previous-version-of-the-docker-container-to-5-1-or-later). Unfortunately this means that files created prior to 5.1 won’t have the correct permissions for later versions.

| Version |   User  | User ID |
|:-------:|:-------:|:-------:|
|  < 5.1  | grafana |   104   |
|  \>= 5.1 | grafana |   472   |

There are two possible solutions to this problem.

1. Change ownership from 104 to 472
2. Start the upgraded container as user 104

## Specifying a user in docker-compose.yml

To change ownership of the files run your grafana container as root and modify the permissions.

First perform a `docker-compose down` then modify your docker-compose.yml to include the `user: root` option:

```yaml
  grafana:
    image: grafana/grafana:5.2.2
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/datasources:/etc/grafana/datasources
      - ./grafana/dashboards:/etc/grafana/dashboards
      - ./grafana/setup.sh:/setup.sh
    entrypoint: /setup.sh
    user: root
    environment:
      - GF_SECURITY_ADMIN_USER=${ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    expose:
      - 3000
    networks:
      - monitor-net
    labels:
      org.label-schema.group: "monitoring"
```

Perform a `docker compose up -d` and then issue the following commands:

```bash
docker exec -it --user root grafana bash

# in the container you just started:
chown -R root:root /etc/grafana && \
chmod -R a+r /etc/grafana && \
chown -R grafana:grafana /var/lib/grafana && \
chown -R grafana:grafana /usr/share/grafana
```

To run the grafana container as `user: 104` change your `docker-compose.yml` like such:

```yaml
  grafana:
    container_name: monitoring-grafana
    labels:
      - "type=monitoring,visualization,dashboards,observability"
    build:
      context: ./src/monitoring/grafana
      dockerfile: Dockerfile
      args:
        - LOKI_PORT=${LOKI_PORT}
    volumes:
      - grafana_data:/var/lib/grafana
    entrypoint: /setup.sh
    user: "104"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USERNAME}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=${GRAFANA_ALLOW_SIGNUP}
      - PROMETHEUS_PORT=${PROMETHEUS_PORT}
    restart: ${RESTART_POLICY}
    expose:
      - ${GRAFANA_PORT}
    networks:
      - monitor-net
```
