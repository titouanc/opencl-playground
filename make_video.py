import os
from time import time
from sys import stdout
from fractale import Renderer


def make_anim(args_constructor, *args, **kwargs):
    n_frames = kwargs['n_frames']
    start = time()
    last = time()
    last_eta = n_frames
    for i in Renderer(*args_constructor).render_mp4(*args, **kwargs):
        now = time()
        dt = now-last
        last = now
        fps = 1.0/dt
        eta = ((n_frames-i-1)*dt + last_eta)/2
        stdout.write('\r[%3d/%d] %.2f fps :: Video: %.2f sec :: Elapsed: %.2f sec :: ETA: %.2f sec     ' % (
            i+1, n_frames, fps, float(i)/20, now-start, eta
        ))
        stdout.flush()
        last_eta = eta
    print
    print "Saved as", kwargs['filename']

if __name__ == "__main__":
    import argparse
    optparser = argparse.ArgumentParser(description="Render a Manndelbrot video")
    optparser.add_argument(
        '-x1', '--x1', type=float,
        action='store', dest='x1', default=-0.7477855,
        help='Real part of the start point'
    )
    optparser.add_argument(
        '-y1', '--y1', type=float,
        action='store', dest='y1', default=0.1,
        help='Imaginary part of the start point'
    )
    optparser.add_argument(
        '-s1', '--scale1', type=float,
        action='store', dest='w1', default=0.1,
        help='Starting width (real part in complex plane)'
    )
    optparser.add_argument(
        '-x2', '--x2', type=float,
        action='store', dest='x2', default=None,
        help='Real part of the arrival point'
    )
    optparser.add_argument(
        '-y2', '--y2', type=float,
        action='store', dest='y2', default=None,
        help='Imaginary part of the arrival point'
    )
    optparser.add_argument(
        '-s2', '--scale2', type=float,
        action='store', dest='w2', default=0.0001,
        help='Arrival width (real part in complex plane)'
    )
    optparser.add_argument(
        '-o', '--output', type=str,
        action='store', dest='filename', default="movie%d.mp4"%(time()),
        help='Destination filename'
    )
    optparser.add_argument(
        '-n', '--nframes', type=int,
        action='store', dest='n_frames', default=500,
        help='Number of frames to compute'
    )
    optparser.add_argument(
        '-i', '--niters', type=int,
        action='store', dest='n_iters', default=1024,
        help='Maximum number of convergence iterations for each pixel'
    )
    optparser.add_argument(
        '-f', '--fps', type=int,
        action='store', dest='fps', default=25,
        help='Number of frames per second'
    )
    optparser.add_argument(
        '-W', '--width', type=int,
        action='store', dest='width', default=1280,
        help='Width of result video'
    )
    optparser.add_argument(
        '-H', '--height', type=int,
        action='store', dest='height', default=720,
        help='Height of result video'
    )

    OPTIONS = optparser.parse_args()
    if OPTIONS.x2 is None:
        OPTIONS.x2 = OPTIONS.x1

    if OPTIONS.y2 is None:
        OPTIONS.y2 = OPTIONS.y1

    make_anim(
        (OPTIONS.width, OPTIONS.height, OPTIONS.n_iters),
        center1=(OPTIONS.x1, OPTIONS.y1), width1=OPTIONS.w1,
        center2=(OPTIONS.x2, OPTIONS.y2), width2=OPTIONS.w2,
        filename=OPTIONS.filename, fps=OPTIONS.fps,
        n_frames=OPTIONS.n_frames
    )
