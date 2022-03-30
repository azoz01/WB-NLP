import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def main():
    with open('../20200705v1/full/metadata/metadata_0.jsonl') as f:
        data = list(f)

    records = list(map(json.loads, data))
    df = pd.DataFrame.from_records(records)
    del [records]

    df = df.loc[
        ~df['doi'].isna() | ~df['pubmed_id'].isna() | ~df['arxiv_id'].isna()
    ]

    df['mag_field_of_study'] = df['mag_field_of_study'].apply(
        lambda x: ['None'] if not x else x)

    mlb = MultiLabelBinarizer(sparse_output=True)

    col = df['mag_field_of_study']
    one_hot_fields = pd.DataFrame.sparse.from_spmatrix(
        mlb.fit_transform(col),
        index=col.index,
        columns=mlb.classes_
    )
    df = pd.concat([df, one_hot_fields], axis='columns')

    df = df.groupby(one_hot_fields.columns.tolist()). \
        apply(lambda group: group.sample(frac=.13, random_state=42)). \
        reset_index(drop=True)
    df = df.drop(columns=one_hot_fields.columns.tolist())

    df.to_csv('../data/sampled.csv', index=False)


if __name__ == '__main__':
    main()
