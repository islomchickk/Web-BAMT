import os.path
from collections import Counter

import pandas as pd
from flask import current_app

from app import db
from .models import Dataset


def automapping(raw_df: pd.DataFrame):
    column_type = dict()
    for c in raw_df.columns.to_list():
        disc = ['str', 'O', 'b', 'categorical', 'object', 'bool']
        disc_numerical = ['int32', 'int64']
        cont = ['float32', 'float64']
        if raw_df[c].dtype.name in disc:
            column_type[c] = 'str'
        elif raw_df[c].dtype.name in cont:
            column_type[c] = 'float'
        elif raw_df[c].dtype.name in disc_numerical:
            column_type[c] = 'str'
        else:
            pass # error ??

    return column_type


def update_db(package, map):
    dataset = Dataset(**package, map=map)

    db.session.add(dataset)
    db.session.commit()


def find_dataset_by_user_and_dataset_name(user: str, name: str) -> Dataset:
    return Dataset.query.filter_by(owner=user, name=name).all()


def remove_dataset_from_database(owner, name):
    meta = get_dataset_location(owner, name)
    if not meta:
        return None
    abs_path = os.path.join(current_app.config["DATASETS_FOLDER"], meta["location"])
    os.remove(abs_path)

    Dataset.query.filter_by(owner=owner, name=name).delete()
    db.session.commit()
    return True


def get_dataset_meta_by_user(user):
    return {dataset.name: dataset.description for dataset in Dataset.query.filter_by(owner=user).all()}


def get_number_of_datasets(user: str, ) -> int:
    return len(Dataset.query.filter_by(owner=user).all())


def get_dataset_location(owner: str, name: str):
    data = Dataset.query.filter_by(owner=owner, name=name).with_entities(Dataset.location).first()
    return data


def get_header_from_csv(file):
    return pd.read_csv(file, index_col=0, nrows=0).columns.tolist()


def check_db_fullness(folders_mapped: dict):
    """
    Function checks if database and files relations are corrupted.
    :return:
    """
    failed = False
    result = {i: {} for i in folders_mapped.keys()}
    for table, upload_folder in folders_mapped.items():
        query = \
            f"""
        SELECT {"location" if table == "datasets" else "sample_loc"} FROM {table}
        {"WHERE id not in (1, 2)" if table == "datasets" else ""};
        """
        db_content = db.session.execute(query).fetchall()
        db_content = [i[0] for i in db_content]
        folder_content = []

        for dirname, dirnames, filenames in os.walk(upload_folder):
            if not dirnames:
                user = os.path.basename(dirname)
                folder_content.extend([os.path.join(user, file) for file in filenames])

        if not (Counter(folder_content) == Counter(db_content)):
            failed = True
            diff_items = set(db_content) - set(folder_content)
            result[table] = diff_items

    if not failed:
        return True, result
    else:
        return False, result
