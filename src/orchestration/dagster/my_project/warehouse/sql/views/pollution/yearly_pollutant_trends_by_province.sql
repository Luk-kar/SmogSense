/*
 --------------------------------------------------------------
 -- Analyzes yearly trends of selected air pollutants across 
 -- provinces. The query processes air quality data through 
 -- temporary tables to provide a structured comparison of 
 -- pollution trends.
 --
 -- Steps:
 -- 1) Corrects pollutant formula names (e.g., 'formaldehyde' to 
 --    'CH2O').
 -- 2) Filters pollutants of interest (e.g., PM10, NO2, O3, SO2).
 -- 3) Aggregates yearly pollution data per province, calculating:
 --    - Average pollutant concentration (avg_μg_m3)
 --    - Total number of measurements
 --    - Number of stations contributing data
 -- 4) Retrieves the final dataset for regional air quality analysis.
 --
 -- This output helps assess pollution trends over time at the 
 -- provincial level.
 --------------------------------------------------------------
 */
-- 1) Substitute the mistake in formula
DROP VIEW IF EXISTS yearly_pollutant_trends_by_province;

CREATE VIEW yearly_pollutant_trends_by_province AS WITH temp_pollutants_fixed AS (
    -- 1) Correct the pollutant formula names
    SELECT
        id_indicator,
        name,
        CASE
            WHEN formula = 'formaldehyde' THEN 'CH2O'
            ELSE formula
        END AS formula
    FROM
        air_quality_dim_integrated.indicator
    ORDER BY
        name
),
temp_pollutants_of_interest AS (
    -- 2) Filter the pollutants of interest
    SELECT
        *
    FROM
        temp_pollutants_fixed
    WHERE
        formula IN (
            'PM10',
            'PM2.5',
            'NO2',
            'O3',
            'C6H6',
            'SO2',
            'CH2O',
            'Pb(PM10)',
            'EC(PM2.5)',
            'NO3_(PM2.5)'
        )
    ORDER BY
        name
) -- 3) Aggregate yearly pollution data per province
SELECT
    m.year,
    p.province,
    -- Province name from province table
    i.name AS pollutant_name,
    i.formula,
    AVG(m."avg_μg_m3") AS avg_concentration_μg_m3,
    SUM(m."number_of_measurements") AS number_of_measurements,
    COUNT(m.id_measurement) AS station_count
FROM
    air_quality_dim_annual_statistics.measurement m
    JOIN temp_pollutants_of_interest i ON m.id_indicator = i.id_indicator
    JOIN air_quality_dim_annual_statistics.station s ON m.id_station = s.id_station
    JOIN air_quality_dim_annual_statistics.zone z ON s.id_zone = z.id_zone
    JOIN air_quality_dim_integrated.province p ON z.id_province = p.id_province
GROUP BY
    m.year,
    p.province,
    i.id_indicator,
    i.name,
    i.formula
ORDER BY
    i.name,
    m.year,
    p.province;