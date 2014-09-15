from fractale import Renderer
from time import time

if __name__ == "__main__":
    import argparse
    optparser = argparse.ArgumentParser(description="Render a Manndelbrot video")
    optparser.add_argument(
        '-x', '--x', type=float,
        action='store', dest='x', default=0,
        help='Real part of the center point'
    )
    optparser.add_argument(
        '-y', '--y', type=float,
        action='store', dest='y', default=0,
        help='Imaginary part of the center point'
    )
    optparser.add_argument(
        '-s', '--scale', type=float,
        action='store', dest='w', default=4,
        help='Width (real part in complex plane)'
    )
    optparser.add_argument(
        '-o', '--output', type=str,
        action='store', dest='filename', default="render%d.png"%(time()),
        help='Destination filename'
    )
    optparser.add_argument(
        '-i', '--niters', type=int,
        action='store', dest='n_iters', default=1024,
        help='Maximum number of convergence iterations for each pixel'
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

    r = Renderer(OPTIONS.width, OPTIONS.height, OPTIONS.n_iters)
    r.render_png(
        OPTIONS.filename, 
        center=(OPTIONS.x, OPTIONS.y), 
        width=OPTIONS.w
    )
