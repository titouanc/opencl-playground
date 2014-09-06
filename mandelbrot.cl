inline float2 complex_prod(float2 z1, float2 z2)
{
    return (float2)(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

__kernel void mandelbrot(
    __write_only image2d_t dest, 
    __global float2 *p1, __global float2 *p2,
    __global float2 *size
){
    /* x,y coordinates in dest image */
    int2 p = (int2) (get_global_id(0), get_global_id(1));

    /* Iteration variables */
    float2 c, z;
    /* re,im in complex plane between p1 && p2 */
    c = *p1 + ((float2) (p.x, p.y))*(*p2-*p1) / *size;
    /* Z0 = 0 */
    z = (float2) (0, 0);

    for (int i=0; i<256; i++){
        /* z^2 */
        z = complex_prod(z, z);

        /* Add c */
        z += c;
        if (length(z) > 4.0){
            write_imagef(dest, p, 1.0-((float) i)/256.0);
            return;
        }
    }

    write_imagef(dest, p, 0);
}

__kernel void mandeltest(
    __write_only image2d_t dest, 
    float2 p1, float2 p2,
    float2 size
){
    /* x,y coordinates in dest image */
    int2 p = (int2) (get_global_id(0), get_global_id(1));
    float2 r = (float2) (p.x, p.y);

    write_imagef(dest, p, length(r));
}
