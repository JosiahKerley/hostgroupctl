#!/usr/bin/python
import os
import sys
import json
import commands
import argparse


## CLI Args
parser = argparse.ArgumentParser(description='Manage Packages for a Hostgroup')
parser.add_argument('--install', '-i', action="store",      dest="install", default=False, help='List of packages to mark as install',   nargs='*')
parser.add_argument('--remove',  '-r', action="store",      dest="remove",  default=False, help='List of packages to mark as remove',    nargs='*')
parser.add_argument('--unset',   '-u', action="store",      dest="unset",   default=False, help='List of packages to mark as unmanaged', nargs='*')
parser.add_argument('--list',    '-l', action="store_true", dest="list",    default=False, help='Return list of current configs')
parser.add_argument('--verbose', '-v', action="store_true", dest="verbose", default=False, help='Verbose output')
results = parser.parse_args()


## Get info
hostgroup = commands.getstatusoutput('get-hostgroup-name')[-1]
cmd = "hammer --output=csv sc-param list --per-page='10000' | grep install_hostgroupapps | cut -d',' -f1"
if results.verbose: print(cmd)
install_param_id = commands.getstatusoutput(cmd)[-1]
cmd = "hammer --output=csv sc-param list --per-page='10000' | grep remove_hostgroupapps  | cut -d',' -f1"
if results.verbose: print(cmd)
remove_param_id = commands.getstatusoutput(cmd)[-1]
try:
  cmd = "hammer --output=json sc-param  info --id "+install_param_id
  if results.verbose: print(cmd)
  installed = json.loads(commands.getstatusoutput(cmd)[-1])
except:
  installed = {}
try:
  cmd = "hammer --output=json sc-param  info --id "+remove_param_id
  if results.verbose: print(cmd)
  removed = json.loads(commands.getstatusoutput(cmd)[-1])
except:
  removed = {}
try: marked_install = installed['Override values']['Values']['1']['Value']
except: marked_install = []
try: marked_remove = removed['Override values']['Values']['1']['Value']
except: marked_remove = []


## Operations
go = False
if results.install:
  go = True
  to_install = marked_install + results.install
  for i in to_install:
    for r in marked_remove:
      if i == r:
        marked_remove.remove(i)
  to_install = list(set(to_install))
  to_remove  = list(set(marked_remove))
if results.remove:
  go = True
  to_remove = marked_remove + results.remove
  for i in marked_install:
    for r in to_remove:
      if i == r:
        marked_install.remove(i)
  to_remove  = list(set(to_remove))
  to_install = list(set(marked_install))
if results.unset:
  go = True
  to_install = marked_install
  to_remove  = marked_remove
  for i in results.unset:
    try: to_install.remove(i)
    except: pass
    try: to_remove.remove(i)
    except: pass
if results.list:
  for i in marked_install:
    print('+%s'%(i))
  for i in marked_remove:
    print('-%s'%(i))


## Execute
if go:
  try:
    cmd = 'hammer sc-param remove-override-value --smart-class-parameter-id '+str(install_param_id)+' --id '+str(installed['Override values']['Values']['1']['Id'])
    if results.verbose: print(cmd)
    os.system(cmd)
  except:
    pass
  try:
    cmd = 'hammer sc-param remove-override-value --smart-class-parameter-id '+str(remove_param_id)+' --id '+str(removed['Override values']['Values']['1']['Id'])
    if results.verbose: print(cmd)
    os.system(cmd)
  except:
    pass
  try:
    cmd = 'hammer sc-param add-override-value --match hostgroup='+hostgroup+' --value \''+json.dumps(to_install)+'\' --smart-class-parameter-id '+str(install_param_id)
    if results.verbose: print(cmd)
    os.system(cmd)
  except:
    pass
  try:
    cmd = 'hammer sc-param add-override-value --match hostgroup='+hostgroup+' --value \''+json.dumps(to_remove)+'\' --smart-class-parameter-id '+str(remove_param_id)
    if results.verbose: print(cmd)
    os.system(cmd)
  except:
    pass







