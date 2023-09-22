import json
import warnings

import certifi
import urllib3
from urllib.parse import urlencode


# -----------------------------------------------------------------------------
# class CmrProcess
#
# @author: Caleb Spradlin, caleb.s.spradlin@nasa.gov
# @version: 08.31.2023
#
# https://cmr.earthdata.nasa.gov/search/
# https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
# -----------------------------------------------------------------------------
class CmrProcess(object):

    CMR_BASE_URL = 'https://cmr.earthdata.nasa.gov' +\
        '/search/granules.umm_json_v1_4?'

    # Range for valid lon/lat
    LATITUDE_RANGE = (-90, 90)
    LONGITUDE_RANGE = (-180, 180)

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self,
                 mission,
                 dateTime,
                 lonLat=None,
                 error=False,
                 dayNightFlag='',
                 spatialParameter='bounding_box',
                 pageSize=150,
                 maxPages=50):

        self._error = error
        self._dateTime = dateTime
        self._mission = mission
        self._pageSize = pageSize
        self._maxPages = maxPages
        self._onlineOnly = 'true'
        self._spatialParameter = spatialParameter

        self._lonLat = lonLat
        self._dayNightFlag = dayNightFlag

    # -------------------------------------------------------------------------
    # run()
    #
    # Given a set of parameters on init (time, location, mission), search for
    # the most relevant file. This uses CMR to search metadata for
    # relevant matches.
    # -------------------------------------------------------------------------
    def run(self):
        print('Starting query')
        fileUrlsSet = set()
        providerID = None
        for pageIdx in range(self._maxPages):

            pageNumber = pageIdx + 1

            returnDict, error = self._cmrQuery(pageNum=pageNumber)

            if error and pageIdx > 1:
                return sorted(list(fileUrlsSet))

            if not error:
                print('Results found on page: {}'.format(pageNumber))
                returnDicts = list(returnDict.values())
                out = [r['file_url'] for r in returnDicts]
                providerID = returnDicts[0]['provider_id']
                fileUrlsSet.update(out)

        fileUrlsList = sorted(list(fileUrlsSet))

        # LRU caching requires that the serializable object
        # be immutable so we make it a tuple
        fileUrlsTuple = tuple(fileUrlsList)
        return fileUrlsTuple, providerID

    # -------------------------------------------------------------------------
    # cmrQuery()
    #
    # Search the Common Metadata Repository(CMR) for a file that
    # is a temporal and spatial match.
    # -------------------------------------------------------------------------

    def _cmrQuery(self, pageNum=1):

        requestDictionary = self._buildRequest(pageNum=pageNum)
        totalHits, resultDictionary = self._sendRequest(requestDictionary)

        if self._error:
            return None, self._error

        if totalHits <= 0:
            print('No hits on page number: {}, ending search.'.format(pageNum))
            # warnings.warn(msg)
            return None, True

        try:
            resultDictionaryProcessed = self._processRequest(resultDictionary)

        except KeyError as ke:
            warnings.warn('Error processing returned request dict from ' +
                          f'CMR. Error: {ke}')
            self._error = True
            return None, True

        return resultDictionaryProcessed, self._error

    # -------------------------------------------------------------------------
    # buildRequest()
    #
    # Build a dictionary based off of parameters given on init.
    # This dictionary will be used to encode the http request to search
    # CMR.
    # -------------------------------------------------------------------------
    def _buildRequest(self, pageNum=1):
        requestDict = dict()
        requestDict['page_num'] = pageNum
        requestDict['page_size'] = self._pageSize
        requestDict['short_name'] = self._mission
        requestDict[self._spatialParameter] = self._lonLat
        requestDict['day_night_flag'] = self._dayNightFlag
        requestDict['temporal'] = self._dateTime
        requestDict['online_only'] = self._onlineOnly
        return requestDict

    # -------------------------------------------------------------------------
    # _sendRequest
    #
    # Send an http request to the CMR server.
    # Decode data and count number of hits from request.
    # -------------------------------------------------------------------------
    def _sendRequest(self, requestDictionary):
        with urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                 ca_certs=certifi.where()) as httpPoolManager:
            encodedParameters = urlencode(requestDictionary, doseq=True)
            requestUrl = self.CMR_BASE_URL + encodedParameters
            print(requestUrl)
            try:
                requestResultPackage = httpPoolManager.request('GET',
                                                               requestUrl)
            except urllib3.exceptions.MaxRetryError:
                self._error = True
                return 0, None

            requestResultData = json.loads(
                requestResultPackage.data.decode('utf-8'))
            status = int(requestResultPackage.status)

            if not status == 400:
                totalHits = len(requestResultData['items'])
                return totalHits, requestResultData

            else:
                msg = 'CMR Query: Client or server error: ' + \
                    'Status: {}, Request URL: {}, Params: {}'.format(
                        str(status), requestUrl, encodedParameters)
                warnings.warn(msg)
                return 0, None

    # -------------------------------------------------------------------------
    # _processRequest
    #
    # For each result in the CMR query, unpackage relevant information to
    # a dictionary. While doing so set flags if data is not desirable (too
    # close to edge of dataset).
    #
    #  REVIEW: Make the hard-coded names class constants? There are a lot...
    # -------------------------------------------------------------------------
    def _processRequest(self, resultDict):

        resultDictProcessed = dict()

        for hit in resultDict['items']:

            fileName = hit['umm']['RelatedUrls'][0]['URL'].split(
                '/')[-1]

            # ---
            # These are hardcoded here because the only time these names will
            # ever change is if we changed which format of metadata we wanted
            # the CMR results back in.
            #
            # These could be placed as class constants in the future.
            # ---
            fileUrl = hit['umm']['RelatedUrls'][1]['URL']
            providerID = hit['meta']['provider-id']

            temporalRange = hit['umm']['TemporalExtent']['RangeDateTime']
            dayNight = hit['umm']['DataGranule']['DayNightFlag']

            spatialExtent = hit['umm']['SpatialExten' +
                                       't']['HorizontalSpatialDom' +
                                            'ain']

            key = fileName

            resultDictProcessed[key] = {
                'file_name': fileName,
                'file_url': fileUrl,
                'provider_id': providerID,
                'temporal_range': temporalRange,
                'spatial_extent': spatialExtent,
                'day_night_flag': dayNight}

        return resultDictProcessed
