/*
 --------------------------------------------------------------
 -- Analyzes median annual pollutant concentrations and total 
 -- deaths by province and year. The query combines air quality 
 -- and health mortality data, calculating the median pollutant 
 -- level using `PERCENTILE_CONT(0.5)` for robustness against 
 -- outliers. Deaths are aggregated per province and year, and 
 -- results are enriched with deaths per 100,000 population.
 --
 -- Steps:
 -- 1) Filters air quality data to exclude null measurements.
 -- 2) Aggregates health mortality data by province and year.
 -- 3) Joins air quality and health data, calculating median 
 --    pollutant levels and deaths per 100,000 population.
 -- 4) Groups results by year, province, and pollutant, ordered 
 --    chronologically for trend analysis.
 --
 -- This output supports environmental and public health analysis
 -- by linking pollution levels to mortality trends.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS median_pollutant_levels_and_deaths_by_province_year;

CREATE VIEW median_pollutant_levels_and_deaths_by_province_year AS WITH air_quality_data AS (
    SELECT
        aqm.year,
        aqm.id_station,
        aqm.id_indicator,
        aqm."avg_μg_m3"
    FROM
        air_quality_dim_annual_statistics.measurement aqm
    WHERE
        aqm."avg_μg_m3" IS NOT NULL
),
health_data AS (
    SELECT
        hm.year,
        hm.id_province,
        SUM(hm.deaths) AS total_deaths
    FROM
        health_dim.measurement hm
    GROUP BY
        hm.year,
        hm.id_province
)
SELECT
    aq.year,
    prov.province AS province_name,
    ind.name AS pollutant_name,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY
            aq."avg_μg_m3"
    ) AS median_pollutant_level_ug_m3,
    hd.total_deaths,
    ROUND(
        (
            hd.total_deaths :: NUMERIC / hp.people_total * 100000
        ),
        2
    ) AS deaths_per_100k
FROM
    air_quality_data aq
    JOIN air_quality_dim_annual_statistics.station st ON aq.id_station = st.id_station
    JOIN air_quality_dim_annual_statistics.zone z ON st.id_zone = z.id_zone
    JOIN air_quality_dim_integrated.province prov ON z.id_province = prov.id_province
    JOIN air_quality_dim_integrated.indicator ind ON aq.id_indicator = ind.id_indicator
    JOIN health_data hd ON prov.id_province = hd.id_province
    AND aq.year = hd.year
    JOIN health_dim.country_population hp ON aq.year = hp.year
GROUP BY
    aq.year,
    prov.province,
    ind.name,
    hd.total_deaths,
    deaths_per_100k
ORDER BY
    aq.year,
    prov.province,
    ind.name;