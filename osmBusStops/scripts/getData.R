library(tidyverse)
library(osmdata)
library(mapview)
library(sf)
library(rnaturalearth)
library(GADMTools)
library(mapview)
library(ISOcodes)
library(here)
library(glue)
library(data.table)

# get the data ------------------------------------------------------------


# get the isocode of austria
ISOcodes::ISO_3166_1 %>% 
  filter(str_detect(Name, "Austria")) %>% pull(Alpha_3) -> isocode

data_dir = here("data/regions/")
if(!dir.exists(data_dir)){
  dir.create(data_dir, recursive = T)
}


# get the shape for austria
austria = gadm_sf.loadCountries(isocode, level=0, basefile = "./data/regions/")$sf

# get the shape for the level 1 regions
regions = gadm_sf.loadCountries(isocode, level=1, basefile = "./data/regions/")$sf

public_transport = regions %>% split(., .$NAME_1) %>% lapply(., function(x) {
  name = x$NAME_1
  cat("\nGetting data for: ", name, "\r")
  f = here(data_dir, glue("{name}.gpkg"))
  if (!file.exists(f)) {
    osm_bb = getbb(name, featuretype = "region")
    data = osm_bb %>% opq(timeout = 60) %>% add_osm_feature(key = "public_transport") %>% osmdata_sf() %>% .[["osm_points"]]
    data = data %>% select(osm_id, name, bus, highway, public_transport)
    write_sf(data, f)
    data
  } else{
    data = read_sf(f)
    data
  }
}) %>% rbindlist(idcol = "region") %>% st_as_sf()




# shape of austria --------------------------------------------------------
grid = st_make_grid(austria, cellsize = .8, square = F)
grid_centroids = st_centroid(grid) %>% st_as_sf()
pts = grid_centroids[austria, ] %>% mutate(id = row_number())


# write out the points ----------------------------------------------------
pts_path = here("data/stations.geojson")
if(file.exists(pts_path)){
  file.remove(pts_path)
}
st_write(pts, pts_path)























