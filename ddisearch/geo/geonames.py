# simple client to interact with geonames api, since
# the geopy client is too limited and doesn't expose all OPTIONS:

import requests

class GeonamesClient(object):

    api = 'http://api.geonames.org/searchJSON'

    def __init__(self, username):
        self.username = username

    def geocode(self, query=None, name=None, name_equals=None,
                exactly_one=True, timeout=None,
                country_bias=None, feature_code=None, feature_class=None,
                admin_code1=None):

        if not any([query, name, name_equals]):
            raise Exception('One of query, name or name_equals is required')

        params = {'username': self.username, 'orderBy': 'relevance'}

        # query term (really only expect one of these)
        if query:
            params['query'] = query
        if name:
            params['name'] = name
        if name_equals:
            params['name_equals'] = name_equals

        if exactly_one:
            params['maxRows'] = 1
        if country_bias:
            params['countryBias'] = country_bias
        if admin_code1:
            params['adminCode1'] = admin_code1
        if feature_code:
            # TODO: check that this works correctly for list of params
            params['featureCode'] = feature_code
        if feature_class:
            params['featureClass'] = feature_class

        r = requests.get(self.api, params=params)
        result = r.json()
        if result['totalResultsCount']:
            if exactly_one:
                return GeonamesResult(result['geonames'][0])
            else:
                return [GeonamesResult(res) for res in result['geonames']]


class GeonamesResult(object):
    '''Simple result class for locations returned by geonames search,
    compatible with :mod:`geopy` results.'''

    def __init__(self, data):
        self.latitude = data['lat']
        self.longitude = data['lng']
        self.raw = data

    def __unicode__(self):
        return self.raw['name']

    def __repr__(self):
        return u'<GeonamesResult %s>' % unicode(self)


# sample result to use for tests

# {"totalResultsCount":5325,"geonames":[{"countryId":"2635167","adminCode1":"ENG","countryName":"United Kingdom","fclName":"city, village,...","countryCode":"GB","lng":"-0.12574","fcodeName":"capital of a political entity","toponymName":"London","fcl":"P","name":"London","fcode":"PPLC","geonameId":2643743,"lat":"51.50853","adminName1":"England","population":7556900},{"countryId":"2635167","adminCode1":"ENG","countryName":"United Kingdom","fclName":"city, village,...","countryCode":"GB","lng":"-0.09184","fcodeName":"seat of a third-order administrative division","toponymName":"City of London","fcl":"P","name":"City of London","fcode":"PPLA3","geonameId":2643741,"lat":"51.51279","adminName1":"England","population":7556900}]}
