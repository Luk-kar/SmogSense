# Stage 1: Template processor
FROM alpine:3.19 AS processor

ARG LOKI_PORT
ENV LOKI_PORT=${LOKI_PORT}

RUN [ -z "$LOKI_PORT" ] && (echo "ERROR: Build argument LOKI_PORT must be set and non-empty"; exit 1) || true

RUN apk add --no-cache gettext

WORKDIR /build

# Copy the provisioning template
COPY loki.yaml.template .

# Substitute the environment variable at build time
RUN export LOKI_PORT=$LOKI_PORT && \
    envsubst < loki.yaml.template > loki.yaml

# Stage 2: Final Grafana image
FROM grafana/grafana:11.5.1

# Create provisioning directory if it doesn't exist
COPY provisioning/ /etc/grafana/provisioning/

# Copy the processed provisioning file
COPY --from=processor /build/loki.yaml /etc/grafana/provisioning/datasources/loki.yaml