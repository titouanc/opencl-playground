#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <CL/cl.h>

#define MAX_SOURCE_SIZE 65536

static bool init_cl_called = false;
static cl_context context;
static cl_command_queue command_queue;
static cl_program program;
static cl_kernel mandelbrot;

#define init_cl() if (! init_cl_called) __init_opencl()
static void __init_opencl()
{
    
    fprintf(stderr, "=== Init OpenCL ===\n");

    // Get platform and device information
    cl_platform_id platform_id = NULL;
    cl_device_id device_id = NULL;   
    cl_uint ret_num_devices;
    cl_uint ret_num_platforms;
    
    cl_int ret = clGetPlatformIDs(1, &platform_id, &ret_num_platforms);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "get platform ID failed: %d\n", ret);
        if (ret == CL_INVALID_VALUE)
            fprintf(stderr, "Invalid value\n");
        exit(-1);
    }

    ret = clGetDeviceIDs( platform_id, CL_DEVICE_TYPE_ALL, 1, 
            &device_id, &ret_num_devices);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "get devices failed: %d\n", ret);
        if (ret == CL_INVALID_VALUE)
            fprintf(stderr, "Invalid value\n");
        exit(-1);
    }

    // Create an OpenCL context
    context = clCreateContext( NULL, 1, &device_id, NULL, NULL, &ret);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "Create context failed: %d\n", ret);
        exit(-1);
    }
    fprintf(stderr, "Created context %p\n", (void*) context);

    // Create a command queue
    command_queue = clCreateCommandQueue(context, device_id, 0, &ret);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "Create command queue failed: %d\n", ret);
        exit(-1);
    }
    fprintf(stderr, "Created command queue %p\n", (void*) command_queue);

    // Create a program from the kernel source
    fprintf(stderr, "Reading program ...\n");
    FILE *fp;
    char *source_str;
    size_t source_size;

    fp = fopen("mandelbrot.cl", "r");
    if (!fp) {
        fprintf(stderr, "Failed to load kernel.\n");
        exit(1);
    }
    source_str = (char*)malloc(MAX_SOURCE_SIZE);
    source_size = fread(source_str, 1, MAX_SOURCE_SIZE, fp);
    fclose(fp);

    program = clCreateProgramWithSource(context, 1, (const char **) &source_str, &source_size, &ret);
    fprintf(stderr, "Loaded program source (%d)\n", ret);

    // Build the program
    ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "Unable to build program: %d\n", ret);
        char msg[MAX_SOURCE_SIZE];
        clGetProgramBuildInfo(program, device_id,  CL_PROGRAM_BUILD_LOG, sizeof(msg), (void*)msg, NULL);
        fprintf(stderr, "%s\n", msg);
        exit(-1);
    }

    mandelbrot = clCreateKernel(program, "mandelbrot", &ret);


    printf("=== OpenCL initialized ===\n");
}

bool gpu_draw(
    float *dest, int width, int height,
    float x1, float y1, float x2, float y2
){
    init_cl();
    size_t memsize = width*height*sizeof(float);
    cl_int ret;
    float p1[2] = {x1, y1}, p2[2] = {x2, y2};
    float size[2] = {width, height};

    cl_mem R = clCreateBuffer(context, CL_MEM_WRITE_ONLY, memsize, NULL, &ret);
    if (ret != CL_SUCCESS){
        fprintf(stderr, "Unable to create destination buffer (%d)\n", (int) ret);
        return false;
    }

    clSetKernelArg(mandelbrot, 0, sizeof(cl_mem), (void *)&R);
    clSetKernelArg(mandelbrot, 1, sizeof(p1), (void*)p1);
    clSetKernelArg(mandelbrot, 2, sizeof(p2), (void*)p2);
    clSetKernelArg(mandelbrot, 3, sizeof(size), (void*)size);

    const size_t global_item_size = width*height; 
    const size_t local_item_size = 64; 
    ret = clEnqueueNDRangeKernel(command_queue, mandelbrot, 1, NULL, &global_item_size, &local_item_size, 0, NULL, NULL);
    if (ret != CL_SUCCESS)
        printf("Enqueue OpenCL job failed: %d\n", ret);

    ret = clEnqueueReadBuffer(command_queue, R, CL_TRUE, 0, memsize, dest, 0, NULL, NULL);
    if (ret != CL_SUCCESS)
        printf("Read OpenCL result failed: %d\n", ret);

    clReleaseMemObject(R);
    return true;
}

bool cpu_draw(
    float *dest, int width, int height,
    float x1, float y1, float x2, float y2
){
    float dx = (x2-x1)/width;
    float dy = (y2-y1)/height;
    for (int i=0; i<width; i++){
        float c_re = x1 + i*dx;
        for (int j=0; j<height; j++){
            float c_im = y1 + j*dy;
            float z_re=0, z_im=0;
            for (int k=0; k<100000; k++){
                float re = z_re*z_re - z_im*z_im;
                z_im = 2 * z_re * z_im;
                z_re = re;
                z_re += c_re;
                z_im += c_im;
            }
            dest[j*width+i] = z_im*z_im + z_re*z_re;
        }
    }
    return true;
}



int main(int argc, const char **argv)
{
    int w=192, h=64;
    float *img = malloc(w*h*sizeof(float));
    float x1=-2, y1=1, x2=2, y2=-1;

    if (argc < 2 || strcmp(argv[1], "cpu") == 0){
        cpu_draw(img, w, h, x1, y1, x2, y2);
        puts("CPU DONE");
    } else if (strcmp(argv[1], "gpu") == 0) {
        gpu_draw(img, w, h, x1, y1, x2, y2);
        puts("GPU DONE");
    }

    for (int i=0; i<h; i++){
        for (int j=0; j<w; j++){
            float val = img[i*w+j];
            //printf("%.2f ", val);
            if (val <= 1)
                putchar('*');
            else if (val <= 4)
                putchar('.');
            else
                putchar(' ');
        }
        putchar('\n');
    }
    
    free(img);

    return EXIT_SUCCESS;
}
