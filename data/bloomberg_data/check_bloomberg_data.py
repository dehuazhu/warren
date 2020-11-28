import os
import pandas as pd
from pdb import set_trace

def get_ignore_list():
    ignore_list = [
            'BBBiotech',
            'PrivateEquityHolding',
            'RoyalDutchShell',
            'Nebag',
            '11BitStudios',
            'Formulafirst',
            'CastlePrivateEquity',
            'HBMHealthcareInvestments',
            'SchweizerischeNationalbank',
            'ENRRussiaInvest',
            'AlpineSelect',
            'BellFoodGroup',
            'CastleAlternativeInvest',
            'Alcon',
            'Siemens',
            'SiemensEnergy',
            'TomTom'
            ]
    return ignore_list

def four_files_in_folder():
    directory = 'BloombergData'
    all_checks_passed = 0
    for entry in os.scandir(directory):
        subpath = entry.path
        number_of_subfiles = 0
        isFile = os.path.isfile(subpath)
        if isFile:
            continue
        for subentry in os.scandir(subpath):
            number_of_subfiles = number_of_subfiles + 1
        if number_of_subfiles < 4:
            print('Missing file in ' + entry.path)
            all_checks_passed = all_checks_passed + 1
        if number_of_subfiles > 4:
            print('Too many files in ' + entry.path)
            all_checks_passed = all_checks_passed + 1

    if all_checks_passed == 0:
        return True
    return False

def all_files_of_right_company():
    directory = 'BloombergData'
    all_checks_passed = 0
    for entry in os.scandir(directory):
        subpath = entry.path
        number_of_subfiles = 0
        isFile = os.path.isfile(subpath)
        if isFile:
            continue
        print(entry)
        for subentry in os.scandir(subpath):
            name_file = os.path.basename(subentry.path)
            df = pd.read_excel(subentry, sheet_name=None)
            if "ownership" in name_file:
                # ToDo
                continue
            first_sheet = next(iter(df))
            name_of_company = df[first_sheet].iloc[0,0]
            print(name_of_company)


    if all_checks_passed == 0:
        return True
    return False


def no_random_files():
    directory = 'BloombergData'
    all_checks_passed = 0
    for entry in os.scandir(directory):
        isFile = os.path.isfile(entry.path)
        if isFile:
            all_checks_passed = all_checks_passed + 1

    if all_checks_passed == 0:
        print('No random files in bloomberg folder')
        return True
    print('There are %d random files which are not in folders' %all_checks_passed)
    return False


def check_rawdata_name(company_name, company_file_path):
    df = pd.read_excel(company_file_path, sheet_name=None)
    first_sheet = next(iter(df))
    # name_of_company_in_file = df[first_sheet].iloc[0,0]
    name_of_company_in_file = df['Per Share'].iloc[0,0]
    name_of_company_in_file = name_of_company_in_file.replace(" ", "").replace("-", "").lower()
    company_name = company_name.replace(" ", "").replace("-", "").lower()
    if company_name.lower() in name_of_company_in_file.lower():
        return True
    return False

def check_critical_rawdata_sheets(df):
    result = False
    if ('Per Share' in df) \
            and ('Stock Value' in df) \
            and ('Income - As Reported' in df) \
            and (('Income - GAAP' in df) or ('Income Statement' in df))\
            and (('Bal Sheet - Standardized' in df) or ( 'Balance Sheet' in df))\
            and ('Bal Sheet - As Reported' in df)\
            and ('Cash Flow - As Reported' in df)\
            and (('Cash Flow - Standardized' in df) or ('Cash Flow Statement' in df)):
                result = True
    if result == False: set_trace()
    return result

def check_signal_words(df):
    '''
    see if there are any signal words like 'Requesting Data' or 'Daily Capacity'
    '''
    result = True
    for sheet_name in df:
        current = df[sheet_name]
        if ('Requesting Data' in current.values) or ('Daily' in current.values):
            result = False
    return result

def check_rawdata_file(company_name, company_file_path):
    result = False

    correct_name            = check_rawdata_name(company_name, company_file_path)
    df                      = pd.read_excel(company_file_path, sheet_name=None)
    correct_critical_sheets = check_critical_rawdata_sheets(df)
    no_signal_words         = check_signal_words(df)

    result  = correct_name and correct_critical_sheets
    return result


def check_ownership_file(directory_name, company_directory_path):
    result = False
    df = pd.read_excel(company_directory_path)
    db_name = df['Unnamed: 4'][5].replace(' ','')
    if directory_name in db_name: result = True
    return result

def check_bloomberg_company(company, ignore_list):
    check_rawdata_annual    = False 
    check_rawdata_quarterly = False 
    check_ownership         = False
    check_ownership_insider = False

    if company.name in ignore_list:
        check_rawdata_annual    = True 
        check_rawdata_quarterly = True 
        check_ownership         = True
        check_ownership_insider = True

    else:
        for company_file in os.scandir(company.path):
            if 'rawdata_annual.' in company_file.name:
                if check_rawdata_file(company.name, company_file.path):
                    check_rawdata_annual = True
            if 'rawdata_quarterly.' in company_file.name:
                if check_rawdata_file(company.name, company_file.path):
                    check_rawdata_quarterly = True
            if 'ownership.' in company_file.name:
                if check_ownership_file(company.name, company_file.path):
                    check_ownership = True
            if 'ownership_insider.' in company_file.name:
                if check_ownership_file(company.name, company_file.path):
                    check_ownership_insider = True

    if check_rawdata_annual is False:
        print(company_path + ': missing/corrupt rawdata_annual')
    if check_rawdata_quarterly is False:
        print(company_path + ': missing/corrupt rawdata_quarterly')
    if check_ownership is False:
        print(company_path + ': missing/corrupt ownership')
    if check_ownership_insider is False:
        print(company_path + ': missing/corrupt ownership_insider')
    
    return check_rawdata_annual and check_rawdata_quarterly and check_ownership and check_ownership_insider


def check_bloomberg_data(directory, ignore_list):
    number_of_companies = len(os.listdir(directory))
    company_counter = 0
    for company in os.scandir(directory):
        company_counter += 1
        print(f'checking company {company_counter}/{number_of_companies}: {company.name}         ', end='\r')
        result = check_bloomberg_company(company, ignore_list)


if __name__ == '__main__':
    directory = 'BloombergData'
    ignore_list = get_ignore_list()
    # all_files_of_right_company()
    # no_random_files()
    # four_files_in_folder()
    check_bloomberg_data(directory, ignore_list)
