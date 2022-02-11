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

# Format data as df to save as csv
def extract_as_df(geog_obj, round_str, append_df = None):
    if round_str == 'all':
        base_df = geog_obj.all_df.copy()
    elif round_str == 's16':
        base_df = geog_obj.s16_df.copy()
    elif round_str == 'e8':
        base_df = geog_obj.e8_df.copy()
    elif round_str == 'f4':
        base_df = geog_obj.f4_df.copy()
        
    round_dict = {'all' : 'All', 's16' : 'Sweet 16', 'e8' : 'Elite 8', 'f4' : 'Final 4'}
        
    base_df['Year'] = geog_obj.yr
    base_df['Round'] = round_dict[round_str]
    base_df['Is_Center'] = 'N'
    
    # Append round centroid
    if round_str == 'all':
        centroid = geog_obj.centroid_df_all.copy()
    elif round_str == 's16':
        centroid = geog_obj.centroid_df_s16.copy()
    elif round_str == 'e8':
        centroid = geog_obj.centroid_df_e8.copy()
    elif round_str == 'f4':
        centroid = geog_obj.centroid_df_f4.copy()
    
    centroid_append = {'SCHOOL' : 'Centroid', 'ID' : 0, 'LONGITUD' : centroid.at[0, 'geometry'].x, 
                   'LATITUDE' : centroid.at[0, 'geometry'].y,
                  'Year' : geog_obj.yr, 'Round' : round_dict[round_str], 'Is_Center' : 'Y'}


    if append_df is None:
        return_df = base_df.copy()
        return_df = return_df.append(centroid_append, ignore_index=True)
    else:
        return_df = pd.concat([append_df, base_df])
        return_df = return_df.append(centroid_append, ignore_index=True)
        
    return return_df
