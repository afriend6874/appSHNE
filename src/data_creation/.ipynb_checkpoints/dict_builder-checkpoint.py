import re
# import json
import os
import numpy as np
import time
import random
import csv

import src.data_creation.json_functions as jf


# with open("config/dict_build.json", "r") as read_file:
#     params = json.load(read_file)
    
# direc = params["directory"]
# verbose = params["verbose"]
# truncate = params["truncate"]
# lower_bound_api_count = params["lower_bound_api_count"]
# key_dst=os.path.join(params["key_directory"], "naming_key.json")
# call_dst=os.path.join(params["key_directory"], "api_calls.json")

    
def fast_dict(**kwargs):
    """Builds dictionaries which can be converted into matrices A,B,P,I, along with corrisponding test matrices

    :return; four dictionaries corresponding to matrices A,B,P,I and a test matrix A_test
    """
    key_directory=kwargs["dict_directory"]
    verbose=kwargs["verbose"]
    direc=kwargs["out_path"]
    truncate=kwargs["truncate"]
    lower_bound_api_count=kwargs["lower_bound_api_count"]
    naming_key_filename=kwargs["data_naming_key_filename"]
    api_call_filename=kwargs["api_call_filename"]
    
    key_dst=os.path.join(key_directory, naming_key_filename)
    call_dst=os.path.join(key_directory, api_call_filename)
    
    def add_key(store, value, prefix, suffix, value_type):
        """
        Takes a value and a dictionary to add the value to. Adds a key, value pair to dictionary if it does not already exist. 
        Will return the key associated with a value. 
        Key is created by concatenating the letter of the associated node, a,v,c,p, and i to the length of the lookup table.
        """
        if value not in store["get_key"][value_type]:
            key=prefix+str(suffix)
            store["lookup_key"][key]=value
            store["get_key"][value_type][value]=key
            suffix+=1
        else:
            key=store["get_key"][value_type][value]
        return key, suffix

    def append_value(store, key, value):
        """
        Appends value to dictionary at index key. Returns dictionary with appended value
        """
        if key in store:
            store[key].append(value)
        else:
            store[key]=[value]
    
    #########################
    #FOR TRAIN PORTION OF SPLIT
    #########################
    B = {}
    A = {}
    P = {}
    I = {}
    C = {}
#     call_list=set() #set to keep track of all the calls
    
    # c- prefix denotes api call
    # a- prefix denotes app
    # b- prefix denotes code block
    # p- prefix denotes package
    # i- prefix denotes invoke type
    key_lookup={
        "get_key":{
            "apps":{}, #input a value and value type, i.e. "apps", etc, and get the associated key
            "blocks":{},
            "packages":{},
            "invokes":{},
            "calls":{}
        }, 
        "lookup_key":{} #input a key and get the associated value
    } 
    
    
    list_of_files = []
    for root, dirs, files in os.walk(direc):
        list_of_files.append(files)

    list_of_files = list(set([item for sublist in list_of_files for item in sublist]))
    random.shuffle(list_of_files)
    print(str(len(list_of_files)) + " Total Files for Dictionary Creation")
    
    ax=0 #index for apps
    bx=0 #index for blocks
    px=0 #index for packages
    ix=0 #index for invoke types
    cx=0 #index for calls
    iix=0 #keep track of iterations
    #print(list _of_files)
    
    start_time=time.time()
    
    for file in list_of_files:
        if "checkpoint" in file: #for stupid git ignores
            continue

        # with open(direc + file, "r") as f:
        #     filez = json.load(f)
        fn=direc+file
        filez=jf.load_json(fn)
                
        filename=file.rstrip(".json")
        akey, ax=add_key(key_lookup, filename,"a", ax, "apps")
        
#         if filename=="test_f_B_extract":
#             print("\ntest_f_B_extract")
        #print("Parsing " + str(len(filez)) + " Blocks from " + filename)   
        
        if ax!=len(list_of_files)-1:
            print("\tParsed %i blocks from %i/%i apps in %i seconds"%(bx,ax,len(list_of_files), time.time()-start_time), end="\r")
        else:
            print("\tParsed %i blocks from %i/%i apps in %i seconds"%(bx,ax,len(list_of_files), time.time()-start_time))
        
        for block in filez:            

            if len(block)>0:#skip empty blocks
                full_block=" ".join(block)
                #add block to lookup table and get a key
                bkey, bx = add_key(key_lookup, full_block, "b",bx, "blocks")
                
                for call in block:
                    try:
                        api_call=call.split("}, ")[1].split(" ")[0].strip()
                        ckey, cx=add_key(key_lookup, api_call, "c",cx, "calls")    
                        append_value(A,akey,ckey) #append key to dictionary
                        append_value(B, bkey, ckey) 
        #                 call_list.add(ckey)

                        package=call.split(";")[0].split(",")[-1].strip()
                        pkey, px=add_key(key_lookup, package, "p",px, "packages")    
                        append_value(P,pkey,ckey) 


                        invoke_type=call.split("}, ")[0].split(" ")[0].strip()
                        ikey, ix=add_key(key_lookup, invoke_type, "i",ix, "invokes")
                        append_value(I,ikey,ckey)
                        #print(ikey,ix, invoke_type)                  
        #                 print(cx,C)
        #                 print()
                        if ckey in C:
                            C[ckey] = C[ckey] + 1
                        else:
                            C[ckey] = 1
                        iix+=1
                    except:
                        continue
                
#         if verbose:
#             if iix % 100000 == 0:
#                 print(str(np.round((iix/len(I.keys()))*100,2)) + "% Parsing Done In " + str(time.time() - dst) + "s")
#                 dst = time.time()
    print()
    
    if truncate:
        print()
        print("Truncation is set to True, API calls only occuring less than lower_bound_api_count will be removed from the model.")
        print("Number of API calls Before Truncation: " + str(len(B.keys())))
        for i in [B, P, I, A]:
            
            #remove files where APIs occur less than lower_bound_api_count across whole data set
            #doesn't work rn
            # remove both keys and values from dict
            
            d = dict((k, v) for k, v in C.items() if v <= lower_bound_api_count)
            for k in d.keys():
                try:
                    del i[k]
                except:continue
        print("Number of API calls After Truncation:  " + str(len(B.keys())))
        print()
        
    #save the key_lookup table to "key_directory" config parameter in dict_build.json
    print("Saving node key lookup table to:\n\t%s"%key_dst)
    print("...",end=" ")
    # os.makedirs(key_directory, exist_ok=True)
    # with open(key_dst, "w") as outfile:
    #     json.dump(key_lookup, outfile)
    jf.save_json(key_lookup, key_dst)
    print("Done\n")
    #save a list of all api calls to "key_directory" config parameter in dict_build.json
    print("Saving api call list to:\n\t%s"%call_dst)
    print("...",end=" ")
    #os.makedirs(call_dst, exist_ok=True)
#     with open(call_dst, "w") as outfile:
# #         write=csv.writer(outfile)
# #         write.writerow(call_list)
#         json.dump(C, outfile)
    jf.save_json(C, call_dst)
    print("Done\n")
    #save the key_lookup table to "key_directory" config parameter in dict_build.json
    return B, P, I, A
                    
                    
                        
                    
                    
            
        