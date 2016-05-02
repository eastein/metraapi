from __future__ import print_function
import tornado.gen
import tornado.httpclient
import json
import pprint
import six

if six.PY2:
    import urllib as urllib_parse_module
else:
    import urllib.parse as urllib_parse_module

import metraapi.metraapi_internal as internal


def format_query_params(url, queryparams):
    """
    :param url: URL without a query portion
    :param queryparams: dictionary of query variables, must not be empty
    :return: formatted URL
    """
    return '{0}?{1}'.format(url, urllib_parse_module.urlencode(queryparams))

def async_fetch(*args, **kwargs):
    return tornado.httpclient.AsyncHTTPClient().fetch(*args, **kwargs)

@tornado.gen.coroutine
def get_arrival_times(line_id, origin_station_id, destination_station_id, verbose=False):
    a_params = internal.get_acquity_request_parameters(line_id, origin_station_id, destination_station_id)
    g_params = internal.get_gtd_request_parameters(line_id, origin_station_id, destination_station_id)

    a_future = async_fetch(a_params['url'], method='POST', headers=a_params['headers'],
                                                          body=a_params['payload'])
    gtd_request_url = format_query_params(g_params['url'], g_params['query'])

    g_future = async_fetch(gtd_request_url)

    result = yield {
        'acquity': a_future,
        'gtd': g_future,
    }

    print(repr(result['actuity'].body))

    d = json.loads(result['acquity'].body)['d']
    acquity_data = json.loads(d)

    if verbose:
        print('data from %s:' % a_params['url]'])
        pprint.pprint(acquity_data)

    gtd_data = json.loads(result['gtd'].body)
    if verbose:
        print('data from %s:' % g_params['url'])
        pprint.pprint(gtd_data)

    interpreted_results = internal.interpret_arrival_times(line_id, origin_station_id, destination_station_id,
                                                         acquity_data=acquity_data, gtd_data=gtd_data)

    raise tornado.gen.Return(interpreted_results)


@tornado.gen.coroutine
def get_stations_from_line(line_id):
    params = internal.get_stations_request_parameters(line_id)

    lines_response = yield async_fetch(format_query_params(params['url'], params['query']))

    raise tornado.gen.Return(internal.interpret_stations_response(lines_response.body))
