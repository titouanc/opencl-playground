import os
from time import time
from sys import stdout
from fractale import Renderer
import subprocess as sp
import numpy as np

W, H = 1280, 720
r = Renderer(W, H)

def make_anim(x=-0.4025, y=0.595, zoom=500):
    command = [ 
        'ffmpeg',
        '-y', # (optional) overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', '%dx%d' % (W, H), # size of one frame
        '-pix_fmt', 'gray',
        '-r', '20', # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'libx264',
        'movie_%f-%f-%d.mp4' % (x, y, zoom) 
    ]
    pipe = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)
    
    # Start width
    w = 4.0
    # Center of zoom
    c = (x, y)
    # Resolution
    s = (1920, 1080)

    start = time()
    last = time()
    for i in range(zoom):
        frame = (r.render((x, y), w)*255).astype(np.uint8)
        try:
            pipe.stdin.write(frame.tostring())
        except IOError as err:
            message = pipe.stderr.read()
            print "ERROR:", message
            exit(1)

        now = time()
        dt = now-last
        last = now
        fps = 1.0/dt
        eta = (zoom-i-1)*dt
        stdout.write('\r[%3d/%d] %.2f fps :: Video: %.2f sec :: Elapsed: %.2f sec :: ETA: %.2f sec     ' % (
            i+1, zoom, fps, float(i)/20, now-start, eta
        ))
        stdout.flush()
        w -= 3*w/100
    print

if __name__ == "__main__":
    # Interesting points:
    # -0.7477855 0.1
    # -0.4025, 0.595

    from sys import argv
    if len(argv) == 1:
        make_anim()
    elif len(argv) >= 3:
        x = float(argv[1])
        y = float(argv[2])
        make_anim(x, y)
