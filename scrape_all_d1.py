""""""  		  	   		   	 			  		 			 	 	 		 		 	
"""  		  	   		   	 			  		 			 	 	 		 		 		 			  		 			 	 	 		 		 	
Function to scrape all D1 teams from Wikipedia

User can change optional parameters to return the dataframe,
but default is to save a csv at the specified file name.
"""  		  	   		   	 			  		 			 	 	 		 		 	
  		  	   		   	 			  		 			 	 	 		 		 	
# Import packages
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import csv
import re
from bs4 import NavigableString

# Define function
def scrape_all_d1(file_name, save_csv = True, return_df = False):
    
    url = 'https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_men%27s_basketball_programs'
    
    soup = get_soup(url)
    
    table = soup.find('table')
    
    team_dict = {}

    rows = table.find_all('tr')

    for row in rows:

        if len(row.find_all('td')) == 0:
            continue
        else:
            cells = row.find_all('td')
            team = cells[0].text.strip()
            ncaa = cells[4].text.strip()
            f4 = cells[5].text.strip()

            team_dict[team] = {'ncaa': ncaa, 'f4': f4}
            
    as_df = pd.DataFrame.from_dict(team_dict)
    
    if save_csv:
        as_df.T.to_csv(file_name) # 'all_d1_teams.csv'
        
    if return_df:
        return as_df.T
