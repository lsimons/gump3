# password encryption table used by cvs
shifts = [
    0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
   16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
  114,120, 53, 79, 96,109, 72,108, 70, 64, 76, 67,116, 74, 68, 87,
  111, 52, 75,119, 49, 34, 82, 81, 95, 65,112, 86,118,110,122,105,
   41, 57, 83, 43, 46,102, 40, 89, 38,103, 45, 50, 42,123, 91, 35,
  125, 55, 54, 66,124,126, 59, 47, 92, 71,115, 78, 88,107,106, 56,
   36,121,117,104,101,100, 69, 73, 99, 63, 94, 93, 39, 37, 61, 48,
   58,113, 32, 90, 44, 98, 60, 51, 33, 97, 62, 77, 84, 80, 85,223,
  225,216,187,166,229,189,222,188,141,249,148,200,184,136,248,190,
  199,170,181,204,138,232,218,183,255,234,220,247,213,203,226,193,
  174,172,228,252,217,201,131,230,197,211,145,238,161,179,160,212,
  207,221,254,173,202,146,224,151,140,196,205,130,135,133,143,246,
  192,159,244,239,185,168,215,144,139,165,180,157,147,186,214,176,
  227,231,219,169,175,156,206,198,129,164,150,210,154,177,134,127,
  182,128,158,208,162,132,167,209,149,241,153,251,237,236,171,195,
  243,233,253,240,194,250,191,155,142,137,245,235,163,242,178,152 ]

# encode a password in the same way that cvs does
def mangle(passwd):
  return 'A' +''.join(map(chr,[shifts[ord(c)] for c in str(passwd or '')]))

if __name__=='__main__':
  from gump import load
  from gump.conf import *
  from gump.model import Module,Repository
  from fnmatch import fnmatch

  import os

  # read the list of cvs repositories that the user is already logged into
  password={}
  cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'))
  try:
    cvspass=open(cvspassfile)
    for line in cvspass.readlines():
      password.update(dict([line.strip().split(' ',1)]))
    cvspass.close()
  except: 
    pass

  # load the workspace
  if len(sys.argv)>2 and sys.argv[1] in ['-w','--workspace']:
    workspace=load(sys.argv[2])
    del sys.argv[1:3]
  else:
    workspace=load(default.workspace)

  # determine which modules the user desires (wildcards are permitted)
  selected=sys.argv[1:] or ['*']
  if selected[0]=='all': selected[0]='*'

  # determine which modules are available
  modules=Module.list.keys()
  modules.sort()

  os.chdir(workspace.cvsdir)
  print workspace.cvsdir

  for name in modules:
    module=Module.list[name]
    if not module.cvs: continue

    # does this name match
    for pattern in selected:
      if fnmatch(name,pattern): break
    else:
      # no match, advance to the next name
      continue

    repository=Repository.list[module.cvs.repository]
    root=module.cvsroot()
  
    # log into the cvs repository
    if repository.root.method=='pserver':
      newpass=mangle(repository.root.password)
      if not root in password or password[root]<>newpass:
        cvspassfile=os.path.expanduser(os.path.join('~','.cvspass'),'a')
        cvspassfile.write(root+' '+newpass+'\n')
        cvspassfile.close()

    if os.path.exists(name):

      # do a cvs update
      cmd='cvs -d '+ root + ' update'
      if module.cvs.tag: 
        cmd+=' -r ' + module.cvs.tag
      else:
        cmd+=' -A'
      cmd+=' '+name

    else:

      # do a cvs checkout
      cmd='cvs -d '+ root + ' checkout -P'
      if module.cvs.tag: cmd+=' -r ' + module.cvs.tag
      if module.cvs.module<>name: cmd+=' -d '+name
      cmd+=' '+module.cvs.module

    #execute the command
    print
    from popen2 import popen2
    (stdout,stdin)=popen2(cmd + " 2>&1")
    stdin.close()
    line=cmd
    while line:
      print line
      line=stdout.read()
