import re, time, urllib
from xml.sax.saxutils import escape
from xml.sax import parse
from xml.sax.handler import ContentHandler

gumproot='http://cvs.apache.org/builds/gump/'
summary=re.compile('<td>\s(\d\d:\d\d:\d\d)\s</td>\s' +
                   '<td.*?>\s<a href="(.*?)">([-\w]*)</a>\s</td>\s' +
		   '<td.*?>\s(\w+)\s</td>\s')
TZ='%+.2d:00' % (-time.timezone/3600)

module={}
class Workspace(ContentHandler):
  logdir='.'
  def startElement(self, name, attrs):
    if name=='workspace':
      attrs=dict(attrs)
      if 'logdir' in attrs:
	Workspace.logdir=attrs['logdir']
    if name=='project':
      attrs=dict(attrs)
      if 'name' in attrs and 'module' in attrs:
	module[attrs['name']]=attrs['module']

parse(open('work/merge.xml'),Workspace())

def analyze(file,pstat,date):
  print file
  index=urllib.urlopen(file).read()
  for (time, url, project, status) in summary.findall(index):
    if project not in pstat:
      pstat[project]=(date, time, status, url, project, 1)
    elif pstat[project][2]<>status: 
      pstat[project]=(date, time, status, url, project, 0)

pstat={}
builds=urllib.urlopen(gumproot).read()
for date in re.findall('<a href="([\d-]*)/">',builds):
  analyze(gumproot+date,pstat,date)

today=time.strftime('%Y-%m-%d')
analyze(Workspace.logdir+'/index.html',pstat,today)

result=pstat.values()
result.sort()
result.reverse()

gumprss=open(Workspace.logdir + '/index.rss','w')
gumprss.write("""<rss version="2.0"
  xmlns:admin="http://webns.net/mvcb/" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/">

  <channel>
    <title>Gump</title>
    <link>http://jakarta.apache.org/gump/</link>
    <description>Life is like a box of chocolates</description>

    <admin:generatorAgent rdf:resource="http://cvs.apache.org/viewcvs/jakarta-gump/python/gumprss.py"/>
    <admin:errorReportsTo rdf:resource="mailto:gump@jakarta.apache.org"/>

    <sy:updateFrequency>1</sy:updateFrequency>
    <sy:updatePeriod>daily</sy:updatePeriod>""")

for (date,time,status,url,project,first) in result:
  if first: continue
  if not project in module: continue
  link=gumproot + date + '/' + url
  print link
  if date==today:
    data=urllib.urlopen(Workspace.logdir+'/'+url).read()
  else:
    data=urllib.urlopen(link).read()
  content=re.split('</?XMP>',data)
  if len(content)<2: content=re.split('</?p>',data)
  content=escape('\n'.join((content+[''])[1].splitlines()[-25:]))

  gumprss.write("""
    <item>
      <title>%s %s %s</title>
      <link>%s</link>
      <description>&lt;pre&gt;%s&lt;/pre;&gt;</description>
      <dc:subject>%s</dc:subject>
      <dc:date>%sT%s%s</dc:date>
    </item>""" % (project,status,date, link, content, module[project], date,time,TZ))


gumprss.write("""
  </channel>
</rss>
""")
gumprss.close()
