from page_downloaders import PlainUrlPage, WebtoonsLoggedInPage

from measurements import Measurement, parse_tapas_views, parse_tapas_subs
from measurements import number_in_thousands_with_suffix_K, body_of_tag, float_between_0_and_10
from measurements import featured_comics_in_order, compose_parsers, integer_with_commas

import observable

class Artifacts(object):
    def __init__(self, pages, measurements, observables):
        self.pages, self.measurements, self.observables = pages, measurements, observables

def tapas_numerical_observables(config):
    tapas_comic_page   = PlainUrlPage('http://tapas.io/series/{}'.
                                      format(config.comic_name))
    tapas_creator_page = PlainUrlPage('https://tapas.io/{}/subscribers'.
                                      format(config.creator_name))

    tapas_views = Measurement('tapas.views', tapas_comic_page, parse_tapas_views)
    tapas_subs  = Measurement('tapas.subs'  , tapas_creator_page,
                              parse_tapas_subs(config.creator_name))

    measurements = [tapas_subs, tapas_views]
    return [observable.identity(m) for m in measurements]

def tapas_ranking_observables(config):
    tapas_popular_first_page     = PlainUrlPage('https://tapas.io/comics?browse=POPULAR')
    tapas_trending_first_page    = PlainUrlPage('https://tapas.io/comics?browse=TRENDING')
    tapas_staff_picks_first_page = PlainUrlPage('https://tapas.io/comics?browse=TAPASTIC')

    tapas_popular     = Measurement('tapas.popular-comics',
                                    tapas_popular_first_page,
                                    featured_comics_in_order)

    tapas_trending    = Measurement('tapas.trending-comics',
                                    tapas_trending_first_page,
                                    featured_comics_in_order)
    
    tapas_staff_picks = Measurement('tapas.staff-picks-comics',
                                    tapas_staff_picks_first_page,
                                    featured_comics_in_order)

    measurements = [tapas_popular, tapas_trending, tapas_staff_picks]
    return [observable.rank(config.comic_name, config.creator_name, m)
            for m in measurements]

def webtoons_logged_in_dashboard_observables(config):
    if not config.webtoons_username:
        return []

    webtoons_logged_in_dashboard = WebtoonsLoggedInPage(
        'http://www.webtoons.com/challenge/titleStat?titleNo=81223',
        username=config.webtoons_username,
        password=config.webtoons_password)

    subs_selector = '//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[1]/li[3]/span/text()'
    webtoons_subs        = Measurement('webtoons.subs',
                                       webtoons_logged_in_dashboard,
                                       compose_parsers(
                                           integer_with_commas,
                                           body_of_tag(
                                               selector=subs_selector)))

    monthly_pv_selector  = \
        '//*[@id="content"]/div[2]/div[2]/div/div[2]/ul[2]/li[3]/span/text()'
    webtoons_monthly_pvs = Measurement('webtoons.monthly_pvs',
                                       webtoons_logged_in_dashboard,
                                       compose_parsers(
                                           integer_with_commas,
                                           body_of_tag(
                                               selector=monthly_pv_selector)))

    likes_selector       = '//*[@id="content"]/div[2]/ul/li/div/p[2]/em/text()'
    webtoons_likes       = Measurement('webtoons.likes',
                                       webtoons_logged_in_dashboard,
                                       compose_parsers(
                                           integer_with_commas,
                                           body_of_tag(
                                               selector=likes_selector)))

    measurements = [webtoons_subs, webtoons_likes, webtoons_monthly_pvs]
    return [observable.identity(m) for m in measurements]

def webtoons_public_number_observables(config):
    webtoons_public_comic_page = PlainUrlPage(
        'http://www.webtoons.com/en/challenge/camellia/list?title_no=81223'.
        format(config.creator_name))

    views_selector  = '//*[@id="_asideDetail"]/ul/li[2]/em/text()'
    webtoons_views  = Measurement('webtoons.views',
                                  webtoons_public_comic_page,
                                  compose_parsers(
                                      number_in_thousands_with_suffix_K,
                                      body_of_tag(selector=views_selector)))

    rating_selector = '//*[@id="_starScoreAverage"]/text()'
    webtoons_rating = Measurement('webtoons.rating',
                                       webtoons_public_comic_page,
                                       compose_parsers(
                                           float_between_0_and_10,
                                           body_of_tag(selector=rating_selector)))

    measurements = [webtoons_rating, webtoons_views]
    return [observable.identity(m) for m in measurements]

def all_observables(config):
    answer = tapas_numerical_observables(config) + \
             tapas_ranking_observables(config) + \
             webtoons_logged_in_dashboard_observables(config) + \
             webtoons_public_number_observables(config)
    
    return answer

def all_artifacts(config):
    # TODO cleanliness: Can this interface b cleanly implemented?    
    # diff_observables      = map(Observe_diff, numerical_observables)

    observables  = all_observables(config)
    measurements = set([o.measurement for o in observables])
    pages        = set([m.page        for m in measurements])

    return Artifacts(pages, measurements, observables)
