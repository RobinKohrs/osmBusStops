import os
import glob
import subprocess


def compress(in_dir, out_dir):
    files = [os.path.join(in_dir, x)
             for x in os.listdir(in_dir) if x.endswith(".tif")]
    for f in files:
        filename, extenstion = os.path.splitext(f)
        outfile = os.path.join(
            out_dir, filename.split("/")[-1]) + "_compress.tif"

        cmd = f"gdal_translate -ot Byte -co COMPRESS=DEFLATE -co PREDICTOR=2 {f} {outfile}"
        # print(cmd)
        subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    data_dir = "./data/multipolygons/raster/"
    out_dir = "./data/multipolygons/raster/compress"
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    compress(data_dir, out_dir)
