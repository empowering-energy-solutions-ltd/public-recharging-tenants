recharing-tenants
==============================

Documentation available at: https://redesigned-tribble-qk6zj22.pages.github.io/

Recharging tenants can be used by site energy managers to recharge tenants of their sites using their site energy bills and the sub meters of the tenants. To use this tool, create utility invoice spreadsheets like those found in `src/data/example_data`, you'll also need to generate a `tenant_readings.csv` an example of one of these can be found in the demonstration notebook with column descriptions. 

When first using the project use `poetry lock` to create the virtual environment. You can then use `poetry show -vv` to find the env path to use as a kernel.

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data           <- Folder containing demo data
    │   │
    │   ├── example_data <- Example input data to run recharging tenants
    │   │   │
    │   │   ├── example_electric_invoice_2.csv <- Electricity invoice table example.
    │   │   │
    │   │   ├── example_gas_invoice.csv <- Gas invoice table example.
    │   │   │
    │   │   ├── example_tenant_readings.csv <- Recharging input data example.
    │   │   │
    │   │   └── example_water_invoice.csv <- Water invoice table example.
    │   │
    │   └── example_results
    │       │
    │       ├── commercial_charges.csv <- Example output of the commercial charges.
    │       │
    │       ├── historical_charges.csv <- Example of historical charges saved from previous recharging tenant months.
    │       │
    │       ├── historical_readings.csv <- Example of historical readings saved from previous recharging tenant months.
    │       │
    │       ├── new_form.csv  <- Example new template form for the next recharging period.
    │       │
    │       └── resident_charges.csv <- Example output of the residential charges.
    │
    ├── notebooks         
    │   │                
    │   └── Demo_notebook.ipynb   <- Demonstration notebook of how to use the recharging tenant class.
    │
    ├── requirements.txt   <- The requirements file for this project.
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download, generate & manipulate data
    │   │   │
    │   │   ├── import_data.py <- Functions for loading the different data sources into the correct format.
    │   │   │   
    │   │   └── schema.py <- Schemas used in recharging tenants 
    │   │
    │   └── models
    │       │ 
    │       └── report.py  <- Where all the functions for the Site object are held and where recharging tenants is done.
    │
    └── requirements.txt   <- requirements file for needed imports


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
