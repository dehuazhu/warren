# import the main project folder  
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

# import data modules
import data.make_google_sheet_database
import data.bloomberg_data.make_bloomberg_database
from pdb import set_trace

# import standard python modules
import pickle


class Company:
    """
    Datastructure for a company. It contains both ZWDB and Bloomberg data.
    """
    def __init__(self, name, zw_data, bloomberg_data = []):
        self.name = name
        self.zw_data = zw_data
        self.bloomberg_data = bloomberg_data

class Database:
    """
    Datastructure for the database.
    """
    def __init__(self, companies, companies_without_bloomberg_data, paths):
        self.companies = companies
        self.companies_without_bloomberg_data = companies_without_bloomberg_data
        self.paths = paths

        
def get_paths():
    """
    Store all paths for sub-databases and sources
    """
    paths = {}
    paths['bloomberg_rawdata_directory'] = 'data/bloomberg_data/BloombergData'
    paths['bloomberg_pickel_directory'] = 'data/bloomberg_data/bloomberg_companies.pkl'
    paths['zw_google_sheet_url'] = 'https://docs.google.com/spreadsheets/d/1blyB_oDQ0GM4e8x-uVG9AXttNuLAcK_lwdT0VvDi8Uk/edit#gid=0'
    paths['zw_pickel_directory'] = 'data/zw_data/zw_companies.pkl'
    paths['factset_google_sheet_url'] = 'https://docs.google.com/spreadsheets/d/11bx2QqvAa9IkRjTsiGlvQQEp45LcVfS3n4ThCYS8wxg/edit#gid=1078945644'
    paths['factset_pickel_directory'] = 'data/factset_data/factset_companies.pkl'
    paths['database_directory'] = 'data/database.pkl'
    return paths


def refresh_zw_database():
    """
    Function to activate the ZWDB module
    """ 
    paths = get_paths()
    data.make_google_sheet_database.make_google_sheet_database(
        paths['zw_google_sheet_url'],
        paths['zw_pickel_directory'])


def refresh_bloomberg_database():
    """
    Fuction to activate the Bloomberg module
    """
    paths = get_paths()
    data.bloomberg_data.make_bloomberg_database.make_bloomberg_database(
        paths['bloomberg_rawdata_directory'],
        paths['bloomberg_pickel_directory'])


def make_consolidated_database():
    """
    This function takes all pickle files of sub-databases and consolidates
    them into the main database pickle.
    """
    # load path for pickle destinations and sources
    paths=get_paths()
    
    # Load the pickle files of sub-databases
    bloomberg_companies   = pickle.load(open(paths['bloomberg_pickel_directory'], 'rb'))
    zw_companies          = pickle.load(open(paths['zw_pickel_directory'], 'rb'))
    
    # Use the dictionary data format as end format.
    companies = {}
    
    # Also carry the ZWDB campanies which could not be matched with the Bloomberg database. 
    companies_without_bloomberg_data = []
    
    # Create an object for each company, and insert it into the dictionary 'companies'
    for company_name in zw_companies:
        zw_data = zw_companies[company_name]
        
        # Try to match the ZWDB company with the corresponding company in the Bloomberg database. 
        # If the match fails, put in a dummy '[]' and log it in 'companies_without_bloomberg_data'
        try:
            bloomberg_data = bloomberg_companies[company_name]
        except:
            bloomberg_data = []
            companies_without_bloomberg_data.append(company_name)
            
        # Append the dictionary by the current company
        companies[company_name] = Company(company_name, 
                                          zw_data = zw_data,
                                          bloomberg_data = bloomberg_data,)
        
    # Dump everything in pickle 
    database = Database(companies, companies_without_bloomberg_data, paths)
    database_file = open(paths['database_directory'], 'wb')
    pickle.dump(database, database_file)
    database_file.close()
    print('Created master database at' + paths['database_directory'] )


def import_database(flag_refresh_zw_database = False,
                    flag_refresh_bloomberg_database = False,
                    flag_refresh_factset_database = False):
    """
    This is the main function for accessing warren's database. 
    The parameters are flag setting which part of the databse needs to be refreshed.
    If all flags are left at default value, it simply loads the database.pkl file.
    """ 
    
    # load path for pickle destinations and sources
    paths = get_paths()
    
    # refresh the sub-databases according to flag settings
    if flag_refresh_zw_database:        refresh_zw_database()
    if flag_refresh_bloomberg_database: refresh_bloomberg_database()
    if flag_refresh_factset_database:   print('factset_database not implemented (yet)')
        
    # if any sub-database has been refreshed, also remake the consolidated database
    if (flag_refresh_zw_database or flag_refresh_bloomberg_database or flag_refresh_factset_database):
        make_consolidated_database()
    
    # store the consolidated database as pickel file
    with open(paths['database_directory'],'rb') as database_file:
        database = pickle.load(database_file)
    return database
    

if __name__ == '__main__':
    make_consolidated_database()
    database = import_database()