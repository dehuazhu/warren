import pandas as pd
import time, math, sys, pickle, os
from data.bloomberg_data.check_bloomberg_data import check_bloomberg_company, get_ignore_list


class BloombergCompany:
    """
    Datastructure of managing all resources belonging to a single Bloomberg company.
    """
    def __init__(self, name, check_result, data):
        self.name = name
        self.data = data
        
        # This feature carries the qualification result that 
        # reports on the completeness and correctness of the dataset.
        self.check_result = check_result


def make_bloomberg_company(company):
    """
    This function takes the path of the folder of a Bloomberg company and 
    transforms it into a Bloomberg Company object.
    """
    
    # Load the function that qualifies the data-set's completeness and correctnes. 
    # In case of disqualification, the result is simply flagged, but wouldn't hinder the process.
    check_result = check_bloomberg_company(company, get_ignore_list())
    
    # The different files are stored in a dictionary.
    data = {}
    
    # Looping through the excel files in the folder. 
    for company_file in os.scandir(company.path):
        company_file_path = company_file.path
        
        # Each excel file is first checked for it's excistence, then directly imported by 
        # a built-in function into padas dataframes.
        if 'rawdata_annual.' in company_file.name:
            data['rawdata_annual'] = pd.read_excel(company_file_path, sheet_name=None)
        if 'rawdata_quarterly.' in company_file.name:
            data['rawdata_quarterly'] = pd.read_excel(company_file_path, sheet_name=None)
        if 'ownership.' in company_file.name:
            data['ownership'] = pd.read_excel(company_file_path, sheet_name=None)
        if 'ownership_insider.' in company_file.name:
            data['ownership_insider'] = pd.read_excel(company_file_path, sheet_name=None)
            
    # The result is consolidated into a custom class.
    bloomberg_company = BloombergCompany(company.name, check_result, data)
    
    return bloomberg_company


def make_bloomberg_database(bloomberg_directory, pickle_directory):
    """
    The main function of generating the bloomberg database, which is a dictionary.
    """
    
    # Use a timer here, as this process takes quite long. With me it takes about 4 minutes now.
    start_time = time.time()
    
    
    number_of_companies = len(os.listdir(bloomberg_directory))
    company_counter = 0
    bloomberg_companies = {}
    ignore_list = get_ignore_list()
    
    # Looping through the path all companies, which are already manually sorted into individual folders.
    for company in os.scandir(bloomberg_directory):
        
        # Some companies are downloaded from Bloomberg for our own interest.
        # Those are not to be included in the main database.
        # There are also companies with incomplete Bloomberg Financial Analyser dataset.
        if company.name in ignore_list:
            continue
        
        company_counter += 1
        
        # A lazy hack to refresh the line
        filler = '                        '
        print(f'Importing Bloomberg company {company_counter}/{number_of_companies}: {company.name}' + filler, end='\r')
        
        # This is the main function of converting excel files into a pandas data frame based structure.
        bloomberg_company = make_bloomberg_company(company)
        
        # Append the dataframes into the dictionary.
        bloomberg_companies[bloomberg_company.name] = bloomberg_company
        
    # Log the time taken for the process and display it on screen.
    # Hopefully, this routine can one day be parallelized.
    function_call_time = math.ceil(time.time() - start_time)
    print(f'All Bloomberg data imported. It took {function_call_time} seconds.')
    
    # Dump the database into the pickle file.
    bloomberg_companies_file_name = pickle_directory
    bloomberg_companies_file = open(bloomberg_companies_file_name, 'wb')
    pickle.dump(bloomberg_companies, bloomberg_companies_file)
    bloomberg_companies_file.close()
    print(f'Result saved in {bloomberg_companies_file_name}')


if __name__ == '__main__':
    bloomberg_directory = 'BloombergData'
    pickle_directory = 'bloomberg_companies.pkl'
    make_bloomberg_database(bloomberg_directory, pickle_directory)
