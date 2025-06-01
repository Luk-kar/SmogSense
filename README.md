# SmogSense

## Development

### Useful commands:
```
docker exec -it smogsense_dagster_user_code /bin/bash
```
```
docker exec -it smogsense_postgres psql -U postgres -d smogsense
DROP SCHEMA air_quality_dim_station CASCADE;
DROP SCHEMA air_quality_dim_annual_statistics CASCADE;
SELECT COUNT(*) FROM air_quality_dimensions.province; SELECT COUNT(*) FROM air_quality_dimensions.area; SELECT COUNT(*) FROM air_quality_dimensions.location; SELECT COUNT(*) FROM air_quality_dimensions.station;
DROP SCHEMA social_media CASCADE;

```

```
DROP TABLE air_quality_dim_sensor.indicator;
DROP TABLE air_quality_dim_sensor.sensor;
DROP TABLE air_quality_dim_annual_statistics.indicator;
DROP TABLE air_quality_dim_annual_statistics.measurement;

DROP TABLE air_quality_dim_integrated.indicator;
```

```
SELECT * FROM air_quality_dim_integrated.indicator;
SELECT * FROM social_media_dim.bounding_box;
\d+ air_quality_dim_integrated.indicator;
```
```
ALTER TABLE air_quality_dim_map_pollutant.pollutants
DROP CONSTRAINT fk_id_indicator;
```
```
tree "src/orchestration/dagster" > structure.txt
```
```
docker compose build dagster_daemon dagster_webserver
docker compose up dagster_code_air_quality dagster_daemon dagster_webserver
docker compose up dagster_code_health dagster_daemon dagster_webserver
docker compose up dagster_code_social_media dagster_daemon dagster_webserver
docker compose up dagster_code_warehouse dagster_daemon dagster_webserver
docker compose stop
```
```
docker compose down dagster_code_health && docker compose build dagster_code_health && docker compose up dagster_code_health
docker compose down dagster_code_air_quality && docker compose build dagster_code_air_quality && docker compose up dagster_code_air_quality
docker compose down dagster_code_social_media && docker compose build dagster_code_social_media && docker compose up dagster_code_social_media
docker compose down dagster_code_warehouse && docker compose build dagster_code_warehouse && docker compose up dagster_code_warehouse
docker compose down dagster_code_territory && docker compose build dagster_code_territory && docker compose up dagster_code_territory
dagster_code_territory
```
```
docker compose down
```
```
docker compose up dagster_user_code dagster_webserver dagster_daemon
docker compose up dagster_code_social_media dagster_daemon dagster_webserver
```
### Useful paths:
Path for temporary storage
```
/tmp/dagster_storage/
```

