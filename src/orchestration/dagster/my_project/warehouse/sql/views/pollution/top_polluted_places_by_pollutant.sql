/*
 --------------------------------------------------------------
 -- Identifies the most polluted locations for key pollutants 
 -- (PM10, PM2.5, NO2) in the latest common year. The query 
 -- follows these steps:
 --
 -- 1) Determines the latest year with data for all pollutants.
 -- 2) Extracts pollution data for that year, linking measurements 
 --    to places and zones.
 -- 3) Identifies the highest pollution levels per pollutant and 
 --    zone type, selecting the top 100 most polluted locations.
 -- 4) Enriches results with pollutant names and zone details.
 --
 -- This output ranks the worst air pollution hotspots.
 --------------------------------------------------------------
 */
-- Step 1: Store the available years for each pollutant
DROP TABLE IF EXISTS temp_pollutant_years;

CREATE VIEW top_polluted_places_by_pollutant AS WITH temp_pollutant_years AS (
    -- Step 1: Determine the available years for each pollutant
    SELECT
        i.formula AS pollutant_name,
        m.year
    FROM
        air_quality_dim_annual_statistics.measurement m
        JOIN air_quality_dim_integrated.indicator i ON m.id_indicator = i.id_indicator
    WHERE
        i.formula IN ('PM10', 'PM2.5', 'NO2')
        AND m.avg_μg_m3 IS NOT NULL
    GROUP BY
        i.formula,
        m.year
),
temp_last_year AS (
    -- Step 2: Find the common maximum year with data for all pollutants
    SELECT
        year AS max_year
    FROM
        temp_pollutant_years
    GROUP BY
        year
    HAVING
        COUNT(DISTINCT pollutant_name) = 3 -- Ensure the year exists for all 3 pollutants
    ORDER BY
        year DESC
    LIMIT
        1
), temp_city_pollutant_stats AS (
    SELECT
        m.id_indicator,
        m.avg_μg_m3,
        m.id_station,
        z.id_zone,
        zt.id_zone_type
    FROM
        air_quality_dim_annual_statistics.measurement AS m
        LEFT JOIN air_quality_dim_annual_statistics.station AS s ON m.id_station = s.id_station
        LEFT JOIN air_quality_dim_annual_statistics.zone AS z ON s.id_zone = z.id_zone
        LEFT JOIN air_quality_dim_annual_statistics.zone_type AS zt ON z.id_zone_type = zt.id_zone_type
        LEFT JOIN air_quality_dim_integrated.indicator i ON m.id_indicator = i.id_indicator
    WHERE
        m.year = (
            SELECT
                max_year
            FROM
                temp_last_year
        )
        AND m.avg_μg_m3 IS NOT NULL
        AND i.formula IN ('PM10', 'PM2.5', 'NO2')
),
RankedPollutants AS (
    -- Step 4: Rank locations per pollutant based on maximum pollution levels
    SELECT
        id_indicator,
        id_zone,
        id_zone_type,
        MAX(avg_μg_m3) AS max_avg_μg_m3,
        ROW_NUMBER() OVER (
            PARTITION BY id_indicator
            ORDER BY
                MAX(avg_μg_m3) DESC
        ) AS rank
    FROM
        temp_city_pollutant_stats
    GROUP BY
        id_indicator,
        id_zone,
        id_zone_type
),
temp_max_100_pollutant_stats AS (
    -- Step 5: Select the top 100 locations per pollutant
    SELECT
        id_indicator,
        id_zone,
        id_zone_type,
        max_avg_μg_m3
    FROM
        RankedPollutants
    WHERE
        rank <= 100
    ORDER BY
        id_indicator,
        max_avg_μg_m3 DESC
) -- Final output: Enrich results with pollutant and zone details
SELECT
    i.formula,
    i.name AS pollutant_name,
    z.zone_name,
    zt.zone_type,
    max_avg_μg_m3
FROM
    temp_max_100_pollutant_stats m
    JOIN air_quality_dim_integrated.indicator i ON m.id_indicator = i.id_indicator
    JOIN air_quality_dim_annual_statistics.zone z ON m.id_zone = z.id_zone
    JOIN air_quality_dim_annual_statistics.zone_type zt ON z.id_zone_type = zt.id_zone_type
ORDER BY
    i.formula,
    max_avg_μg_m3 DESC;