from BeautifulSoup import BeautifulSoup
import requests
import pylast

pl_url = 'http://www.wnur.org/playlist/playlists/?dj=Joe+G'
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
    print 'Query: %s - %s' % (tr[1],tr[2])
    try:
        track = client.get_track(tr[1],tr[2])
        print 'Duration: %s' % str(float(track.get_duration())/1000)
    except pylast.WSError, e:
        print e

