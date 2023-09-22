from swotdashboard.model.cmr_query import CmrProcess
from swotdashboard.model.common import read_config

from functools import lru_cache

import requests
import s3fs
import warnings
import xarray as xr

# DEV ONLY
import pathlib
import time
# END DEV ONLY


# -----------------------------------------------------------------------------
# Ingest
# -----------------------------------------------------------------------------
class Ingest(object):

    PROVIDER_CREDENTIAL_ENDPOINT: dict = {
        'GES_DISC': 'https://data.gesdisc.earthdata.nasa.gov/s3credentials',
        'PODAAC': 'https://archive.podaac.earthdata.nasa.gov/s3credentials',
        'LPDAAC': 'https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials',
        'ORNLDAAC': 'https://data.ornldaac.earthdata.nasa.gov/s3credentials',
        'GHRCDAAC': 'https://data.ghrc.earthdata.nasa.gov/s3credentials'
    }

    def __init__(self, config):

        self.config = config

        # self.s3 = s3fs.S3FileSystem(anon=True)

    # -------------------------------------------------------------------------
    # get_data_from_bounds
    # -------------------------------------------------------------------------
    def get_data_from_bounds(self, query_package: dict) -> dict:

        search_dict = query_package

        cmrP = CmrProcess(mission=search_dict['collection_id'],
                          dateTime=search_dict['datetime'],
                          lonLat=','.join(str(e)
                                          for e in search_dict['coords']),
                          spatialParameter=search_dict['spatialParameter'],
                          pageSize=150,
                          maxPages=1)

        resultList, providerID = cmrP.run()

        st = time.time()
        data = self.ingest(providerID, resultList)
        et = time.time()
        print(f'Time to get data: {et-st}')
        # print(data.variables)

        return_dict = {'key': search_dict['collection_id'],
                       'data': data,
                       'variables': list(data.variables)}

        return return_dict

    # -------------------------------------------------------------------------
    # _get_temp_credentials
    # -------------------------------------------------------------------------
    @lru_cache(maxsize=32)
    def _get_temp_credentials(self, provider: str):
        """_summary_

        Args:
            provider (str): _description_

        Returns:
            _type_: _description_
        """

        requestUrl = self.PROVIDER_CREDENTIAL_ENDPOINT[provider]

        print(requestUrl)

        try:

            requestResultPackage = requests.get(requestUrl)

        except requests.exceptions.RequestException as e:

            msg = f'{provider} S3 credential error: ' + \
                f'Exception: {e}' + \
                'Client or server error: ' + \
                f'Request URL: {requestUrl}'

            warnings.warn(msg)

            self._error = True

            return 0, None

        temporaryS3Credentials = requestResultPackage.json()

        return temporaryS3Credentials

    # ------------------------------------------------------------------------
    # ingest
    # ------------------------------------------------------------------------
    @lru_cache(maxsize=32)
    def ingest(self, provider_id: str, s3_list: list) -> xr.DataArray:
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        temp_s3_creds = self._get_temp_credentials(provider_id)

        s3FileSystem = s3fs.S3FileSystem(
            anon=False,
            key=temp_s3_creds['accessKeyId'],
            secret=temp_s3_creds['secretAccessKey'],
            token=temp_s3_creds['sessionToken'])

        s3_file_objects = []

        for s3_file_path in s3_list:

            try:

                s3_file_object = s3FileSystem.open(s3_file_path)

                s3_file_objects.append(s3_file_object)

            except Exception as e:

                print(f'Error opening {s3_file_path} using these' +
                      f' credentials {temp_s3_creds} for this' +
                      f' DAAC: {provider_id}: {e}')

        if len(s3_file_objects) == 0:

            print(f'No data returned from s3paths: {s3_list} from' +
                  f'this provider: {provider_id}')

            return None

        ingested_data = xr.open_mfdataset(s3_file_objects, combine='by_coords')

        return ingested_data

    # ------------------------------------------------------------------------
    # ingest
    # ------------------------------------------------------------------------
    @lru_cache(maxsize=32)
    def ingest_dummy(self, provider_id: str, s3_list: list) -> xr.DataArray:
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        # _ = self._get_temp_credentials(provider_id)

        merra_dir = pathlib.Path(
            '/explore/nobackup/people/cssprad1/' +
            'projects/swot-dashboard/data/merra')
        merra_files = merra_dir.glob('*.nc4')

        ingested_data = xr.open_mfdataset(merra_files,
                                          combine='by_coords').resample(
                                              time='1D').mean()

        return ingested_data


if __name__ == '__main__':

    # DEV ONLY
    import shapely
    from shapely.geometry import Polygon
    import datetime

    # END DEV ONLY
    config = read_config('swot-dashboard/configs/test_config.yaml')

    date_beginning = datetime.datetime(2019, 5, 18)
    date_end = datetime.datetime(2019, 6, 18)
    datetimeStr = f"{date_beginning.isoformat()}Z," + \
        f"{date_end.isoformat()}Z"
    COLLECTID_ATL08_V5 = "GLDAS_NOAH025_3H"

    search_dict_bbox = {
        'spatialParameter': 'bounding_box',
        'coords': [-76.6, 38.8, -76.5, 38.9],
        'datetime': datetimeStr,
        'collection_id': COLLECTID_ATL08_V5
    }

    search_dict_point = {
        'spatialParameter': 'point',
        'coords': [-76.6, 38.8],
        'datetime': datetimeStr,
        'collection_id': COLLECTID_ATL08_V5,
    }

    coords = [[[-80.622075, 38.104592], [-74.645512, 38.242781],
               [-75.524418, 34.420806], [-81.3252, 34.130297],
               [-80.622075, 38.104592]]]
    polygon = Polygon(coords[0])
    # this is important to get
    poly = shapely.geometry.polygon.orient(polygon)
    polygon_coords_str = [lat_or_lon for latlon in
                          poly.exterior.coords for
                          lat_or_lon in latlon]

    search_dict_polygon = {
        'spatialParameter': 'polygon',
        'coords': polygon_coords_str,
        'datetime': datetimeStr,
        'collection_id': COLLECTID_ATL08_V5
    }

    search_dict = search_dict_polygon

    config = read_config('swot-dashboard/configs/test_config.yaml')
    ingest = Ingest(config)

    print(ingest)

    print("attempt 1")
    st = time.time()
    pkg = ingest.get_data_from_bounds(search_dict)
    print(pkg)
    et = time.time()
    pkg['data'].close()
    print(f'attempt 1 took {et - st}')
    print('attempt 2')
    st = time.time()
    pkg = ingest.get_data_from_bounds(search_dict)
    print(pkg)
    et = time.time()
    print(f'attempt 2: took {et - st}')
