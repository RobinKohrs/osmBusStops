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
  f = here(data_dir, glue("{name}_new.gpkg"))
  if (!file.exists(f)) {
    osm_bb = getbb(name, featuretype = "settlement")
    data = st_bbox(x) %>% opq(timeout = 60) %>% add_osm_feature(key = "public_transport") %>% osmdata_sf() %>% .[["osm_points"]]
    data = data %>% select(osm_id, name, bus, highway, public_transport)
    write_sf(data, f)
    data
  } else{
    data = read_sf(f)
    data
  }
}) %>% rbindlist(idcol = "region") %>% st_as_sf()


# read shape for austria ---------------------------------------------------------------
public_transport = public_transport[austria, ]

# filter the data ---------------------------------------------------------
public_transport %>%
  mutate(x = st_coordinates(.)[, 1],
         y = st_coordinates(.)[, 2]) %>%
  st_drop_geometry() %>%
  distinct(name, .keep_all = T) %>%
  st_as_sf(., coords = c("x", "y"), crs = 4326) %>% 
  mutate(
    id  = row_number()
  ) -> filt


st_write(filt, here("data/filtered.gpkg"))
st_write(filt, "../pythonIsochrones/stations2.geojson")
st_write(public_transport, here("data/all.gpkg"))


# get the missing ones ----------------------------------------------------
a = filt$name
b = st_read("../../qgis/isochrones_poi/filtered.gpkg") %>% pull(name)
mis = which(!a %in% b)
miss = filt[mis, ]
n = str_match(files, "(\\d+)_")[,2] %>% as.numeric() # the max id of the already existing
r = (max + 1):(max + nrow(miss)) + 1
miss = miss %>% mutate(id = as.integer(r))
st_write(miss, "../pythonIsochrones/missing.geojson")

# write out the points to the python dir  ----------------------------------
pts_path = "../pythonIsochrones/stations.geojson"
if(file.exists(pts_path)){
  file.remove(pts_path)
}

st_write(filt, pts_path)























