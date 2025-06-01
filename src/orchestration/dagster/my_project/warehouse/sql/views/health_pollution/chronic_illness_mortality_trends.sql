/*
 --------------------------------------------------------------
 -- Analyzes mortality trends for chronic illnesses over multiple 
 -- years. The query aggregates total deaths per illness and year, 
 -- enabling trend analysis over time.
 --
 -- Steps:
 -- 1) Aggregates mortality data by illness and year.
 -- 2) Joins aggregated data with illness names for clarity.
 -- 3) Orders results chronologically to observe increases or 
 --    decreases in mortality rates for specific illnesses.
 --
 -- This output helps identify long-term trends in chronic illness 
 -- mortality.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS chronic_illness_mortality_trends;

CREATE VIEW chronic_illness_mortality_trends AS WITH aggregated_measurements AS (
    SELECT
        id_illness,
        year,
        SUM(deaths) AS total_deaths
    FROM
        health_dim.measurement
    GROUP BY
        id_illness,
        year
)
SELECT
    di.illness,
    am.year,
    am.total_deaths
FROM
    health_dim.death_illness di
    JOIN aggregated_measurements am ON di.id_illness = am.id_illness
ORDER BY
    di.illness,
    am.year;