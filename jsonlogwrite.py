import datetime
try:
    import simplejson as json
except ImportError:
    import json

def write(data, logfile):
    data = data
    data['log_timestamp'] = str(datetime.datetime.now())
    if 'window_title' in data:
        data['window_title'] = data['window_title'].encode('string_escape')
    text = json.dumps(data, separators=(',',':')) #compact
    print(logfile, text)
    with open(logfile, 'a') as fp:
        fp.write(text + '\n')


# post to google forms:
# https://docs.google.com/forms/d/e/1FAIpQLSfL1-rJig0nTvT3MdM1hZk34mJlZ_FUDPKD2MjWe-r1YdDfFA/viewform?usp=sf_link
# https://goo.gl/forms/Di4ffwYmlFgq42C23
