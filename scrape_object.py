""""""  		  	   		   	 			  		 			 	 	 		 		 	
"""  		  	   		   	 			  		 			 	 	 		 		 		 			  		 			 	 	 		 		 	
Function to define an object that scrapes Wikipedia page to return
a year's NCAA tournament teams by round (all participants, Sweet 16,
Elite 8 and Final 4).

Requires passing a dictionary to dedupe school names, which is saved in
GitHub repo as dedupe_mapping.json

Example usage:
ncaa_17 = ncaa_scrape(2017, dedupe_mapping)
ncaa_17.scrape_all()
"""  		  	   		   	 			  		 			 	 	 		 		 	
  		  	   		   	 			  		 			 	 	 		 		 	
# Import packages
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import csv
import re
from bs4 import NavigableString
import json

# Define scrape object
class ncaa_scrape:
    
    def __init__(self, yr, dedupe_mapping):
        self.yr = yr
        if yr == 2010:
            self.url = '''https://en.wikipedia.org/wiki/2010_NCAA_Division_I_Men%27s_Basketball_Tournament:_qualifying_teams'''
        else:
            self.url = 'https://en.wikipedia.org/wiki/{0}_NCAA_Division_I_Men%27s_Basketball_Tournament'.format(yr)
        self.dedupe_mapping = dedupe_mapping

        city_list_all = dedupe_mapping['city_list_all']
        city_list_s16 = dedupe_mapping['city_list_s16']
        city_list_e8 = dedupe_mapping['city_list_e8']

        if str(yr) in list(city_list_all.keys()):
            self.city_list_all = city_list_all[str(yr)]
        else:
            self.city_list_all = ["None"]

        if str(yr) in list(city_list_s16.keys()):
            self.city_list_s16 = city_list_s16[str(yr)]
        else:
            self.city_list_s16 = ""

        if str(yr) in list(city_list_e8.keys()):
            self.city_list_e8 = city_list_e8[str(yr)]
        else:
            self.city_list_e8 = ""
        
    def get_soup(self, opt_url = None):
        if opt_url is None:
            req = urllib.request.urlopen(self.url)
        else:
            req = urllib.request.urlopen(opt_url)
        return BeautifulSoup(req, 'html.parser')
        
    def get_tourney_teams(self):
    
        table_index = 0
        if self.yr <= 1994:
            table_index = 2
        else:
            table_index = 1

        if self.yr < 2007:
            keyword_terms = ['Teams', 'teams']
        elif self.yr >= 2007 and self.yr < 2010:
            keyword_terms = ['grouping and seeding']
        elif self.yr >= 2010 and self.yr < 2013:
            keyword_terms = ['region and seeding']
        elif self.yr >= 2013:
            keyword_terms = ['Tournament seeds']

        if self.yr < 2007:
            play_in = True
        elif self.yr >= 2009: #2014:
            play_in = True
        else:
            play_in = False

        soup = self.get_soup()

        self.schools = []

        for header in soup.select('h2, h3'):
            if any(term in header.text for term in keyword_terms):
                table = header.findNextSibling()
            else:
                continue

        try:
            while len(self.schools) < 64:
                if self.yr < 2019:
                    self.schools = self.extract_from_table(table, self.schools, table_index, play_in)
                    table = table.findNextSibling()
                else:
                    self.schools = self.extract_from_table_19(table, self.schools, table_index, play_in)
                    table = table.findNextSibling()

        except Exception as e:
            print("Error Year {0}".format(yr))
            print(e)

        #return schools
        
    def extract_from_table(self, table, schools_list, table_index, play_in):
        cell_lens = []
        if isinstance(table, NavigableString):
            pass
        else:
            rows = table.find_all('tr')

            for row in rows:
                if isinstance(row, NavigableString):
                    continue
                else:
                    if len(row.find_all('td')) == 0:
                        continue
                    else:
                        cells = row.find_all('td')

                        # determine length of cells to account for play-in
                        if len(cells) > 1 and len(cells) < 10:
                            cell_lens.append(len(cells))
                        else:
                            continue

                        # If play-in
                        if play_in:
                            if len(cells) == np.median(np.array(cell_lens)):
                                name = cells[table_index].text
                            elif len(cells) == np.median(np.array(cell_lens)) - 1:
                                name = cells[table_index - 1].text
                        else:
                            name = cells[table_index].text
                        schools_list.append(name.strip())

        return schools_list
    
    
    def extract_from_table_19(self, table, schools_list, table_index, play_in):
        if isinstance(table, NavigableString):
            pass
        else:
            rows = table.find_all('tr')

            for row in rows:
                if 'Seed' not in row.th.text:
                    name = row.th.text
                    schools_list.append(name.strip())

        return schools_list
        
    
    def clean_and_dedupe(self):
        cleaned = []
        for team in self.schools:
            if team in list(self.dedupe_mapping.keys()):
                team = self.dedupe_mapping[team]

            if team not in self.city_list_all:
                cleaned.append(team)
            
        self.cleaned = cleaned
    
    def get_s16_e8(self):
        alt_url = 'https://en.wikipedia.org/wiki/{0}_NCAA_Division_I_Men%27s_Basketball_Tournament'.format(self.yr)
        soup = self.get_soup(alt_url)

        keyword_terms = ["East Regional", "West Regional", "Midwest Regional", 
                         "South Regional", "Southeast Regional", "Southwest Regional"]

        if self.yr >= 2004 and self.yr <= 2006:
            keyword_terms = ["East Rutherford Regional", "St. Louis Regional", "Atlanta Regional",
                             "Phoenix Regional", "Minneapolis Regional", "Oakland Regional",
                             "Washington, D.C. Regional",
                            "Albuquerque Regional", "Chicago Regional", "Syracuse Regional",
                            "Austin Regional"]

        if self.yr == 2001:
            keyword_terms = ["East regional", "West regional", "Midwest regional", 
                         "South regional", "Southeast regional", "Southwest regional"]

        bracket_text = []
        count_dict = {}
        s16 = []
        e8 = []

        for header in soup.select('h2,h3'):
            if any(term in header.text for term in keyword_terms):
                table = header.findNextSibling()

                # Add one table skip for 2005
                if self.yr == 2005 and "Syracuse Regional" in header.text:
                    table = table.findNextSibling()

                for row in table.find_all('tr'):
                    for cell in row.find_all('td'):
                        if len(cell.text) > 0:
                            try:
                                num = int(cell.text)
                            except:
                                text = cell.text
                                text = text.strip()
                                if len(text) > 0:
                                    bracket_text.append(text)

        for text in bracket_text:
            # Correct for 1988 (UK) 2008 (WSU) S16; 1992 (Ohio St) for E8
            if text == "Washington St.":
                text = "Washington State"
            elif text == "Kentucky#":
                text = "Kentucky"
            elif self.yr == 1992 and text == 'Ohio St':
                text = "Ohio State"

            if text in count_dict.keys():
                count_dict[text] = count_dict[text] + 1
            else:
                count_dict[text] = 1  

        for k, v in count_dict.items():
            if v >= 3:
                s16.append(k)
            if v >= 4:
                e8.append(k)

        return s16, e8, count_dict

    def clean_s16_e8(self, s16, e8):
        s16_cleaned = []
        e8_cleaned = []

        for item in s16:
            if item in self.city_list_s16:
                continue
            elif item in list(self.dedupe_mapping.keys()):
                item = self.dedupe_mapping[item]
                s16_cleaned.append(item)
            elif item in self.cleaned: #self.cleaned_set
                s16_cleaned.append(item)

        for item in e8:
            if item in self.city_list_e8:
                continue
            elif item in list(self.dedupe_mapping.keys()):
                item = self.dedupe_mapping[item]
                e8_cleaned.append(item)
            elif item in self.cleaned: #self.cleaned_set
                e8_cleaned.append(item)

        return s16_cleaned, e8_cleaned
                
    def get_f4(self):
        
        alt_url = 'https://en.wikipedia.org/wiki/{0}_NCAA_Division_I_Men%27s_Basketball_Tournament'.format(self.yr)
        soup = self.get_soup(alt_url)

        keyword_terms = ["Final Four"]

        if self.yr == 1999:
            keyword_terms = ["St. Petersburg"]

        if self.yr == 2015:
            keyword_terms = ["Lucas Oil Stadium"]

        if self.yr == 2016:
            keyword_terms = ["NRG Stadium"]

        if self.yr == 2017:
            keyword_terms = ['University of Phoenix Stadium']

        if self.yr == 2018:
            keyword_terms = ['Alamodome']

        bracket_text = []
        count_dict = {}
    
        for header in soup.select('h3'): #('h2,h3')
            if any(term in header.text for term in keyword_terms):
                table = header.findNextSibling()

                while len(bracket_text) < 4:

                    for row in table.find_all('tr'):
                        for cell in row.find_all('td'):
                            if len(cell.text) > 0:
                                try:
                                    num = int(cell.text)
                                except:
                                    text = cell.text
                                    text = text.strip()
                                    if len(text) > 0:
                                        bracket_text.append(text)

                    table = table.findNextSibling()

        return bracket_text
    
    def clean_f4(self, f4):
        f4_cleaned = set()

        for item in f4:
            if item in list(self.dedupe_mapping.keys()):
                item = self.dedupe_mapping[item]
                f4_cleaned.add(item)
            elif item in self.cleaned: #self.cleaned_set
                f4_cleaned.add(item)

        return f4_cleaned
    
    def validate_counts(self, verbose = False, raise_error = False):

        if self.yr < 2001:
            team_count = 64
        elif self.yr >= 2001 and self.yr < 2011:
            team_count = 65
        else:
            team_count = 68
    
        if verbose:
            print("Total team count{0}".format(len(self.cleaned)))
            print("Sweet 16 count: {0}".format(len(self.s16)))
            print("Elite 8 count: {0}".format(len(self.e8)))
            print("Final 4 count: {0}".format(len(self.f4)))
        
        if raise_error:
            assert len(self.cleaned) == team_count, "Total team count invalid, got {0}".format(len(self.cleaned))
            assert len(self.s16) == 16, "Sweet 16 count invalid, got {0}".format(len(self.s16))
            assert len(self.e8) == 8, "Elite 8 count invalid, got {0}".format(len(self.e8))
            assert len(self.f4) == 4, "Final 4 count invalid, got {0}".format(len(self.f4))
    
    def scrape_all(self):
        self.get_tourney_teams()
        self.clean_and_dedupe()
        s16_pre, e8_pre, _ = self.get_s16_e8()
        self.s16, self.e8 = self.clean_s16_e8(s16_pre, e8_pre)
        f4_pre = self.get_f4()
        self.f4 = self.clean_f4(f4_pre)
        
