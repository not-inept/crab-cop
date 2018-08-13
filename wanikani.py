from json import loads
from enum import Enum
from urllib.request import urlopen, Request

__all__ = ['WaniKani']

URL_TEMPLATE = 'https://api.wanikani.com/v2/{endpoint}/{argument}?{filters}'
AUTH_TEMPLATE = 'Bearer {token}'
ERROR_TEMPLATE = '{code} - {message}'

class WaniKani(object):
    def __init__(self, token, url_template=URL_TEMPLATE, auth_template=AUTH_TEMPLATE):
        self.auth = auth_template.format(token=token)
        self.url_template = url_template

    def request(self, endpoint, argument='', filters={}, after=None, before=None):
        if after is not None:
            filters['page_after_id'] = after
        elif before:
            filters['page_before_id'] = before
        filters = '&'.join([f + '=' + str(filters[f]) for f in filters])
        url = self.url_template.format(endpoint=endpoint, argument=argument, filters=filters)
        request = Request(url)
        request.add_header('Authorization', self.auth)   
        result = loads(urlopen(request).read().decode('utf-8'))
        return result

    def get_user(self):
        return self.request('user')
    user = property(get_user)

    def get_subjects(self, id='', filters={}, after=None, before=None):
        return self.request('subjects', id, filters, after, before)
    subjects = property(get_subjects)

    def get_assignments(self, id='', filters={}, after=None, before=None):
        return self.request('assignments', id, filters, after, before)
    assignments = property(get_assignments)

    def get_review_statistics(self, id='', filters={}, after=None, before=None):
        return self.request('review_statistics', id, filters, after, before)
    review_statistics = property(get_review_statistics)

    def get_study_materials(self, id='', filters={}, after=None, before=None):
        return self.request('study_materials', id, filters, after, before)
    study_materials = property(get_study_materials)

    def get_summary(self):
        return self.request('summary')
    summary = property(get_summary)

    def get_reviews(self, id='', filters={}, after=None, before=None):
        return self.request('reviews', id, filters, after, before)
    reviews = property(get_reviews)   

    def get_level_progressions(self, id='', filters={}, after=None, before=None):
        return self.request('level_progressions', id, filters, after, before)
    level_progressions = property(get_level_progressions)

    def get_resets(self, id='', filters={}, after=None, before=None):
        return self.request('resets', id, filters, after, before)
    resets = property(get_resets)
