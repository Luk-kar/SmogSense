/*
 --------------------------------------------------------------
 -- Retrieves pollutant concentrations and geographical data for 
 -- mapping and spatial analysis. The query joins pollutant, 
 -- measurement, and geometry tables to provide a comprehensive 
 -- dataset for visualization.
 --
 -- Steps:
 -- 1) Joins pollutant names with measurement values.
 -- 2) Links measurements to geographical coordinates.
 -- 3) Retrieves all records for further spatial analysis.
 --
 -- This output enables the creation of pollution concentration 
 -- maps.
 --------------------------------------------------------------
 */
DROP VIEW IF EXISTS pollutant_concentration_map;

CREATE VIEW pollutant_concentration_map AS
SELECT
    p.pollutant_name,
    g.value,
    g.geometry
FROM
    air_quality_dim_map_pollutant.geometry AS g
    JOIN air_quality_dim_map_pollutant.measurement AS m ON g.id_measurement = m.id_measurement
    JOIN air_quality_dim_map_pollutant.pollutant AS p ON m.id_pollutant = p.id_pollutant;