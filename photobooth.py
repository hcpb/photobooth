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
	camera_arg=True

if 'doubleprint' in sys.argv:
	doubleprint=True
else:
	doubleprint=False

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
print 'nomove:', repr(move)
print 'lastphoto:', last
print 'increment:', repr(increment)
print 'doubleprint:', repr(doubleprint)

pygame.init()
screen = pygame.display.set_mode(size)
#toggle_fullscreen()

while (1):

	# wait for key push.
	# bb = raw_input('\r\nHit return to continue...')
	showtext(screen, "Push any button", 100)

	key = waitforkey([K_g, K_r, K_y])
	if key == K_y: tone='-sepia'
	if key == K_r: tone='-bw'
	if key == K_g: tone =''

	fillscreen(screen, black)

	showtext(screen, "Four photos will be taken", 75)
	time.sleep(2.5)
	fillscreen(screen, black)

	# keep track of the starting time for some statistics...
	start = time.time()
	
	# get a new filename and print it to the console...
	filename= new_filename(increment=increment)
	print '\r\nnew filename:', filename

	# *** for PIL instead of graphicsmagick... ***
	imDisplay = Image.new('RGBA', (1280, 720), 'white')
	imPrint = Image.new('RGBA', (2000, 6000), 'white')
	dispbox = [ (124, 12, 628, 348), (124, 373, 628, 709), (652, 12, 1156, 348), (652, 373, 1156, 709) ]
	printbox= [ (120, 996, 1876, 2160), (120, 2248, 1876, 3412), (120, 3500, 1876, 4664), (120, 4752, 1876, 5916) ]
	# ****************************

	# grab the sequence of images from the camera (or, if specified, dummy images)...
	for i in range(4):
		showtext(screen, 'Image: '+str(4-i), 100)
		time.sleep(1.0)
		print 
		print 'Grabbing image: ', i+1
		fillscreen(screen, black)
		grab_image2(filename, i, camera_arg)
		displayimage(screen, filename+'_'+suffix[i]+'.jpg', camerasize, cameraloc)
		time.sleep(3)
		# assemble incremental composite...
		bb =  Image.open(filename+'_'+suffix[i] + '.jpg')
		print bb.size
		imDisplay.paste(bb.resize( (504, 336), Image.ANTIALIAS), dispbox[i])
		imPrint.paste(bb.resize( (1756, 1164), Image.ANTIALIAS), printbox[i])

	# add emblems to composites...
	tmp = Image.open('images/overlay-disp.png').resize( (233, 233), Image.ANTIALIAS )
	print tmp.size, tmp.mode
	imDisplay.paste( tmp, (522, 243, 755, 476), mask=tmp )
	tmp = Image.open('images/overlay-phone.png').resize( (1500, 941), Image.ANTIALIAS )
	print tmp.size, tmp.mode
	imPrint.paste( tmp, (250, 50, 1750, 991), mask=tmp )
	# save composites...
	imDisplay.save(filename+'_display.jpg', 'JPEG', quality=98)
	imPrint.save(filename+'_phone.jpg', 'JPEG', quality=90)
	imDouble = Image.new('RGB', (4000, 6000), 'white')
	# generate double strip for printing...
	imDouble.paste( imPrint, (0, 0, 2000, 6000) )
	imDouble.paste( imPrint, (2000, 0, 4000, 6000) )
	draw = ImageDraw.Draw(imDouble)
	draw.line( (2000, 0, 2000, 6000), fill='rgb(0,0,0)', width=2)
	del draw
	imDouble.save(filename+'_print.jpg', 'JPEG', quality=90)



	time.sleep(1)

	# clean up the temporary files generated during compositing...
	cleanup_temp_files(filename)

	# print elapsed time to console...
	print '\r\nDone: ', time.time()-start



