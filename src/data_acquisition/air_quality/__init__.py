"""
air quality data from GIOS API:
https://powietrze.gios.gov.pl/pjp/content/api
https://api.gios.gov.pl/pjp-api/swagger-ui/#/

Sensors' data updated:
    yearly:
        - measurement stations and measurement sites
        - annual statistics
        - maps of pollutant concentration distributions
    daily:
        - measurement aggregates
    hourly:
        - current measurement data
        - air quality index
        - exceedance information
"""

from src.data_acquisition.air_quality.gios_api.current import (
    fetch_current_measurement_data,
    fetch_air_quality_index,
    fetch_exceedance_information,
)

from src.data_acquisition.air_quality.gios_api.aggregate import (
    fetch_measurement_aggregates,
)

from src.data_acquisition.air_quality.gios_api.annual import (
    fetch_station_data,
    fetch_sensor_data,
    fetch_annual_statistics,
    fetch_map_pollutant_concentration_distribution,
)

from src.data_acquisition.air_quality.gios_api.all_data_fetchers import (
    fetch_sensor_data_all,
    fetch_current_measurement_data_all,
    fetch_fetch_air_quality_index_all,
    fetch_map_pollutants_all,
    fetch_annual_statistics_all,
)
