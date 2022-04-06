import pandas as pd
import requests
import json
import pickle as pkl
from tqdm.auto import tqdm
tqdm.pandas()

df = pd.read_csv('../data/data_with_altmetric.csv')

# Filter out na's
df = df[~df['doi'].isna()]
df = df[~df['abstract'].isna()]

# Given doi returns dict with data obtained from OpenAlex


def get_openalex_attributes(doi: str):
    url = f'https://api.openalex.org/works/doi:{doi}'
    # If something went wrong e.g. timeout during request
    try:
        resp = requests.get(url, timeout=10)
        content = json.loads(resp.content)
    except:
        print('Error occured')
        return None

    result_dict = {}
    result_dict['type'] = content['type']
    result_dict['host_display_name'] = content['host_venue']['display_name']
    result_dict['publisher'] = content['host_venue']['publisher']
    result_dict['is_open_access'] = content['open_access']['is_oa']
    result_dict['open_alex_citations_count'] = content['cited_by_count']
    inst_nested_list = [el['institutions'] for el in content['authorships']]
    inst_nested_names = list(map(lambda inst_list: [
                             entry['display_name'] for entry in inst_list], inst_nested_list))
    result_dict['institutions'] = [
        el for subl in inst_nested_names for el in subl]

    return result_dict


respones = df['doi'].progress_apply(get_openalex_attributes)

# Backup
with open('../data/openalex_respones.pkl', 'wb') as f:
    pkl.dump(respones, f)

# Drop entries with null response
df = df.loc[~respones.isna()].reset_index(drop=True)
respones = respones.loc[~respones.isna()]
# Convert dicts to pd.DataFrame rows
rows = respones.apply(pd.DataFrame)
# Merge into single DataFrame
responses_df = pd.concat(rows.to_list(), axis='index').reset_index(drop=True)
# Merge with df
df_with_openalex = pd.concat([df, responses_df], axis='columns')
df_with_openalex.to_csv('data/df_all.csv', index=False)
