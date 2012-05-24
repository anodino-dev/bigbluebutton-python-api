from urllib2 import urlopen
from urllib import urlencode
from hashlib import sha1
import xml.etree.ElementTree as ET
import bbb_settings as settings


def parse(response):
    try:
        xml = ET.XML(response)
        code = xml.find('returncode').text
        if code == 'SUCCESS':
            return xml
        else:
            raise
    except:
        return None

def api_call(query, call):
    prepared = "%s%s%s" % (call, query, settings.SALT)
    checksum = sha1(prepared).hexdigest()
    result = "%s&checksum=%s" % (query, checksum)
    return result


def join_url(meeting_id, name, password):
    call = 'join'
    query = urlencode((
                       ('fullName', name),
                       ('meetingID', meeting_id),
                       ('password', password),
                       ))
    hashed = api_call(query, call)
    url = settings.BBB_API_URL + call + '?' + hashed
    return url

def end_meeting(meeting_id, password):
    call = 'end'
    query = urlencode((
                       ('meetingID', meeting_id),
                       ('password', password),
    ))
    hashed = api_call(query, call)
    url = settings.BBB_API_URL + call + '?' + hashed
    result = parse(urlopen(url).read())
    if result:
        pass
    else:
        return 'error'

def meeting_info(meeting_id, password):
    call = 'getMeetingInfo'
    query = urlencode((
                       ('meetingID', meeting_id),
                       ('password', password),
                       ))
    hashed = api_call(query, call)
    url = settings.BBB_API_URL + call + '?' + hashed
    r = parse(urlopen(url).read())
    if r:
        # Create dict of values for easy use in template
        d = {
             'start_time': r.find('startTime').text,
             'end_time': r.find('endTime').text,
             'participant_count': r.find('participantCount').text,
             'moderator_count': r.find('moderatorCount').text,
             'moderator_pw': r.find('moderatorPW').text,
             'attendee_pw': r.find('attendeePW').text,
             'invite_url': 'join=%s' % meeting_id,
             }
        return d
    else:
        return None

def get_meetings():
    call = 'getMeetings'
    query = urlencode((
                       ('random', 'random'),
                       ))
    hashed = api_call(query, call)
    url = settings.BBB_API_URL + call + '?' + hashed
    result = parse(urlopen(url).read())
    if result:
        # Create dict of values for easy use in template
        d = []
        r = result[1].findall('meeting')
        for m in r:
            meeting_id = m.find('meetingID').text
            password = m.find('moderatorPW').text
            d.append({
                      'name': meeting_id,
                      'running': m.find('running').text,
                      'moderator_pw': password,
                      'attendee_pw': m.find('attendeePW').text,
                      'info': meeting_info(
                                           meeting_id,
                                           password)
                      })
        return d
    else:
        return 'error'