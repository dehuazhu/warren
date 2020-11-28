import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import os, time, math, sys, pickle
import data.zw_data.sanity_check
from pdb import set_trace

class GoogleSheetRawData:
    """
    This class...
    1) downloads the metric-based ZWDB google sheet from a given url,
    2) Converts the sheets into pandas dataframe,
    3) Stores some key metadata, useful for the the conversion into a company-based datastructure.
    """
    
    def __init__(self, google_sheet_url):
        self.google_sheet_url = google_sheet_url
        
        # It takes the private key from David to access the google sheet. 
        # Still a very bad security practice, until we find a better solution.
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('.credentials.json')
        
        sys.stdout.write("\033[K")
        print(f'Downloading google sheet workbook from {google_sheet_url}')
        
        # Call functions to convert the google workbook into a dictionary of pandas dataframe.
        # Each dataframe represents a single google worksheet.
        self.client = gspread.authorize(self.credentials)
        self.workbook = self.client.open_by_url(self.google_sheet_url) 
        self.worksheets = self.make_worksheets_dictionary()
        self.number_of_worksheets = len(self.worksheets)
        
        # Save a list of company names, useful later for the conversion into a company-based data structure.
        self.names_of_companies = self.get_names_of_companies()
        self.number_of_companies = len(self.names_of_companies)
        
        print(f'The database has been downloaded with {self.number_of_companies} companies and {self.number_of_worksheets} worksheets.')

    def make_worksheets_dictionary(self):
        """
        This function runs through the google worksheets and gives a dictionary with pandas dataframes.
        """
        
        worksheets_dictionary = {}
        worksheets_raw = self.workbook.worksheets()
        number_of_worksheets = len(worksheets_raw)
        worksheet_counter = 0
        
        # Looping through the worksheets
        for worksheet in worksheets_raw:        
            worksheet_counter += 1

            # A lazy hack to refresh the line
            filler = '                   '
            print(f'Importing worksheet {worksheet_counter}/{number_of_worksheets}: {worksheet.title}' + filler, end='\r')
            
            # The worksheet's content is here converted into a numpy array.
            # It is an intermediate step before the conversion into pandas dataframe.
            worksheet_array = np.array(worksheet.get_all_values())
            
            # Make the pandas dataframe. The index ranges are necessary to strip of 'noise-columns' and 'noise-rows'
            dataframe = pd.DataFrame(data = worksheet_array[1:,1:],
                        index   = worksheet_array[1:,0],
                        columns = worksheet_array[0,1:])
            # Append the dictionary by the dataframe
            worksheets_dictionary[worksheet.title] = dataframe
        return worksheets_dictionary
    
    
    def get_names_of_companies(self):
        """
        Make a quick scan through the first sheet 'GeneralInformation' to save a list of companies.
        """
        
        names_of_companies = self.worksheets['GeneralInformation']['Company Name']
        return names_of_companies
        

class GoogleSheetCompany:
    """
    The datastructure containing all information of a company from ZWDB.
    """
    def __init__(self, name, row_number_consistent, sanity_check_passed, company_row_number, data):
        self.name = name
        self.row_number_consistent = row_number_consistent
        self.sanity_check_passed = sanity_check_passed
        self.company_row_number = company_row_number 
        self.data = data

 
def make_google_sheet_company(name_of_company, google_sheet_raw_data):
    """
    Core algorithm of extracting a single company from all sheets in the google workbook.
    It then prepares the information in pandas dataframes in a plotting-friendly fashion.
    """
    
    names_of_companies     = google_sheet_raw_data.names_of_companies
    
    # The company will be iterated by row number instead of searching for the company in each sheet. 
    # This increases the code efficiency, but requires a check to guarantee that the row number is correct for all sheets.
    company_row_number     = int(names_of_companies[names_of_companies == name_of_company].index.values[0]) - 1
    row_number_consistent  = True
    
    # Store 'general_information' as a stand-alone element. 
    general_information    = google_sheet_raw_data.worksheets['GeneralInformation'][company_row_number:company_row_number+1]
    
    # Loop through all worksheet and extract the companies' row and consilidate the rows into a new pandas dataframe
    for worksheet_name in google_sheet_raw_data.worksheets:
        
        # Remove the two 'special' worksheets.
        if ('GeneralInformation' in worksheet_name) or ('Sanity_Check' in worksheet_name):
            continue
        
        # Sanity check to make sure that the row number is correct for the current sheet.
        # If the row number is wrong, the company data is still stored, but an error flag with be saved and a warning message is diplayed.
        if google_sheet_raw_data.worksheets[worksheet_name]['Company Name'][company_row_number] != name_of_company:
            print(f'WARNING: for company {name_of_company} the row number in worksheet {worksheet_name} does not match!')
            row_number_consistent = False
        rawdata_line = google_sheet_raw_data.worksheets[worksheet_name][company_row_number:company_row_number+1]
        
        # Drop the companies' name and currency as those are reporten in the 'general information'
        # Sometimes, sheets don't contain currency, like 'employees', or 'number of shares'.
        # This situation is catched here.
        try:
            rawdata_line = rawdata_line.drop(columns=['Company Name', 'Currency'])
        except:
            rawdata_line = rawdata_line.drop(columns=['Company Name'])
                
        # Add a front column with the metrics now becoming the name of 'rows'.
        rawdata_line.insert(0,'metric',worksheet_name)
        
        # Separate between annual and quarterly metrics and make two stand-alone dataframes
        if 'Annual' in worksheet_name:
            
            # Create a new dataframe if it's the first worksheet, otherwise append.
            if 'rawdata_annual' not in locals():
                rawdata_annual = rawdata_line  
            else:
                rawdata_annual = pd.concat([rawdata_annual,rawdata_line])
                
        if 'Quarterly' in worksheet_name:
            
            # Create a new dataframe if it's the first worksheet, otherwise append.
            if 'rawdata_quarterly' not in locals():
                rawdata_quarterly = rawdata_line  
            else:
                rawdata_quarterly = pd.concat([rawdata_quarterly,rawdata_line])
                
    # Putting all dataframes of the company into a single dictionary.
    data = {
        'general_information': general_information,
        'rawdata_annual': rawdata_annual,
        'rawdata_quarterly': rawdata_quarterly
    }
    
    # sanity-checking the companies entries for completeness and correctness
    sanity_check_passed = True
    # sanity_check_passed, details_of_sanity_check = zw_data_sanity_check.sanity_check(data)
    
    # Consolidate metadata, sanity check results, and the main dataframes into a single object.
    google_sheet_company = GoogleSheetCompany(name = name_of_company,
                                              row_number_consistent = row_number_consistent,
                                              sanity_check_passed = sanity_check_passed,
                                              company_row_number = company_row_number,
                                              data = data)  
    return google_sheet_company


def make_google_sheet_companies(google_sheet_raw_data):
    """
    Takes the ZWDB 'one metric per sheet' format and converts it into 
    'one company per sheet' format.
    """
    
    company_counter = 0
   
    # Use dictionary as data structure.
    google_sheet_companies = {}
    
    # Looping through companies
    for name_of_company in google_sheet_raw_data.names_of_companies:
        company_counter += 1

        # A lazy hack to refresh the line
        filler = '                           '
        print(f'Extracting company {company_counter}/{google_sheet_raw_data.number_of_companies}: {name_of_company}' + filler, end='\r')
        
        # Activate the core algorithm of extracting a single company and append the dictionary with it.
        google_sheet_company                      = make_google_sheet_company(name_of_company, google_sheet_raw_data)
        google_sheet_companies[name_of_company]   = google_sheet_company
        
    return google_sheet_companies


def make_google_sheet_database(google_sheet_url, google_sheet_companies_file_path):
    """
    The master function to make the google sheet database.
    """
   
    # Download the ZWDB in the format as it is in pandas datafram format.
    google_sheet_raw_data   = GoogleSheetRawData(google_sheet_url)
    
    # Convert the raw ZWDB from 'one metric per sheet' to 'one company per sheet'. 
    google_sheet_companies  = make_google_sheet_companies(google_sheet_raw_data)
    
    # A lazy hack to refresh the line
    filler = '                           '
    print('All google sheets data imported.' + filler)
    
    # Dump everything in pickle.
    google_sheet_companies_file = open(google_sheet_companies_file_path, 'wb')
    pickle.dump(google_sheet_companies, google_sheet_companies_file)
    google_sheet_companies_file.close()
    print(f'Result saved in {google_sheet_companies_file_path}')


if __name__ == '__main__':
    zw_google_sheet_url = 'https://docs.google.com/spreadsheets/d/1blyB_oDQ0GM4e8x-uVG9AXttNuLAcK_lwdT0VvDi8Uk/edit#gid=0'
    zw_google_sheet_companies_file_path = 'zw_companies.pkl'
    make_google_sheet_database(zw_google_sheet_url, zw_google_sheet_companies_file_path)
