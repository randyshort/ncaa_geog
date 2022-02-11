""""""  		  	   		   	 			  		 			 	 	 		 		 	
"""  		  	   		   	 			  		 			 	 	 		 		 		 			  		 			 	 	 		 		 	
Function to define an object that joins school name with geography data
and calculates the geographic centroid of each round.

Requires passing a two pandas dataframes stored as CSV:
1) id_mapping.csv, which maps school names to the geography id
2) lat_long.csv, which was the latitude and longitude of each school

Also requires passing the ncaa_scrape object defined in scrape_object.py

Example usage:
geog_17 = ncaa_geog(ncaa_17, id_mapping, lat_long)
geog_17.handle_data()
"""  		  	   		   	 			  		 			 	 	 		 		 	
  		  	   		   	 			  		 			 	 	 		 		 	
# Import packages
import numpy as np
import pandas as pd
import csv
import json
import geopandas as gpd
import descartes
import shapely
import matplotlib.pyplot as plt
from shapely.geometry import MultiPoint

# Define geog object
class ncaa_geog:
    
    def __init__(self, scrape, id_mapping, lat_long_list):
        self.yr = scrape.yr
        self.team_list = scrape.cleaned
        self.s16 = scrape.s16
        self.e8 = scrape.e8
        self.f4 = scrape.f4
        self.yr = scrape.yr
        self.id_list = id_mapping
        self.lat_long_list = lat_long_list
        
    def join_data(self):
        
        # Create df of all teams
        self.all_df = pd.DataFrame(self.team_list, columns = ['SCHOOL'])
        self.all_df = pd.merge(self.all_df, self.id_list[['SCHOOL', 'ID']], on=['SCHOOL'])
        self.all_df['ID'] = pd.to_numeric(self.all_df["ID"])
        self.all_df = pd.merge(self.all_df, self.lat_long_list[['ID', 'LONGITUD', 'LATITUDE']], on = ['ID'])
        
        # Create df of S16 teams
        self.s16_df = pd.DataFrame(self.s16, columns = ['SCHOOL'])
        self.s16_df = pd.merge(self.s16_df, self.id_list[['SCHOOL', 'ID']], on=['SCHOOL'])
        self.s16_df['ID'] = pd.to_numeric(self.s16_df["ID"])
        self.s16_df = pd.merge(self.s16_df, self.lat_long_list[['ID', 'LONGITUD', 'LATITUDE']], on = ['ID'])        

        # Create df of E8 teams
        self.e8_df = pd.DataFrame(self.e8, columns = ['SCHOOL'])
        self.e8_df = pd.merge(self.e8_df, self.id_list[['SCHOOL', 'ID']], on=['SCHOOL'])
        self.e8_df['ID'] = pd.to_numeric(self.e8_df["ID"])
        self.e8_df = pd.merge(self.e8_df, self.lat_long_list[['ID', 'LONGITUD', 'LATITUDE']], on = ['ID'])
        
        # Create df of F4 teams
        self.f4_df = pd.DataFrame(list(self.f4), columns = ['SCHOOL'])
        self.f4_df = pd.merge(self.f4_df, self.id_list[['SCHOOL', 'ID']], on=['SCHOOL'])
        self.f4_df['ID'] = pd.to_numeric(self.f4_df["ID"])
        self.f4_df = pd.merge(self.f4_df, self.lat_long_list[['ID', 'LONGITUD', 'LATITUDE']], on = ['ID'])
        
    def create_geo_dfs(self):
        
        # Create geo df for all teams
        longs_all = self.all_df['LONGITUD'].values
        lats_all = self.all_df['LATITUDE'].values
        self.geometry_all = [shapely.geometry.Point(xy) for xy in zip(longs_all,lats_all)]
        self.gdf_all = gpd.GeoDataFrame(geometry = self.geometry_all)
        
        # Create geo df for S16 teams
        longs_s16 = self.s16_df['LONGITUD'].values
        lats_s16 = self.s16_df['LATITUDE'].values
        self.geometry_s16 = [shapely.geometry.Point(xy) for xy in zip(longs_s16,lats_s16)]
        self.gdf_s16 = gpd.GeoDataFrame(geometry = self.geometry_s16)
        
        # Create geo df for E8 teams
        longs_e8 = self.e8_df['LONGITUD'].values
        lats_e8 = self.e8_df['LATITUDE'].values
        self.geometry_e8 = [shapely.geometry.Point(xy) for xy in zip(longs_e8,lats_e8)]
        self.gdf_e8 = gpd.GeoDataFrame(geometry = self.geometry_e8)
        
        # Create geo df for F4 teams
        longs_f4 = self.f4_df['LONGITUD'].values
        lats_f4 = self.f4_df['LATITUDE'].values
        self.geometry_f4 = [shapely.geometry.Point(xy) for xy in zip(longs_f4,lats_f4)]
        self.gdf_f4 = gpd.GeoDataFrame(geometry = self.geometry_f4)
        
    def get_us_map(self):
        shapefile = gpd.read_file("tl_2021_us_state/tl_2021_us_state.shp")
        to_keep = ['West Virginia', 'Florida', 'Illinois', 'Minnesota', 'Maryland',
         'Rhode Island', 'Idaho', 'New Hampshire', 'North Carolina', 'Vermont',
         'Connecticut', 'Delaware', 'New Mexico', 'California', 'New Jersey',
         'Wisconsin', 'Oregon', 'Nebraska', 'Pennsylvania', 'Washington', 'Louisiana',
         'Georgia', 'Alabama', 'Utah', 'Ohio', 'Texas', 'Colorado', 'South Carolina',
         'Oklahoma', 'Tennessee', 'Wyoming', 'North Dakota', 'Kentucky',
        'Maine', 'New York',
         'Nevada','Michigan', 'Arkansas', 'Mississippi',
         'Missouri' ,'Montana', 'Kansas', 'Indiana', 'South Dakota',
         'Massachusetts', 'Virginia', 'District of Columbia', 'Iowa', 'Arizona']
        
        self.state_map = shapefile[shapefile.NAME.isin(to_keep)]
        
    def calc_centroids(self, as_df = True):
        
        # Calc centroid for all teams
        self.points_all = MultiPoint(self.geometry_all)
        self.centroid_all = self.points_all.centroid
        self.representative_all = self.points_all.representative_point()
        
        if as_df:
            clat = [self.points_all.centroid.y]
            clong = [self.points_all.centroid.x]
            geo_temp = [shapely.geometry.Point(xy) for xy in zip(clong,clat)]
            self.centroid_df_all = gpd.GeoDataFrame(geometry = geo_temp)
            
        # Calc centroid for S16 teams
        self.points_s16 = MultiPoint(self.geometry_s16)
        self.centroid_s16 = self.points_s16.centroid
        self.representative_s16 = self.points_s16.representative_point()
        
        if as_df:
            clat = [self.points_s16.centroid.y]
            clong = [self.points_s16.centroid.x]
            geo_temp = [shapely.geometry.Point(xy) for xy in zip(clong,clat)]
            self.centroid_df_s16 = gpd.GeoDataFrame(geometry = geo_temp)
            
        # Calc centroid for E8 teams
        self.points_e8 = MultiPoint(self.geometry_e8)
        self.centroid_e8 = self.points_e8.centroid
        self.representative_e8 = self.points_e8.representative_point()
        
        if as_df:
            clat = [self.points_e8.centroid.y]
            clong = [self.points_e8.centroid.x]
            geo_temp = [shapely.geometry.Point(xy) for xy in zip(clong,clat)]
            self.centroid_df_e8 = gpd.GeoDataFrame(geometry = geo_temp)
            
        # Calc centroid for F4 teams
        self.points_f4 = MultiPoint(self.geometry_f4)
        self.centroid_f4 = self.points_f4.centroid
        self.representative_f4 = self.points_f4.representative_point()
        
        if as_df:
            clat = [self.points_f4.centroid.y]
            clong = [self.points_f4.centroid.x]
            geo_temp = [shapely.geometry.Point(xy) for xy in zip(clong,clat)]
            self.centroid_df_f4 = gpd.GeoDataFrame(geometry = geo_temp)
                
    def plot(self, usage, w_centroid = True, title = None):
        
        assert usage in ['all', 's16', 'e8', 'f4'], "Invalid usage. Use one of ['all', 's16', 'e8', 'f4']"
        
        if usage == 'all':
            plot_df = self.gdf_all
            plot_centroid = self.centroid_df_all
        elif usage == 's16':
            plot_df = self.gdf_s16
            plot_centroid = self.centroid_df_s16
        elif usage == 'e8':
            plot_df = self.gdf_e8
            plot_centroid = self.centroid_df_e8
        elif usage == 'f4':
            plot_df = self.gdf_f4
            plot_centroid = self.centroid_df_f4
        
        ax = self.state_map.plot(color='white', edgecolor='black', figsize = [20,12])
        plot_df.plot(ax = ax, marker='o', color='red', markersize=20)
        if w_centroid:
            plot_centroid.plot(ax = ax, marker='o', color='b', markersize=20)
            
        if title is not None:
            plt.title(title)
            
        plt.show()
        
    def handle_data(self):
        self.join_data()
        self.create_geo_dfs()
        self.get_us_map()
        self.calc_centroids()
        
