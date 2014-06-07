/*
 * mandelbrodt(dest, region, width)
 *     Compute the serie Zn = (Zn-1)^2 + c; Z0 = 0 at given point
 * @param dest Destination float area
 * @param p1 One of the corner of the region to be plotted in form (real, imaginary)
 * @param p2 The other corner in form (real, imaginary)
 * @oaram size Size of the destination, in pixels, as int2 (width, height)
 */
__kernel void mandelbrot(
    __global __write_only float *dest, 
    float2 p1, float2 p2, 
    float2 size
){
    int id = get_global_id(0);
    float2 c, z;

    c.s0 = id%(int)size.s0;
    c.s1 = id/(int)size.s0;
    c = p1 + c*(p2-p1)/size;

    z.s0 = z.s1 = 0;

    for (int i=0; i<100000; i++){
        /* Complex Z^2 */
        float re = z.s0*z.s0 - z.s1*z.s1;
        z.s1 = 2 * z.s0 * z.s1;
        z.s0 = re;

        /* Add c */
        z += c;
    }

    /* Complex norm */
    dest[id] = z.s0*z.s0 + z.s1*z.s1;
}
