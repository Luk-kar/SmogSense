#!/bin/sh

if [ -z "$PROMETHEUS_RETENTION_TIME" ]; then
  echo "❌ Critical error: PROMETHEUS_RETENTION_TIME must be set in .env file" >&2
  echo "   or provided via runtime (-e PROMETHEUS_RETENTION_TIME=...)." >&2
  exit 1
fi

# Use default retention if .env value not found
RETENTION="${PROMETHEUS_RETENTION_TIME}"

# 3. Proceed with validated value
echo "✅ Set data retention time: ${RETENTION}"

exec /bin/prometheus \
  "--config.file=/etc/prometheus/prometheus.yml" \
  "--storage.tsdb.path=/prometheus" \
  "--web.console.libraries=/usr/share/prometheus/console_libraries" \
  "--web.console.templates=/usr/share/prometheus/consoles" \
  "--storage.tsdb.retention.time=${RETENTION}" \
  "--web.enable-lifecycle"
