# warren
A framework for preselecting potentially undervalued companies.

## Required pre installation:
Before cloning the library!!!:
- recommended operating system: Linux
- install anaconda with [this guide](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart-de) or install pip
- install gspread and oauth2client with `pip3 install gspread oauth2client`
- install git lfs with [this guide](https://github.com/git-lfs/git-lfs/wiki/Installation)

Only after installing those, especially git lfs, then clone the repository.

## Getting started:
```
cd DESIRED_PATH
git clone https://github.com/ZhuWestphal/warren.git
cd warren
jupyter lab --port 9000
```
Then open a browser and visit [localhost:9000](localhost:9000)

## Getting started locally with anaconda
Install conda environment following [those commands](https://docs.conda.io/projects/conda/en/latest/_downloads/843d9e0198f2a193a3484886fa28163c/conda-cheatsheet.pdf):
```
conda env create --file .conda_requirements.yml
```
Activate conda environment
```
conda activate zw
```

## Getting started locally with pip
Setting up virtual environment with the name venv_zw
```
python3 -m venv venv_zw
```
Opening virtual environment
```
source venv_zw/bin/activate
```
Install prerequisites modules
```
pip install -r .pip_requirements.txt 
```

## Commit, style guide etc
Create pull requests, which someone else will review and merge. Do not merge your own pull requests!
Check the style guide before committing.

module_name, package_name, ClassName, method_name, ExceptionName, function_name, GLOBAL_CONSTANT_NAME, global_var_name, instance_var_name, function_parameter_name, local_var_name.



## Links to libraries
- [gspread library](https://gspread.readthedocs.io/en/latest/index.html)
- [anaconda documentation](https://docs.anaconda.com/)
