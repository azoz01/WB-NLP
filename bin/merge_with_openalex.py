import pandas as pd
import requests
import json
import pickle as pkl
from tqdm.auto import tqdm
tqdm.pandas()

# Given doi returns dict with data obtained from OpenAlex API


def get_openalex_attributes(doi: str):
    url = f'https://api.openalex.org/works/doi:{doi}'

    try:
        resp = requests.get(url, timeout=10)
        content = json.loads(resp.content)
        result_dict = {}
        result_dict['type'] = content['type']
        result_dict['host_display_name'] = content['host_venue']['display_name']
        result_dict['publisher'] = content['host_venue']['publisher']
        result_dict['is_open_access'] = content['open_access']['is_oa']
        result_dict['open_alex_citations_count'] = content['cited_by_count']
        inst_nested_list = [el['institutions']
                            for el in content['authorships']]
        inst_nested_names = list(map(lambda inst_list: [
            entry['display_name'] for entry in inst_list], inst_nested_list))
        result_dict['institutions'] = [
            el for subl in inst_nested_names for el in subl]
    except:
        print('Error occured')
        return None

    return result_dict


def main():
    print('Reading data')
    df = pd.read_csv('data/data_with_altmetric.csv')

    print('Getting OpenAlex data')
    responses = df['doi'].progress_apply(get_openalex_attributes)

    print('Saving OpenAlex data to pkl')
    with open('data/openalex_respones.pkl', 'wb') as f:
        pkl.dump(responses, f)

    print('Filtering null OpenAlex data')
    df = df.loc[~responses.isna()].reset_index(drop=True)
    responses = responses.loc[~responses.isna()]

    print('Converting OpenAlex data to DataFrame')
    inst_col = responses.apply(lambda resp: resp.pop('institutions'))

    openalex_rows = responses.apply(pd.DataFrame, index=[0]).tolist()
    openalex_df = pd.concat(openalex_rows)
    openalex_df = openalex_df.assign(
        institutions=inst_col
    )
    openalex_df = openalex_df.reset_index(drop=True)
    df = pd.concat([df, openalex_df], axis='columns')

    df.to_csv('data/df_all.csv', index=False)


if __name__ == '__main__':
    main()
