FROM alpine:latest AS processor

# Declare mandatory build arguments
ARG PROMETHEUS_MONITOR_LABEL
ARG NODE_EXPORTER_PORT
ARG CADVISOR_PORT
ARG PROMETHEUS_PORT
ARG PUSHGATEWAY_PORT
ARG ALERTMANAGER_PORT
ARG NGINX_EXPORTER_PORT
ARG EVENT_LOG_PORT
ARG PROMETHEUS_RETENTION_TIME

# Validate arguments at build time
RUN for arg in \
    PROMETHEUS_MONITOR_LABEL \
    NODE_EXPORTER_PORT \
    CADVISOR_PORT \
    PROMETHEUS_PORT \
    PUSHGATEWAY_PORT \
    ALERTMANAGER_PORT \
    NGINX_EXPORTER_PORT \
    EVENT_LOG_PORT \
    PROMETHEUS_RETENTION_TIME; \
    do \
    eval "value=\$$arg"; \
    if [ -z "$value" ]; then \
    echo "ERROR: Build argument $arg must be set and non-empty"; \
    exit 1; \
    fi; \
    done

# Convert ARGs to ENV variables
ENV PROMETHEUS_MONITOR_LABEL=$PROMETHEUS_MONITOR_LABEL \
    NODE_EXPORTER_PORT=$NODE_EXPORTER_PORT \
    CADVISOR_PORT=$CADVISOR_PORT \
    PROMETHEUS_PORT=$PROMETHEUS_PORT \
    PUSHGATEWAY_PORT=$PUSHGATEWAY_PORT \
    ALERTMANAGER_PORT=$ALERTMANAGER_PORT \
    NGINX_EXPORTER_PORT=$NGINX_EXPORTER_PORT \
    EVENT_LOG_PORT=$EVENT_LOG_PORT \
    PROMETHEUS_RETENTION_TIME=$PROMETHEUS_RETENTION_TIME

# Install essential utilities
RUN apk add --no-cache gettext

# Set working directory
WORKDIR /config

# Copy configuration files
COPY prometheus.yml.template ./

# Process template using build arguments
RUN envsubst < prometheus.yml.template > prometheus.yml

# Stage 2: Official Prometheus image
FROM prom/prometheus:v3.1.0

# Copy processed configuration
COPY --from=processor /config/prometheus.yml /etc/prometheus/
# As an empty placeholder if not then error
RUN touch /etc/prometheus/.env
COPY entrypoint.sh /entrypoint.sh
COPY config/ ./

# Set permissions
USER root
RUN chmod +x /entrypoint.sh
USER nobody

# Use JSON-safe CMD
CMD ["/entrypoint.sh"]