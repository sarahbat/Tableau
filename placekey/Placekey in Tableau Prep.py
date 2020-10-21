#####
# Using SafeGraph Placekey with Tableau Prep
# by Paul Rossman
#####

import pandas as pd
import numpy as np
import json
import http.client

def prepare_batches_for_API(all_batches):
    batch_payloads = []
    for batch in all_batches:
        payload = json.dumps({"queries":batch, 
                              "options": {"strict_name_match": True}}) #see https://protect-us.mimecast.com/s/4xpECXDk7LI9vzwDH6cN2y?domain=docs.placekey.io
        batch_payloads.append(payload)
    return batch_payloads

def getPlacekeys(batch_payloads, debug=False):
    api_key = "XXXXXXX" # fill this in with your personal API key (do not share publicly)
  
    headers = {
    'accept': "application/json",
    'apikey': api_key,
    'content-type': "application/json"
    }    
    conn = http.client.HTTPSConnection("https://protect-us.mimecast.com/s/3p2qCYElQWT9R4rpHGTzXn?domain=api.placekey.io") 
    responses = []
    for payload in batch_payloads:
        conn.request("POST", "/v1/placekeys", payload, headers)
        res = conn.getresponse()
        data = res.read()
        if(debug):   
          print("data", data)
          print("status", res.status)
          print("headers", res.getheaders())
        responses.append(json.loads(data))
    return responses    

def placekey_lookup(inputs):

    query_id_col = "LOCNUM" # this column in your data should be unique for every row
    column_map = {query_id_col: "query_id",
               "business_name" : "location_name",
               "ADDRESS" : "street_address",
               "CITY": "city",
               "STATE": "region",
               "ZIP_CODE": "postal_code"
    }
    df_for_api = inputs.rename(columns=column_map)
    cols = list(column_map.values())
    df_for_api = df_for_api[cols]
    df_for_api['iso_country_code'] = 'US'
     
    df_clean = df_for_api.copy()
    possible_bad_values = ["", " ", "null", "Null", "None", "nan", "Nan"] # Any other dirty data you need to clean up? 
    for bad_value in possible_bad_values:
        df_clean = df_clean.replace(to_replace=bad_value, value=np.nan)

    data_jsoned = json.loads(df_clean.to_json(orient="records"))
     
    max_batch_size = 50
    batches = [data_jsoned[i:i + max_batch_size] for i in range(0, len(data_jsoned), max_batch_size)]
    batches_json = prepare_batches_for_API(batches)
     
    responses = getPlacekeys(batches_json)
    responses_flat = [item for sublist in responses for item in sublist]
    responses_flat_cleaned = [resp for resp in responses_flat if 'query_id' in resp]
    
    df_placekeys = pd.read_json(json.dumps(responses_flat_cleaned), dtype={'query_id':str})
    
    result = df_placekeys
    
    return result

def get_output_schema():       
    return pd.DataFrame({
    'query_id' : prep_string(),
    'placekey' : prep_string()
    })
