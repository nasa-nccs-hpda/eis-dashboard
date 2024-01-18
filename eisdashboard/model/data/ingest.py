from eisdashboard.model.cmr_query import CmrProcess

from functools import lru_cache
import logging

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
        'POCLOUD': 'https://archive.podaac.earthdata.nasa.gov/s3credentials',
        'LPDAAC': 'https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials',
        'ORNLDAAC': 'https://data.ornldaac.earthdata.nasa.gov/s3credentials',
        'GHRCDAAC': 'https://data.ghrc.earthdata.nasa.gov/s3credentials'
    }

    def __init__(self, config):

        self.config = config

    # -------------------------------------------------------------------------
    # get_nasa_earthdata
    # -------------------------------------------------------------------------
    def get_nasa_earthdata(self, query_package: dict) -> dict:
        return self.get_data_from_bounds(query_package)

    # -------------------------------------------------------------------------
    # get_data_from_bounds
    # -------------------------------------------------------------------------
    def get_data_from_bounds(self, query_package: dict) -> dict:

        search_dict = query_package

        logging.info(f'Querying CMR for data links: {search_dict}')

        cmrP = CmrProcess(mission=search_dict['collection_id'],
                          dateTime=search_dict['datetime'],
                          lonLat=','.join(str(e)
                                          for e in search_dict['coords']),
                          spatialParameter=search_dict['spatialParameter'],
                          pageSize=150,
                          maxPages=1)

        resultList, providerID = cmrP.run()

        if providerID == 'POCLOUD':
            logging.info('Filtering PODAAC data path')
            resultList = self._refine_podaac(resultList)

        logging.info('Ingesting data')

        st = time.time()
        data = self.ingest(providerID, resultList)
        et = time.time()
        logging.info(f'Time to get data: {et-st}')

        logging.info('Done ingesting data')

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

        try:

            requestResultPackage = requests.get(requestUrl)

        except requests.exceptions.RequestException as e:

            msg = f'{provider} S3 credential error: ' + \
                f'Exception: {e}' + \
                'Client or server error: ' + \
                f'Request URL: {requestUrl}'

            warnings.warn(msg)

            self._error = True

            logging.error(msg)

            return 0, None

        temporaryS3Credentials = requestResultPackage.json()

        logging.debug(temporaryS3Credentials)

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

            logging.debug(f'Opening {s3_file_path}')

            try:

                s3_file_object = s3FileSystem.open(s3_file_path)

                s3_file_objects.append(s3_file_object)

            except Exception as e:

                logging.error(f'Error opening {s3_file_path} using these' +
                              f' credentials {temp_s3_creds} for this' +
                              f' DAAC: {provider_id}: {e}')

        if len(s3_file_objects) == 0:

            logging.error(f'No data returned from s3paths: {s3_list} from' +
                          f'this provider: {provider_id}')

            return None

        logging.info('Done opening s3 files, ' +
                     'combining into single XR data-array.')

        ingested_data = xr.open_mfdataset(s3_file_objects, combine='by_coords')

        return ingested_data

    # ------------------------------------------------------------------------
    # ingest
    # ------------------------------------------------------------------------
    def ingest_dummy(self, provider_id: str, s3_list: list) -> xr.DataArray:
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """

        merra_dir = pathlib.Path(
            '/explore/nobackup/people/cssprad1/' +
            'projects/eis-dashboard/data/merra')
        merra_files = merra_dir.glob('*.nc4')

        ingested_data = xr.open_mfdataset(merra_files)

        return ingested_data

    # ------------------------------------------------------------------------
    # get_custom_s3_data
    # ------------------------------------------------------------------------
    def get_custom_s3_data(self, collectionID: str,
                           s3_path: str) -> xr.DataArray:

        logging.info('Ingesting custom s3 data')

        st = time.time()
        data = self.ingest_custom_s3(s3_path)
        et = time.time()
        logging.info(f'Time to get data: {et-st}')

        logging.info('Done ingesting custom s3 data')

        return_dict = {'key': collectionID,
                       'data': data,
                       'variables': list(data.variables)}

        return return_dict

    # ------------------------------------------------------------------------
    # ingest_custom_s3
    # ------------------------------------------------------------------------
    def ingest_custom_s3(self, s3_path: str) -> xr.DataArray:

        logging.debug(f'Opening user-supplied s3 path: {s3_path}')

        try:

            ingested_data = xr.open_mfdataset([s3_path], engine='zarr')

            return ingested_data

        # ---
        # Need to add more specific error handling
        # - what happens when s3 doesn't exist
        # - what happens if bad connection
        # - what happens if it is not xarray compatible
        # Note: this might need to change once we support raster ingesting
        # ---
        except Exception as e:

            logging.error(f'Error opening {s3_path} into xarray data-array' +
                          'make sure file exists and is xarray compatible.' +
                          f' {e}')

            raise e

    # ------------------------------------------------------------------------
    # refine PODAAC CMR list
    # ------------------------------------------------------------------------
    def _refine_podaac(self, urls: list) -> list:
        s3list = []
        suffixes = ('.nc', '.nc4', '.hdf')

        for e in urls:
            if e.endswith(suffixes):
                s3path = '/'.join(['s3:/']+e.split('/')[3:])
                s3list.append(s3path)

        return tuple(s3list)
