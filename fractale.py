import pyopencl as cl
import numpy as np
import subprocess as sp
from PIL import Image

class Renderer:
    # OpenCL Context
    CTX = cl.create_some_context()
    # OpenCL Command Queue
    QUEUE = cl.CommandQueue(CTX)
    # OpenCL Memory Flags
    MF = cl.mem_flags
    # OpenCL Program
    PROGRAM = None

    def __init__(self, width=1920, height=1080, n_iters=1024):
        if not self.PROGRAM:
            prog_source = open('mandelbrot.cl').read()
            if self.CTX.devices[0].double_fp_config:
                prog_source.replace('float', 'double')
            self.PROGRAM = cl.Program(self.CTX, prog_source).build()
        self.width, self.height = width, height
        self.n_iters = n_iters
        self._make_constant_cl_args()

    def _make_constant_cl_args(self):
        self.n_iters_cl = cl.Buffer(
            self.CTX,
            self.MF.READ_ONLY|self.MF.COPY_HOST_PTR,
            hostbuf=np.array([self.n_iters]).astype(np.int32)
        )
        self.size_cl = cl.Buffer(
            self.CTX, 
            self.MF.READ_ONLY|self.MF.COPY_HOST_PTR, 
            hostbuf=np.array((self.width+self.height*1j,)).astype(np.complex64)
        )

        image_fmt = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNSIGNED_INT8)
        self.image_cl = cl.Image(
            self.CTX, 
            self.MF.WRITE_ONLY, image_fmt, 
            shape=(self.width, self.height)
        )

    def _cl_args(self, p1, p2):
        p_cl = tuple(cl.Buffer(
            self.CTX, 
            self.MF.READ_ONLY|self.MF.COPY_HOST_PTR, 
            hostbuf=np.array((x[0]+x[1]*1j,)).astype(np.complex64)
        ) for x in (p1, p2))
        return (self.image_cl,) + p_cl + (self.size_cl, self.n_iters_cl)

    def borders(self, center, width):
        """
        Return two points for the bounding box for an image with center
        given in complex coordinates and width given as a real distance
        """
        ratio = float(self.height)/self.width
        height = width*ratio
        p1 = (center[0]-float(width)/2, center[1]-float(height)/2)
        p2 = (center[0]+float(width)/2, center[1]+float(height)/2)
        return p1, p2

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def ezis(self):
        """
        Yeaaaah, you know that pyOpenCL and Numpy don't agree on dimensions
        order...
        """
        return (self.height, self.width)

    def render(self, center=(-0.5, 0), width=3.2):
        p1, p2 = self.borders(center, width)
        self.PROGRAM.mandelbrot(self.QUEUE, self.size, None, *self._cl_args(p1, p2))
        res = np.ones((self.height, self.width, 4)).astype(np.uint8)
        cl.enqueue_copy(self.QUEUE, res, self.image_cl, origin=(0, 0), region=self.size)
        return res

    def render_png(self, filename, center=(-0.5, 0), width=3.2):
        array = self.render(center, width)
        img = Image.fromarray(array)
        img.save(filename)

    def render_mp4(self, filename, center1, width1, center2, width2, n_frames=500, fps=20):
        dx, dy = (center2[0] - center1[0])/n_frames, (center2[1] - center1[1])/n_frames
        dw = (width2/width1)**(1.0/n_frames)

        command = [ 
            'ffmpeg',
            '-y', # (optional) overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec','rawvideo',
            '-s', '%dx%d' % (self.width, self.height), # size of one frame
            '-pix_fmt', 'rgba',
            '-r', '20', # frames per second
            '-i', '-', # The imput comes from a pipe
            '-an', # Tells FFMPEG not to expect any audio
            '-vcodec', 'libx264',
            filename 
        ]
        pipe = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)

        for i in range(1, n_frames+1):
            x, y = center1[0] + i*dx, center1[1] + i*dy
            w = width1 * dw**i
            frame = self.render((x, y), w)
            pipe.stdin.write(frame.tostring())
            yield i
