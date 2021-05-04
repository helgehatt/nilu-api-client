from typing import Iterable

import pandas as pd
import requests


class NILUClient:
    """
    API client for interacting with NILU.

    See https://api.nilu.no/ for more information.
    """

    def __init__(self):
        self.base_url = "https://api.nilu.no/"

    def _get_url(self, url: str, **query_parameters):
        response = requests.get(f"{self.base_url}{url}?{_stringify(**query_parameters)}")
        response.raise_for_status()
        return pd.DataFrame.from_records(response.json())

    def get_areas(self):
        """
        Returns all available areas.
        """
        return self._get_url("lookup/areas")

    def get_stations(
        self,
        area: str = None,
        utd: bool = None,
    ):
        """
        Returns metadata for all stations.

        ----------
        Parameters
        - `area: str`

        If specified, only stations within the given area are returned.

        - `utd: bool`

        If `True`, only stations with new data are returned.

        """
        return self._get_url("lookup/stations", area=area, utd=utd)

    def get_components(self):
        """
        Returns all available components.
        """
        return self._get_url("lookup/components")

    def get_air_quality_index(
        self,
        component: str = None,
        culture: str = None,
    ):
        """
        Returns an air quality index per component.

        ----------
        Parameters
        - `component: str`

        If specified, only the air quality index for that component is returned.

        - `culture: str`

        Set to `en` to return descriptions in English.

        """
        return _flatten_column(
            self._get_url(
                "lookup/aqis",
                component=component,
                culture=culture,
            ),
            "aqis",
        )

    def get_timeseries(
        self,
        station: str = None,
        component: str = None,
        timestep: int = None,
    ):
        """
        Returns all available time series.

        ----------
        Parameters
        - `station: str`

        If specified, only time series for that station are returned.

        - `component: str`

        If specified, only time series for that component are returned.

        - `timestep: int`

        If specified, only time series for that timestep are returned.

        """
        return self._get_url(
            "lookup/timeseries",
            station=station,
            component=component,
            timestep=timestep,
        )

    def get_observations(
        self,
        fromtime,
        totime,
        station: str = "all",
        components: Iterable[str] = None,
        showinvalid: bool = None,
    ):
        """
        Returns all observations within the given time period.

        ----------
        Parameters
        - `fromtime: date-like`

        Specifies the start of the time interval.

        - `totime: date-like`

        Specifies the end of the time interval

        - `station: str`

        If specified, only observations for that station are returned. Default is `all`.

        - `components: Iterable[str]`

        If specified, only observations for the given components are returned.

        - `showinvalid: bool`

        If `True`, invalid values are return as `None`.

        """
        fromtime = pd.to_datetime(fromtime).strftime("%Y-%m-%d")
        totime = pd.to_datetime(totime).strftime("%Y-%m-%d")

        if components is not None:
            components = ";".join(components)

        return _flatten_column(
            self._get_url(
                f"obs/historical/{fromtime}/{totime}/{station}",
                components=components,
                showinvalid=showinvalid,
            ),
            "values",
        )


def _stringify(**parameters):
    """Converts query parameters to a query string."""
    return "&".join([f"{k}={v}" for k, v in parameters.items() if v is not None])


def _flatten_column(df: pd.DataFrame, column: str):
    """Flattens a DataFrame column of dicts or lists of dicts."""
    try:
        df = df.explode(column, ignore_index=True)
    except KeyError:
        pass  # Raises KeyError if column does not consist of lists
    return pd.concat(
        (df.drop(column, axis="columns"), pd.DataFrame.from_records(df[column])),
        axis="columns",
    )


if __name__ == "__main__":
    client = NILUClient()
    client.get_areas()
    client.get_stations(area="bergen")
    client.get_components()
    client.get_timeseries(station="Danmarks plass")
    client.get_air_quality_index()
    client.get_observations("2021-05-01", "2021-05-02", station="Danmarks plass", components=["NOx"])
