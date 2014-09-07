import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from time import time

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)
mf = cl.mem_flags

try:
    program = cl.Program(ctx, open('mandelbrot.cl').read()).build()
except Exception as err:
    print err.message.what()

def borders(CENTER, WIDTH, SIZE):
    # Region to plot
    ratio = float(SIZE[1])/SIZE[0]
    HEIGHT = WIDTH*ratio
    P1 = (CENTER[0]-float(WIDTH)/2, CENTER[1]-float(HEIGHT)/2)
    P2 = (CENTER[0]+float(WIDTH)/2, CENTER[1]+float(HEIGHT)/2)
    return P1, P2

def render_mandelbrot(CENTER=(-0.5, 0), WIDTH=4, SIZE=(1920, 1080)):
    P1, P2 = borders(CENTER, WIDTH, SIZE)
    
    # Arguments
    EZIS = (SIZE[1], SIZE[0])
    args_np = tuple(np.array((arg[0]+arg[1]*1j,)).astype(np.complex64) for arg in (P1, P2, SIZE))
    args_cl = tuple(cl.Buffer(ctx, mf.READ_ONLY|mf.COPY_HOST_PTR, hostbuf=arg) for arg in args_np)

    # Create FHD image, 1 color channel as float32
    image_f = cl.ImageFormat(cl.channel_order.R, cl.channel_type.FLOAT)
    image = cl.Image(ctx, mf.WRITE_ONLY,  image_f, shape=SIZE)

    # Run kernel
    program.mandelbrot(queue, SIZE, None, image, *args_cl)

    # Copy to main memory
    displayable = np.ones(EZIS).astype(np.float32)
    cl.enqueue_copy(queue, displayable, image, origin=(0, 0), region=SIZE)
    return displayable

def make_anim(x=-0.4025, y=0.595, zoom=500):
    movie_dirname = "movie_%f,%f:%d" % (x, y, zoom)
    os.system("mkdir -p %s" % (movie_dirname))

    start = time()

    # Start width
    w = 4.0
    # Center of zoom
    c = (x, y)
    # Resolution
    s = (1280, 720)

    last = time()
    for i in range(zoom):
        frame_name = "%s/frame_%05d.png" % (movie_dirname, i)
        frame = plt.imshow(render_mandelbrot(CENTER=c, WIDTH=w, SIZE=s))
        plt.axis('off')
        plt.savefig(frame_name, pad_inches=0, dpi=300, bbox_inches='tight')
        plt.clf()

        now = time()
        dt = now-last
        last = now
        b = borders(CENTER=c, WIDTH=w, SIZE=s)
        print '[%3d] %2d fps :: %.2f seconds video/%.2f seconds rendering :: %s - %s' % (
            i+1, 1.0/dt, float(i)/20, now-start, b[0], b[1]
        )
        w -= 3*w/100

if __name__ == "__main__":
    from sys import argv
    if len(argv) == 1:
        make_anim()
    elif len(argv) >= 3:
        x = float(argv[1])
        y = float(argv[2])
        make_anim(x, y)

# Interesting points:
# -0.7477855 0.1
# -0.4025, 0.595
