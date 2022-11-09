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
def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    gdp = {}
    with open(gdpinfo["gdpfile"], newline='') as csvfile1:
        csvreader1 = csv.DictReader(csvfile1, delimiter=gdpinfo["separator"]\
                                   , quotechar=gdpinfo["quote"])
        for row in csvreader1:
            country_code = row[gdpinfo["country_code"]]
            gdp[country_code.casefold()] = row 
            
    code = {}
    with open(codeinfo["codefile"], newline='') as csvfile2:
        csvreader2 = csv.DictReader(csvfile2, delimiter=codeinfo["separator"]\
                                   , quotechar=codeinfo["quote"])
        for row in csvreader2:
            plot_code = row[codeinfo["plot_codes"]]
            code[plot_code] = row 
            
    map_tup=tuple()
    map_dict=dict()
    map_set1=set()
    map_set2=set()

                
    for key, value in plot_countries.items():
        if key.upper() in code:
            new_dict={}
            new_dict[key]=value
            recon_tuple=reconcile_countries_by_code(codeinfo, new_dict ,gdp)   
            if key in recon_tuple[0]:
                gdp_code=recon_tuple[0][key]
                if gdp[gdp_code.casefold()][year]!='':
                    gdp_year=int(float(gdp[gdp_code.casefold()][year]))
                    map_dict[key]=math.log(gdp_year,10)
                else:
                    map_set2.add(key)
            else: 
                map_set1.add(key)
        else:
            map_set1.add(key)
            
    map_tup+=(map_dict,)
    map_tup+=(map_set1,)
    map_tup+=(map_set2,)
    return map_tup


def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = 'GDP by country'+year
    worldmap_chart.add('GDP for'+year,build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)[0])
    worldmap_chart.add('Missing',build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)[1])
    worldmap_chart.add('No data',build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)[2])
    worldmap_chart.render_to_file(map_file)



def test_render_world_map():
    """
    Test the project code for several years
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", \
                    "isp_gdp_world_code_1960.svg")
    #2010
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", \
                    "isp_gdp_world_code_2010.svg")


test_render_world_map()

