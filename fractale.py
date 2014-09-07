import pyopencl as cl
import numpy as np

class Renderer:
    # OpenCL Context
    CTX = cl.create_some_context()
    # OpenCL Command Queue
    QUEUE = cl.CommandQueue(CTX)
    # OpenCL Memory Flags
    MF = cl.mem_flags
    # OpenCL Program
    PROGRAM = cl.Program(CTX, open('mandelbrot.cl').read()).build()

    def __init__(self, width=1920, height=1080, n_iters=1024):
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

        image_fmt = cl.ImageFormat(cl.channel_order.R, cl.channel_type.FLOAT)
        self.image_cl = cl.Image(
            self.CTX, 
            self.MF.WRITE_ONLY, image_fmt, 
            shape=self.size
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
        res = np.ones(self.ezis).astype(np.float32)
        cl.enqueue_copy(self.QUEUE, res, self.image_cl, origin=(0, 0), region=self.size)
        return res

if __name__ == "__main__":
    from PIL import Image
    Image.fromarray(Renderer().render()*256).convert("RGB").save("test.png")
