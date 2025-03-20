from pyesgf.search import SearchConnection
from pyesgf.search import SearchContext
import os
import pandas as pd
import requests

# --- Access CMIP6 data using esgf-pyclient
# https://esgf-node.llnl.gov/search/cmip6/ --> gives results from more data nodes
# https://esgf-data.dkrz.de/esg-search --> gives results from less data nodes 

os.environ["ESGF_PYCLIENT_NO_FACETS_STAR_WARNING"] = "on"

# Specifying the node from which we want the data search to start. 
# Setting the "distrib" parameter to "True" will expand the data search to other nodes
conn = SearchConnection('https://esgf-node.llnl.gov/esg-search', distrib=True)  

# Indicate that we want CMIP6 data
project = ["CMIP6"]

# Specifying if we want historical data or projection (ssp245, ssp585, etc.)
experiment_id = ["historical"] # "ssp245", "ssp585"

# Specifying the climate variable you are searching for
variable = ["rsds"] # rsdt, tas, ps, sfcWind, hurs, rsds, clt

# Specifying the table_id
table_id = ["day"] # 1hr, 3hr, 6hr, day

# Specifying the variant label
variant_label = ["r1i1p1f1"] 

# Specifying grid label, here I'm using only one for consistency
grid_label = ['gn'] # ,'gr'

# this list below (facets) must contain all the variables you intend to 
# use to filter your search
facets = ["project", "experiment_id", "variable",
          "table_id", "grid_label", "variant_label", "latest", "replica"]

# Launching the search
query = conn.new_context (latest = True, # only get the latest version of dataset
                          replica = False, # avoid getting duplicate dataset in the search result
                          project = project,
                          experiment_id = experiment_id,
                          variable = variable,
                          table_id = table_id,
                          grid_label = grid_label,
                          variant_label = variant_label,
                          facets = facets) # confirm the search criteria we have set

# Calculate the total number of results the search has returned
results_count = query.hit_count 
print (f"The search has returned {results_count} results")

# Starting the extraction of URLs.
for i in range(results_count): # This first loop will iterate over each result
    dataset = query.search(ignore_facet_check=True)[i] # This open a dataset 
    files_list = dataset.file_context().search() # This create a list of files contained in the opened dataset

    for file in files_list: # This loop will iterate over each file of the list to extract their URLs
        urls.append(file.download_url)

    print (f"Results {i+1} out of {results_count} processed")

# Saving the URLs in an Excel spreadsheet
df = pd.DataFrame(urls, columns = ["Links"])

# ----
# This is optional : For dealing with so many links from different models/source,
# it is important to consider same models for all variables.
# Thus, we can drop any models with incomplete variables and outside of our time peirod

# First, let save all of the resulted links to a text file
ff = open(f"your/path/{variable[0]}",'w')
for i in df.Links:
    ff.write(i+'\n')# opening a txt file and saving into it.
ff.close()

# Second, create a backup list for the links
df_backup=[]
f = open(f"your/path/{variable[0]}","r")
for line in f:
    stripped_line = line.strip()
    line_list = stripped_line.split()
    df_backup.append(stripped_line) # opening that txt file and appending to df_backup
f.close()

# Now, let's define our time period in order to avoid downloading some years 
# outside of our time period
min_period=19800101 # timestemp for daily data
max_period=20141231 # 

# Create a new list 
new_list = []
source_list = []
kk = len(df_backup)
for url in df_backup:
    fname = url.split('/')[-1] # splitting file name from url
    try: # avoid any ValueError from file name
        yr_min = int(fname.split('_')[-1].split('-')[0]) #;print(yr_min) # split time period of netcdf file
        yr_max = int(fname.split('_')[-1].split('-')[-1].split('.')[0])  #;print(yr_max)       
    except ValueError:
        pass
    if (yr_min < max_period) and (yr_max > min_period): # if file is inside our time period
            new_list.append(url) # appending to the new_list  
    else:
        print(yr_min,' to ',yr_max)

new_list

# Save the new list to a new data frame
df_urls = pd.DataFrame(new_list, columns = ["Links"])
df_urls.to_excel(f"your/path/{variable[0]}.xlsx")

# This is END of the code
