# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 17:32:26 2022

@author: IDOUNT
"""

import numpy as np
import pandas as pd
import pycountry
from functools import lru_cache
from typing import Iterable

@lru_cache()
def get_normal_name(country:str):
    """
    

    Parameters
    ----------
    country : str
        DESCRIPTION.

    Returns
    -------
    name : TYPE
        DESCRIPTION.

    """
    try:
        name = pycountry.countries.search_fuzzy(country)[0].name
        return name
    except Exception as e:
        #TODO: find bad matches and go to self made list :(
        return None
    
def get_all_countries(un_normlized_names_column:Iterable,keep_unmatched=True):
    """
    takes countries by order and retruns their normlized names in the same order.
    for exmple:
    [greek,egept,england] -> [None None 'United Kingdom']
    """
    
    if type(un_normlized_names_column)!= pd.Series:
        un_normlized_names_column = pd.Series(un_normlized_names_column)
        
    uniques = un_normlized_names_column.unique()
    normlized_names = [get_normal_name(country) for country in uniques]
    joiner = pd.DataFrame({'unnormalized':uniques,
                           'normalized':normlized_names})
    
    original = pd.DataFrame({'unnormalized':un_normlized_names_column})
    merged = pd.merge(left=original,right=joiner,how='left',on='unnormalized')
    if keep_unmatched:
        merged['normalized'] = merged['normalized'].fillna(merged['unnormalized'])
    return merged['normalized'].values

def get_distinct_249_countries():
    names = pd.Series([i.name for i in pycountry.countries])
    return names

if __name__ == '__main__':
    raw_dat =  ['greek','egept','england']
    res = get_all_countries(raw_dat)
    print(res)