import pandas as pd


def clean_dataframe_columns(dataframe):
    dataframe = dataframe.copy()
    dataframe.columns = dataframe.columns.astype(str)

    dataframe = dataframe.loc[:, dataframe.columns != "nan"]
    dataframe = dataframe.loc[:, dataframe.columns != "None"]
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains("^Unnamed")]
    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()]
    dataframe = dataframe.dropna(axis=1, how="all")

    # Convert list/dict columns to string for MongoDB compatibility
    for column in dataframe.columns:
        dataframe[column] = dataframe[column].apply(
            lambda x: str(x) if isinstance(x, (list, dict)) else x
        )

    dataframe = dataframe.drop_duplicates()

    return dataframe
