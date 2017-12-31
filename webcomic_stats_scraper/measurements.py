from lxml import html

def integer_with_commas(s):
    return int(s.replace(',', ''))

def chop_suffix(text, suffix, error_message=None):
    if not text.endswith(suffix):
        raise AttributeError("Expected a string that ends with '{}', got: {}".
                             format(suffix, text))
    return text[:-len(suffix)]

def body_of_tag(selector):
    def parser(content):
        return html.fromstring(content).xpath(selector)[0]
    return parser

def featured_comics_in_order(content):
    all_titles = html.fromstring(content).xpath('//*[@id="page-wrap"]/div/section[1]/ul')[0]

    answer = []
    for title_tag in all_titles.getchildren():
        answer.append([a.text for a in title_tag.findall('a')])
        
    return answer

def parse_tapas_subs(creator_name):
    def extract_subscribers_string_from_html(content):
        xpath_selector = '//a[@href="/{}/subscribers"]/text()'.format(creator_name)
        xpath_query_result = html.fromstring(content).xpath(xpath_selector)

        return ''.join([x for x in ''.join(xpath_query_result).strip() if x not in ' \n'])

    def parse(content):
        subs_string = extract_subscribers_string_from_html(content)

        return integer_with_commas(chop_suffix(subs_string, suffix='Subscribers'))
    return parse

def parse_tapas_views(content):
    def extract_pageviews_string_from_html(content):
        xpath_selector = '//ul[@class="number-status"]/li[@class="common-tooltip"]'
        li_tag_containing_pageviews = body_of_tag(xpath_selector)(content)

        if "data-title" not in li_tag_containing_pageviews.attrib:
            raise AttributeError(make_error_message("The 'data-title' attribute wasn't in the li"))
        
        return li_tag_containing_pageviews.attrib["data-title"]
    
    pageviews_string = extract_pageviews_string_from_html(content)
        
    return integer_with_commas(chop_suffix(pageviews_string, suffix=' views'))

def number_in_thousands_with_suffix_K(text):
    return int(float(chop_suffix(text, suffix='K')) * 1000)

def compose_parsers(parser1, parser2):
    def answer(content):
        return parser1(parser2(content))
    return answer

def float_between_0_and_10(text):
    answer = float(text)
    if not 0 < answer < 10:
        raise ValueError("Expected a number between 0 and 10, got {}".format(text))
    return answer        

class Measurement(object):
    def __init__(self, name, page, parse):
        self.name, self.page, self.parse = name, page, parse
