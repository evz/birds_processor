from BeautifulSoup import BeautifulSoup
import requests
import json
import urllib
import math
import pylast

pl_url = 'http://www.wnur.org/playlist/playlists/?dj=Joe+G'
lastfm_url = 'http://ws.audioscrobbler.com/2.0/'
last_fm_api_key = 'da2f492ee9d414260f8ff9e252ab00f3'
last_fm_api_secret = 'cf877f343b4465d8ac3fc786818c299b'
r = requests.get(pl_url)
soup = BeautifulSoup(r.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
test = soup.find('table',{'class':'playlist'})
pl = []
rows = test.findAll('tr')
for row in rows[1:]:
    track = []
    if len(row.findAll('td')) is 6:
        for cell in row.findAll('td'):
            track.append(cell.text)
        pl.append(track)

client = pylast.LastFMNetwork(api_key = last_fm_api_key, api_secret = last_fm_api_secret)
for tr in pl:
    print 'Query string: %s' % tr[3]
    search = client.search_for_album(tr[3])
    for res in search.get_next_page():
        for track in res.get_tracks():
            if tr[2] in track.get_title() and tr[1] in track.get_artist().get_name():
                print 'Artist: %s, Title: %s, Duration: %s' % (track.get_artist(), track.get_title(), track.get_duration())