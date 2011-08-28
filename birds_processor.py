from BeautifulSoup import BeautifulSoup
import requests
import datetime
import os
import time
from subprocess import call
from operator import itemgetter
from hsaudiotag import auto
import pylast
# Use time offset info from url to chop up mp3 and then tag it with info from the table
pl_url = 'http://www.wnur.org/playlist/playlists/?dj=Joe+G'
last_fm_api_key = 'da2f492ee9d414260f8ff9e252ab00f3'
last_fm_api_secret = 'cf877f343b4465d8ac3fc786818c299b'
podcasts_dir = '../podcasts/'

r = requests.get(pl_url)
soup = BeautifulSoup(r.content, convertEntities=BeautifulSoup.HTML_ENTITIES)
podcasts = {}
for file in os.walk(podcasts_dir):
    for f in file[2]:
        podcasts[datetime.datetime.strptime(f[-14:].rstrip('mp3').replace('.',''), '%Y-%m-%d').strftime('%m/%d/%Y')] = f
h2s = soup.findAll('h2')
for k,v in podcasts.items():
    print 'Processing %s' % v
    for h2 in h2s:
        if h2.next.next.text == k:
            table = h2.nextSibling
            pl = []
            rows = table.findAll('tr')
            for row in rows[1:]:
                track = []
                if len(row.findAll('td')) is 6:
                    for cell in row.findAll('td'):
                        track.append(cell.text)
                    track[0] = datetime.datetime.strptime(k + ':' + ' '.join(track[0].split(':')), '%m/%d/%Y:%I %M%p')
                    pl.append(track)
            pl = sorted(pl, key=itemgetter(0))
            starttime = pl[0][0]
            dirname = '-'.join(k.split('/'))
            call(['mkdir', podcasts_dir + dirname])
            tr_start = 0.0
            client = pylast.LastFMNetwork(api_key = last_fm_api_key, api_secret = last_fm_api_secret)
            file_duration =  str(round(int(auto.File(podcasts_dir + v).duration)/60,2))
            for tr in pl:
                try:
                    print 'Looking up: %s - %s' % (tr[1],tr[2])
                    track = client.get_track(tr[1],tr[2])
                    tr_duration = float(time.strftime('%M.%S', time.gmtime(track.get_duration()/1000)))
                    if tr_duration == '0.0':
                        print 'No duration listed in last.fm'
                        continue
                    else:
                        print 'Found it. It\'s %s minutes long' % str(tr_duration)
                        tr_end = tr_start + tr_duration
                        call(['mp3splt', podcasts_dir + v, str(tr_start), str(tr_end), '-d ' + dirname, '-g ' + '[@a=' + '"' + tr[1] + '"' + ',@b=' + '"' + tr[3] + '"' + ',@t=' + '"' + tr[2] + '"' + ']'])
                        tr_start = tr_end
                except pylast.WSError, e:
                    print 'Last.fm says: %s ' % e
#                use this https://github.com/discogs/discogs-python-client
#                call('mp3splt' + ' podcasts/' + v + ' ' + tr_start + ' ' + tr_end + ' -o ' + '_'.join(tr[2].split(' ')) + '.mp3')
