__constant sampler_t smp = CLK_NORMALIZED_COORDS_FALSE | //Natural coordinates
                           CLK_ADDRESS_CLAMP | //Clamp to zeros
                           CLK_FILTER_NEAREST; //Don't interpolate

inline float2 complex_prod(float2 z1, float2 z2)
{
    return (float2)(z1.x*z2.x - z1.y*z2.y, z1.x*z2.y + z1.y*z2.x);
}

inline float4 value2color(float val)
{
    float4 res = (float4) (0, 0, 0, 1);
    val *= 2*M_PI_F;

    if (val > 3*M_PI_2_F || val < M_PI_2_F)
        res.s0 = cos(val);

    if (M_PI_2_F/3 < val && val < 7*M_PI_2_F/3)
        res.s1 = cos(val-2*M_PI_F/3);

    if (5*M_PI_2_F/3 < val && val < 11*M_PI_2_F/3)
        res.s2 = cos(val-4*M_PI_F/3);

    return res;
}

// __kernel void colorize(
//     __write_only image2d_t dest,
//     __read_only image2d_t source
// ){
//     int2 p = (int2) (get_global_id(0), get_global_id(1));
//     float val = read_imagef(source, smp, p);
//     write_imagef(dest, p, value2color(val));
// }

__kernel void mandelbrot(
    __write_only image2d_t dest, 
    __global float2 *p1, __global float2 *p2,
    __global float2 *size, __global int *n_iters
){
    int iter_max = *n_iters;
    /* x,y coordinates in dest image */
    int2 p = (int2) (get_global_id(0), get_global_id(1));

    /* Iteration variables */
    float2 c, z;
    /* re,im in complex plane between p1 && p2 */
    c = *p1 + ((float2) (p.x, p.y))*(*p2-*p1) / *size;
    /* Z0 = 0 */
    z = (float2) (0, 0);

    for (int i=0; i<iter_max; i++){
        /* z^2 */
        z = complex_prod(z, z);

        /* Add c */
        z += c;
        if (length(z) > 4.0f){
            write_imagef(dest, p, 1.0f-((float) i)/iter_max);
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
