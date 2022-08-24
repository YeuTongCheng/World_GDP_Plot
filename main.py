import csv
import math
import pygal


def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    converter = {}
    with open(codeinfo["codefile"], newline='') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=codeinfo["separator"]\
                                   , quotechar=codeinfo["quote"])
        for row in csvreader:
            plot_code = row[codeinfo["plot_codes"]]
            converter[plot_code] = row[codeinfo["data_codes"]]
    return converter


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    recon_tup=tuple()
    recon_dict=dict()
    recon_set=set()
    convert=build_country_code_converter(codeinfo)
    unify_convert={}
    for key,value in convert.items():
        unify_convert[key.casefold()]=value
        
    gdp_set=set(key.casefold() for key in gdp_countries)
    
    for plot_key in plot_countries:
        lowercase=plot_key.casefold()
        if unify_convert[lowercase].casefold() in gdp_set:
            recon_dict[plot_key]=unify_convert[lowercase]
        else:
            recon_set.add(plot_key)
        
    recon_tup+=(recon_dict,)
    recon_tup+=(recon_set,)
    return recon_tup
