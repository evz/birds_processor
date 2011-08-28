from BeautifulSoup import BeautifulSoup
import requests
import datetime
import os
from subprocess import call
from operator import itemgetter
from hsaudiotag import auto
# Use time offset info from url to chop up mp3 and then tag it with info from the table
pl_url = 'http://www.wnur.org/playlist/playlists/?dj=Joe+G'

r = requests.get(pl_url)
soup = BeautifulSoup(r.content)
podcasts = {}
for file in os.walk('podcasts/'):
    for f in file[2]:
        podcasts[datetime.datetime.strptime(f[-14:].rstrip('mp3').replace('.',''), '%Y-%m-%d').strftime('%m/%d/%Y')] = f
h2s = soup.findAll('h2')
for k,v in podcasts.items():
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
            call(['mkdir', dirname])
            for index,tr in enumerate(pl):
                tr_start = tr[0] - starttime
                tr_start = str(round(float(tr_start.seconds)/60,2))
                try:
                    tr_end = pl[index+1][0] - starttime
                    tr_end = str(round(float(tr_end.seconds)/60,2))
                except IndexError:
                    tr_end = str(round(int(auto.File('podcasts/' + v).duration)/60,2))
                print 'tr_start: %s, tr_end: %s' % (tr_start, tr_end)
#                use this https://github.com/discogs/discogs-python-client
#                call('mp3splt' + ' podcasts/' + v + ' ' + tr_start + ' ' + tr_end + ' -o ' + '_'.join(tr[2].split(' ')) + '.mp3')
                call(['mp3splt', 'podcasts/' + v, tr_start, tr_end, '-d ' + dirname, '-g ' + '[@a=' + tr[1] + ',@b=' + tr[3] + ',@t=' + tr[2] + ']'])
