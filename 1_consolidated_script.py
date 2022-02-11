""""""  		  	   		   	 			  		 			 	 	 		 		 	
"""  		  	   		   	 			  		 			 	 	 		 		 		 			  		 			 	 	 		 		 	
Functions to perform varies tasks such as validating the data
and creating the final dataset as a csv
"""  		  	   		   	 			  		 			 	 	 		 		 	
  		  	   		   	 			  		 			 	 	 		 		 	
### Import packages
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import csv
import re
from bs4 import NavigableString
import json
import geopandas as gpd
import descartes
import shapely
import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint

### Import user-defined functions from GitHub
from scrape_object import ncaa_scrape
from geog_object import ncaa_geog
from utils import extract_as_df

### Load supporting files
# Open dedupe_mapping
# User-defined to remove duplicate schools name (see Save dedupe_mapping.ipynb)
with open('dedupe_mapping.json') as json_file:
    dedupe_mapping = json.load(json_file)
    
# Open id_mapping
# Manually defined to match the NCAA Tournament schools to the NCES ID data
id_mapping = pd.read_csv('id_mapping.csv')

# Open lat_long
# From NCES data, reducing the fields to only the ID and geographic data
lat_long = pd.read_csv('lat_long.csv', encoding='latin-1')
lat_long = lat_long.rename(columns = {'UNITID' : 'ID'})

### Iterate through years to create final output

for yr in range(1985,2022):
    if yr == 2020:
        continue
    try:
        scrape = ncaa_scrape(yr, dedupe_mapping)
        scrape.scrape_all()
        #scrape.validate_counts(raise_error = True, verbose = False)
        geog = ncaa_geog(scrape, id_mapping, lat_long)
        geog.handle_data()
        
        if yr == 1985:
            final_df = extract_as_df(geog, 'all')
            final_df = extract_as_df(geog, 's16', final_df)
            final_df = extract_as_df(geog, 'e8', final_df)
            final_df = extract_as_df(geog, 'f4', final_df)
            
        else:
            final_df = extract_as_df(geog, 'all', final_df)
            final_df = extract_as_df(geog, 's16', final_df)
            final_df = extract_as_df(geog, 'e8', final_df)
            final_df = extract_as_df(geog, 'f4', final_df)
        
    except:
        print(yr)

# Save the output as a csv
final_df.to_csv('final_dataset_v02_09_22.csv')
