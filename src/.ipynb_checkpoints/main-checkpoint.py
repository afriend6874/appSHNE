import os
import re
import numpy as np
import pandas as pd
import pickle
import json
import random
import threading
import getopt
import sys
import time
from scipy import sparse
from stellargraph import StellarGraph

from src.data_creation import get_data 
from src.data_creation import json_functions 
from src.data_creation import dict_builder 
from src.data_creation import build_network 
from src.graph_learning import node2vec
from src.graph_learning import metapath2vec
from src.graph_learning import word2vec
from SHNE_code import SHNE

def get_app_names(**kwargs):
    '''
    Function to extract file paths of apps
    
    Parameters
    ----------
    
    limiter
        boolean value to limit number of app paths extracted. If True benign and malicious apps will be limited by the number given by their respective limit parameter, benign_lim and malignant_lim

    **kwargs

        malignant_fp
            The file path of the malicious apps

        benign_fp
            The file path of the benign apps

        lim_benign
            The number of benign apps that the outputed paths will be limited to

        lim_mal
            The number of malicious apps that the outputed paths will be limited to
        
    Returns
    -------
    2 lists
        the first return value being a list of malignant app names found in malignant_fp
        the second return value being a list of benign app names found in benign_fp
    '''
    limiter=kwargs["limiter"]
    malignant_fp=kwargs["mal_fp"]
    benign_fp=kwargs["benign_fp"]
    benign_lim=kwargs["lim_benign"]
    malignant_lim=kwargs["lim_mal"]
    
    print("\n--- Starting Malware Detection Pipeline ---")
    start = time.time()
    if limiter:
        print("Limiting app intake to " + str(malignant_lim + benign_lim) + " apps")
        print()
        mal_app_names = [[name+"/"+sub_name for sub_name in os.listdir(malignant_fp+"/"+name)] for name in os.listdir(malignant_fp) if os.path.isdir(malignant_fp + "/" + name)]
        benign_app_names = [name for name in os.listdir(benign_fp) if (os.path.exists(benign_fp + "/" + name+"/"+"smali"))] #and (len(os.listdir(benign_fp + "/" + name+"/"+"smali")) != 0)]
        flat_list = []
        for sublist in mal_app_names:
            for item in sublist:
                flat_list.append(item)
        mal_app_names = flat_list

        flat_list = []
        mal_app_names = [[name+"/"+sub_name for sub_name in os.listdir(malignant_fp+"/"+name) if os.path.exists(malignant_fp+"/"+name+"/"+sub_name+"/smali")] for name in mal_app_names]
        for sublist in mal_app_names:
            for item in sublist:
                flat_list.append(item)
        mal_app_names = flat_list
        
        
        #get family of malware in its respective app name
        #mal_app_names_full = [family +"_"+ name for family in mal_app_names for name in os.listdir(malignant_fp+"/"+family) if os.path.isdir(malignant_fp +"/"+ family + "/" + name)]
        
        #randomize the list
        random.shuffle(mal_app_names) 
        random.shuffle(benign_app_names)
        
        #limit the apps
        try:
            mal_app_names = mal_app_names[:malignant_lim]
            print(len(mal_app_names))
        except:
            mal_app_names = mal_app_names
            
        try:
            benign_app_names = benign_app_names[:benign_lim]
            print(len(benign_app_names))
        except:
            benign_app_names = benign_app_names
            
        assert len(set(mal_app_names)) == len(mal_app_names), "DUPLICATE APP NAMES"
        assert len(set(benign_app_names)) == len(benign_app_names), "DUPLICATE APP NAMES"

    else:
        print()
        mal_app_names = [name for name in os.listdir(malignant_fp) if os.path.isdir(malignant_fp + "/" + name)]
        mal_app_names = [[name+"/"+sub_name for sub_name in os.listdir(malignant_fp+"/"+name)] for name in mal_app_names]
        flat_list = []
        for sublist in mal_app_names:
            for item in sublist:
                flat_list.append(item)
        mal_app_names = flat_list
        flat_list = []
        for sublist in mal_app_names:
            for item in sublist:
                flat_list.append(item)
        mal_app_names = flat_list
        
        benign_app_names = [name for name in os.listdir(benign_fp) if os.path.isdir(benign_fp + "/" + name)]
        #create_dictionary(mal_app_names,benign_app_names,malignant_fp,benign_fp)
    return mal_app_names, benign_app_names
        
def create_dictionary(malignant_apps, benign_apps, **kwargs):
    '''
    Create dictionaries of individual app api calls.
    Dictionaries wil be saved to
    
    Parameters
    ----------
            
    malignant_apps
        Names of benign apps
        
    benign_apps
        Names of benign apps
        
    **kwargs
        malignant_fp
            The file path of the malicious apps

        benign_fp
            The file path of the benign apps

        multithreading
            Boolean value to turn on multithreaded processing of data

        out_path
            File path of outputed parsed apps

        verbose
            Boolean value to print progress while building dictionaries
    
    '''
    limiter=kwargs["limiter"]
    malignant_fp=kwargs["mal_fp"]
    benign_fp=kwargs["benign_fp"]
    multi_threading=kwargs["multithreading"]
    out_path=kwargs["out_path"]
    verbose=kwargs["verbose"]
    
    if '.ipynb_checkpoints' in benign_apps:
        benign_apps.remove('.ipynb_checkpoints')
    if '.ipynb_checkpoints' in malignant_apps:
        malignant_apps.remove('.ipynb_checkpoints')

    start_time = time.time()
    print("--- Begin Parsing Benign and Malicious Apps ---")
    confirm_exc = get_data.create_app_files(benign_fp, benign_apps,malignant_fp, malignant_apps, multi_threading, verbose, out_path)
    if confirm_exc:
        print("--- All Apps Parsed in " + str(int(time.time() - start_time)) + " Seconds ---")
        print()
        print()
    else:
        raise ValueError("ERROR get_data.create_app_files failed")

def build_dictionaries(**params):
    '''
    Function to build dictionaries of api calls:
    dict_A.json contains api calls indexed by the app they appear in
    dict_B.json contains api calls indexed by the method block they appear in
    dict_P.json contains api calls indexed by the package they appear in
    dict_I.json contains api calls indexed by the invocation type they appear in
    api_calls.json contains api calls with the number of times they appear in all apps 
    naming_key.json is a table to look up keys and their relative api calls, apps, code blocks, packages, or invocation types
    
    Parameters
    ----------
    **params
        dict_directory
            File path of dictionary output

        out_path
            File path to get json files of api calls from parsed apps

        verbose
            Boolean value to print progress while building dictionaries

        truncate
            Boolean value to 

        lower_bound_api_count
    
    '''
    parsed_fp=params["dict_directory"]
    verbose=params["verbose"]
    directory=params["out_path"]
    truncate=params["truncate"]
    lower_bound_api_count=params["lower_bound_api_count"]
    
    
    print("--- Starting Dictionary Creation ---")
    start_time = time.time()
    dict_B, dict_P, dict_I, dict_A = dict_builder.fast_dict(directory, verbose, truncate, lower_bound_api_count, parsed_fp)
    for t,fname in zip([dict_A, dict_B, dict_P, dict_I],["dict_A", "dict_B", "dict_P", "dict_I"]):
        json_functions.save_json(t,parsed_fp+fname)       
    print("--- Dictionary Creation Done in " + str(int(time.time() - start_time)) + " Seconds ---")
    print()
    print()

def make_graph(src):
    print("--- Starting StellarGraph Creation ---")
    start_time = time.time()
    G=build_network.make_stellargraph(src)
    print(G.info())
    print("--- StellarGraph Creation Done in " + str(int(time.time() - start_time)) + " Seconds ---")
    print()
    # list of all node types in the graph
    node_types = ["api_call_nodes", "package_nodes", "app_nodes", "block_nodes"]
#     not working:
#     node_type_set = G.node_types()
#     print(node_type_set)
    # create dictionary with counts of each node type and save to json
    node_dict = {type:len(G.nodes_of_type(type)) for type in node_types}
    json_functions.save_json(node_dict, "out/data/node_counts")
    return G

def run_shne():
    #Start SHNE 
    print("--- Starting SHNE ---")
    s_app = time.time()
    SHNE.run_SHNE()
    print("--- SHNE Embedding Layer Created in " + str(int(time.time() - s_app)) + " Seconds ---")

# def run_all(test,**params):
#     '''
#     Runs the main project pipeline logic, given the targets.
    
#     Parameters
#     ----------
#     targets
#         an optional value form commant line. If the tags `-t`, `--test`, or `--Test` the test set specified by `mal_fp_test_loc` and `benign_fp_test_loc` in `**data_params` will be used.
        
#     **kwargs
#         Key worded arguments from configuration files
        
#         mal_fp
#             file path of the malignant apps
            
#         benign_fp
#             file path of the benign apps
            
#         limiter
#             Boolean value to dictate if number of apps parsed is to be limited
            
#         lim_mal
#             Number of malignant apps to limit parsing of if limiter is True
            
#         lim_benign
#             Number of benign apps to limit parsing of if limiter is True
            
#         mal_fp_test_loc
#             file path of test malignant apps
            
#         benign_fp_test_loc
#             file path of benign apps
                    
#         directory
#             File path to get json files of api calls from parsed apps
            
#         verbose
#             Boolean value to print progress while building dictionaries
            
#         truncate
#             Boolean value to 
            
#         lower_bound_api_count
        
#         dict_directory
#             File path of dictionary output
            
#         multithreading
#             Boolean value to turn on multithreaded processing of data
            
#         out_path
#             File path of outputed parsed apps
            
#         verbose
#             Boolean value to print progress while building dictionaries
            
#         options
#             Single character options for command line
            
#         long_options
#             String options for command line
#     '''
#     print()
#     print()
#     print(params)
#     etl_params=params["etl-params"]
#     wv_params=params["word2vec-params"]
    
#     if test:
#         etl_params["mal_fp"]=etl_params["mal_fp_test"]
#         etl_params["benign_fp"]=etl_params["benign_fp_test"]        
#         etl_params["out_path"]=etl_params["out_path_test"]
#         etl_params["out_path"]=etl_params["out_path_test"]
#         etl_params["dict_directory"] = etl_params["dict_directory-test"]
        
#         etl_params["data_extract_loc"]=etl_params["data_extract_loc_test"]
#         etl_params["data_naming_key"]=etl_params["data_naming_key_test"]
        
#     check_files=["api_calls.json","dict_A.json","dict_B.json","dict_I.json","dict_P.json","naming_key.json"]
#     check_files2=["content.pkl","het_random_walk_full.txt","node_counts.json","word_embedding.txt"]
    
    
#     if os.path.isdir("out/data/") and all([cf in os.listdir("out/data/") for cf in check_files2]):
#         print("PREPROCESSING DONE, STARTING SHNE")
#         run_shne()
        
#     else:
#         if os.path.isdir(etl_params["dict_directory"]) and all([cf in os.listdir(etl_params["dict_directory"]) for cf in check_files]):
#             print("--- DICTIONARIES ALREADY CREATED, STARTING STELLARGRAPH CREATION ---")

#             # get StellarGraph Network Graph
#             G=make_graph(etl_params["dict_directory"])

#             # generate node2vec random walks
#             #node2vec.node2vec_walk(G, params["node2vec-params"])

#             # generate metapath2vec random walks
#             metapath2vec.metapath2vec_walk(G, params["metapath2vec-params"])

#             #BRADEN
#             word2vec.create_w2v_embedding(etl_params["data_extract_loc"],wv_params["size"],wv_params["window"],wv_params["workers"],etl_params["data_naming_key"]) #Config 
#             run_shne()

#         else:
#             #start extracting smali code
#     #         mainpy.extract(limiter, mal_fp, benign_fp, lim_benign, lim_mal, multithreading, verbose, out_path)
#             mal_app_names, benign_app_names=get_app_names(**etl_params)

#             create_dictionary(mal_app_names, benign_app_names, **etl_params)


#             #create dictionaries
#             build_dictionaries(**etl_params)

#             # get StellarGraph Network Graph
#             G=make_graph(etl_params["dict_directory"])


#             # generate node2vec random walks
#             #node2vec.node2vec_walk(G, params["node2vec-params"])

#             # generate metapath2vec random walks
#             metapath2vec.metapath2vec_walk(G, params["metapath2vec-params"])

#             #BRADEN
#             word2vec.create_w2v_embedding(etl_params["data_extract_loc"],wv_params["size"],wv_params["window"],wv_params["workers"],etl_params["data_naming_key"]) #Config
#             run_shne()
        