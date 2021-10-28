# get differences from raster and color only difference -------------------
library(stars)
library(sf)
library(tidyverse)
library(glue)
library(here)
library(purrr)
library(scales)


# paths -------------------------------------------------------------------
raster_dir = "../svelte_poi/public/data/raster/"
data_dir = here("data/rasters_new_colors"); if(!dir.exists(data_dir)) dir.create(data_dir, recursive = T)

# get all rasters ---------------------------------------------------------
raster_paths = dir(raster_dir, pattern = ".tif", full.names = T)
rasters = map(raster_paths, ~stack(.x))

# get the second values that are in the paths
minutes = str_match(raster_paths, "\\/(\\d+)_")[,2]  %>% as.numeric()
minutes_order = minutes %>% order()

# order the list based on these values
rasters = rasters[minutes_order] %>% setNames(., minutes %>% sort())

# create colormap ---------------------------------------------------------
ramp = colour_ramp(c("blue", "green", "red"))
cols = ramp(seq(0, 1, length = length(rasters)))

# get the rgb values
rgbs = col2rgb(cols) %>% as.data.frame()
colnames(rgbs) = 1:9 %>% as.character()


# go through the rasters  -------------------------------------------------

for (i in seq_along(rasters)) {
  
  f = here(data_dir, glue("{names(rasters)[[i]]}.tif"))
   
  if(i == 1){
    
    # make the raster a dataframe
    df = as.data.frame(rasters[[i]]) %>% rename(val = 4)
    
    # get the bands as columns
    df_wide = df %>% pivot_wider(names_from = band, values_from = val) %>% 
      rename(red = `1`,
             gren = `2`,
             blue = `3`,
             alpha = `4`)
    
    reds = which(df_wide$red != 0)
    
    # set those to the right rgb value
    rgb = rgbs[,i]
    df_new = df %>% split(., .$band) %>% imap(., function(v,j){
      
      if(j == 4){
        print("returning the alpha band as is")
        return(v)
      }else{
        v$val[reds] = rgb[as.numeric(j)]
        return(v)
      }
    }) %>% bind_rows()
    rasters[[i]][[1]] = df_new
    
    
  }else{
    
    # check for the indexes of the red values of the previsous ones 
    df_prev = as.data.frame(rasters[[i-1]])
    red_prev = which(df_prev$X300_all.tif != 0)
    
    # set these in the next one to 0
    
    
  }
  
  
  
   
}




