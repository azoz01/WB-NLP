import json
import pickle as pkl
import pandas as pd
import numpy as np


def get_flattened_history(response):
    response = json.loads(response.content)
    history_items = response['history'].items()
    history_columns = [f'history_{entry[0]}' for entry in history_items]
    history_values = [[entry[1]] for entry in history_items]
    return dict(zip(history_columns, history_values))


relevant_response_fields = [
    'cited_by_posts_count',
    'cited_by_tweeters_count',
    'cited_by_policies_count',
    'readers_count',
    'score',
]


def extract_relevant_fields(response):
    response = json.loads(response.content)

    return dict(zip(relevant_response_fields,
                    [[response.get(key, 0)] for key in relevant_response_fields]))


def main():

    df = pd.read_csv('../data/sampled.csv')
    with open('..data/response.pkl', 'wb') as f:
        responses = pkl.load(f)

    response_found = list(
        map(lambda response: response.status_code == 200, responses))
    response_col = pd.DataFrame(
        {'response': np.array(responses)[response_found]})

    df_with_altmetric = pd.concat([df.loc[response_found].reset_index(drop=True), response_col],
                                  axis='columns')

    relevant_fields = df_with_altmetric['response'].apply(
        extract_relevant_fields).to_list()
    relevant_fields_rows = list(map(pd.DataFrame, relevant_fields))
    relevant_fields_df = pd.concat(relevant_fields_rows, axis='rows')
    relevant_fields_df.index = np.arange(len(relevant_fields_df))

    history_fields = df_with_altmetric['response'].apply(
        get_flattened_history).to_list()
    history_fields_rows = list(map(pd.DataFrame, history_fields))
    history_fields_df = pd.concat(history_fields_rows, axis='rows')
    history_fields_df.index = np.arange(len(history_fields_df))

    df_with_altmetric = pd.concat(
        [df_with_altmetric, relevant_fields_df, history_fields_df], axis='columns')

    df_with_altmetric.to_csv('../data/data_with_altmetric.csv')


if __name__ == '__main__':
    main()
