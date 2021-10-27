# generate tilesets for each mulitpolygon ---------------------------------
library(sf)
library(stars)
library(here)
library(glue)
library(mapview)


# paths -------------------------------------------------------------------
path_multipolygons = "../pythonIsochrones/data/multipolygons"
path_austria = "./data/regions/AUT_adm0.sf.rds"

multipolygons = dir(path_multipolygons, pattern = "*.geojson", full.names = T)


# create a raster over austria --------------------------------------------
out_dir = "../pythonIsochrones/data/multipolygons/raster"
if(!dir.exists(out_dir)){
  dir.create(out_dir)
}

for (source in multipolygons) {
  
  # create name for the raster
  bn = basename(source)
  dn = dirname(source)
  dn_out = paste0(dn, .Platform$file.sep, "raster")
  target = paste0(dn_out, "/", sub(".geojson$", replacement = ".tif", bn))
  
  # read vector
  mp = read_sf(source)
    
  # build command 
  cmd = glue("gdal_rasterize -burn 255 -burn 0 -burn 0 -burn 100 -at -tr .005 .005 -ot Byte {source} {target}") #-a_nodata 0 
  system(cmd)
}

