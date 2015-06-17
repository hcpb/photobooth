#!/usr/bin/python
# many dependencies are all brought in with this import...
#from photoboothlib import *
import os
import time
from string import split
import Image, ImageDraw

def shellcmd(command):
	print ' =>', command
	os.system(command)

#=============================================================================
# ==================================  MAIN  ==================================
#=============================================================================

# lists used below...
printed = []
existing = []

# change directory to shared directory root of photo booth files...
os.chdir('/volumes/Photobooth')
#os.chdir('/home/r14793/photobooth/')
# add filenames to existing list and sort...
#for i in os.listdir('for-display'):
#	print i,
#	if os.path.isfile('for-display/'+i): existing.append(i)
existing = os.listdir('for-display')
existing.sort()
print repr(existing)
print
#filename = split(existing[-1], '_')[0]
#print 'filename:', filename

while (1):

	# watch for new file in for-display
	new = False
	while not(new):
		tmp = os.listdir('for-display')
		tmp.sort()
		if len(tmp)>0: 
			newest = tmp[-1]
			#print newest
			if newest not in existing:
				new = True # so we fall out of while loop...
				existing.append(newest)
			else: 
				time.sleep(2)
		else:
			time.sleep(2)

	start = time.time()

	# grab the actual single strip filename, which may have a color suffix...
	tmp = os.listdir('for-print')
	tmp.sort()
	filename = tmp[-1]

	# send print job here...
	shellcmd('lp -d Canon_iP7200_series -o media=Custom.4.2x6.2in '+'/Volumes/Photobooth/for-print/'+filename)

	# then save to printed list...
	printed.append(filename)
	

