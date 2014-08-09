#!/usr/bin/python
# many dependencies are all brought in with this import...
from photoboothlib import *

#=============================================================================
# ========================= COMMAND LINE ARGUMENTS ===========================
#=============================================================================
if 'help' in sys.argv or '-h' in sys.argv or '--help' in sys.argv:
	print """
NAME: 
	photobooth.py  -  a photo booth python script

OPTIONS:
	-h,--help,help	print help
	nousecamera	use dummy photos instead of camera (default: USB connected camera)
	nomove		do not move images after processing (default: move)
	lastphoto=xxxx	begin sequence with the provided 4-digit (>=1000) number 
	noincrement	do not increment the image sequence number (default: increment)
	doubleprint	generate the double print (adds time, default: no doubleprint)
	sepia		do composites in sepia tone
	bw		do composites in black and white

DESCRIPTION:
	This python script implements a photo booth where a sequence of four images is 
	taken by a USB-connected camera and processed into various composite images.

	Requires: libgphoto2, python-pygame, piggyphoto (python binding for libgphoto2)
	and graphicsmagick.

"""
	sys.exit()

# use camera or dummy source images...
if 'nousecamera' in sys.argv:
	camera_arg=False
else:
	camera_arg=False

if 'doubleprint' in sys.argv:
	doubleprint=True
else:
	doubleprint=True

# use sepia tone...
tone = ''
if 'sepia' in sys.argv and not('bw' in sys.argv):
	tone = '-sepia'
if 'bw' in sys.argv and not('sepia' in sys.argv):
	tone='-bw'

# move the files when done? Assume true...
move=True
if 'nomove' in sys.argv:
	print 'Not moving files...'
	move=False

# set lastphoto via command line... 
lastphoto=False
for i in sys.argv:
	if 'lastphoto' in i:
		lastphoto = True
		temp = split(i, '=')[1]
		break
if not(lastphoto):
	# this should be rolled into the filename function but for now it's here...
	last = eval(open('lastphoto', 'r').read())
	print 'Change current photo number '+str(last)+'?'
	temp = raw_input( 'Enter valid new number or nothing to keep: ')
if temp not in ['']: 
	last = eval(temp) 
	open('lastphoto', 'w').write(str(last))

# increment output photo index? default is true...
increment=True
if 'noincrement' in sys.argv:
	increment = False
#=============================================================================
# ===================== DONE COMMAND LINE ARGUMENTS ==========================
#=============================================================================



#=============================================================================
# ==================================  MAIN  ==================================
#=============================================================================

# verify command line args...
print 'nousecamera:', repr(camera_arg)
print 'nomove:', repr(not(move))
print 'lastphoto:', last
print 'increment:', repr(increment)
print 'doubleprint:', repr(doubleprint)


for loopy in [1]:


	# keep track of the starting time for some statistics...
	start = time.time()
	
	# get a new filename and print it to the console...
	filename= new_filename(increment=increment)
	print '\r\nnew filename:', filename

	# prime threads for compositing images...
	t_ = []
	t_.append( threading.Thread(target=generate_composite, args=('display'+tone, filename)) )
	if not(doubleprint): t_.append( threading.Thread(target=generate_composite, args=('phone'+tone, filename)) )
	else: t_.append( threading.Thread(target=generate_print, args=('phone'+tone, filename)) )
	# start the queued threads...
	for i in t_: i.start()

	# grab the sequence of images from the camera (or, if specified, dummy images)...
	print 'Grabbing images... '
	#grab_image(filename, i, camera_arg)
	for suffix in ['_a', '_b', '_c', '_d']:
		shellcmd('cp /media/PHOTOBOOTH/raw-images/'+filename+suffix+'.jpg .')
		open(filename+suffix+'_done', 'w').write('done') 

	# wait until all compositing threads are complete...
	living=True
	displayed=False
	while ( living ):# or t_print.isAlive() ): 
		living=False
		time.sleep(1)
		print '    ===> still processing...'	
		for i in t_: 
			if i.isAlive(): living=True

	print '\r\nAll images done:', time.time()-start
	time.sleep(1)

	# clean up the temporary files generated during compositing...
	cleanup_temp_files(filename)

	# move files (default) to redundant locations...
	if move:
		move_files(filename, path='/media/SD4GB/', copy=True)
		move_files(filename, path='/media/files-n-stuff/', copy=True)
		move_files(filename, path='/media/PHOTOBOOTH/', copy=False)

	# print elapsed time to console...
	print '\r\nDone: ', time.time()-start




