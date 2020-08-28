import requests
import lxml.html as lh
import pandas as pd
import sqlite3


def parse_expereact(url):
    """
    Download a list of all GBOD... chemicals from expereact,
    parse the html table inside there and return a variable holding the parsed data
    """
    file = requests.get(url)  # source url from outer scope
    with open('expereact_source.dat', 'wb') as newfile:
        newfile.write(file.content)  # download to local file
        # (somehow the parsing breaks, if file.content is passed directly
    with open('expereact_source.dat', 'rb') as file:  # load local file
        # Parse html into variable doc
        doc = lh.parse(file)
    # extract table contents and return
    return doc.xpath('//tr')


def convert_table_to_df(table):
    """
    Convert the parsed html table into a pandas dataframe.
    Some assumptions specific to the data are made. (e.g. number of columns == 14)
    :return: pandas.DataFrame
    """
    # Create empty list
    col = []
    i = 0  # For each row, store each first element (header) and an empty list
    for t in table[0]:
        i += 1
        name = t.text_content()
        col.append((name, []))

    # Since out first row is the header, data is stored on the second row onwards
    for j in range(1, len(table)):
        # T is our j'th row
        T = table[j]

        # If row is not of size 14, the //tr data is not from our table
        if len(T) != 14:
            break

        # i is the index of our column
        i = 0

        # Iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()
            # Append the data to the empty list of the i'th column
            col[i][1].append(data)
            # Increment i for the next column
            i += 1

    Dict = {title: column for (title, column) in col}
    df = pd.DataFrame(Dict)
    return df


def cleanup(df):
    """
    Drop unneeded columns of DataFrame and rename the remaining ones to machine-readable strings
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    df.drop(labels=['Status',
                    'Comment',
                    'Order Date',
                    'Reception Date',
                    'Catalogue Nr',
                    'Order Nr'
                    ],
            axis=1, inplace=True
            )
    df.rename(columns={'Supplier':            'supplier',
                       'Product Description': 'description',
                       'Group Code':          'code',
                       'User Name':           'owner',
                       'Location':            'location',
                       'Bottle Nr':           'id',
                       'Quantity':            'quantity',
                       'Price (CHF)':         'price'
                       },
              inplace=True
              )
    return df


def single_sql_query_to_df(cursor_fetchall, name: str):
    id_list = []
    for (row,) in cursor_fetchall:
        id_list.append(row)
    df = pd.DataFrame({name: id_list})
    return df


def commit_df_to_db_detail(df_expereact, db_path):
    """
    Commit a pandas.DataFrame to SQLite3 database. Only add items with 'id' that is not present in the database.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        # fetch all 'id's in the db
        value = ('empty',)
        cur.execute('SELECT id FROM inventorymanagement_bottle WHERE status=?', value)
        # this df will hold all ids of empty bottles
        df_empty = single_sql_query_to_df(cur.fetchall(), 'id')
        cur.execute('SELECT id FROM inventorymanagement_bottle WHERE NOT status=?', value)
        # this df will hold all ids of non-empty bottles
        df_non_empty = single_sql_query_to_df(cur.fetchall(), 'id')
        # reduce df to all the id's that are not yet present in the db (the ~ is the NOT operator)
        df_new = df_expereact.loc[~df_expereact['id'].isin(df_non_empty['id'].to_list())]
        df_new.insert(loc=len(df_new.columns), column='status', value='in')
        # find the ones that where deleted from expereact and delete them from db
        df_all = df_empty['id'].to_list() + df_non_empty['id'].to_list()
        list_delete = list(set(df_all) - set(df_expereact['id'].to_list()))
        print(list_delete)
        for delete_item in list_delete:
            cur.execute('DELETE FROM inventorymanagement_bottle WHERE id=?', (delete_item,))
        conn.commit()
        df_new.to_sql('inventorymanagement_bottle', conn, if_exists='append', index=False, dtype='varchar(200)')
    return


# variables
source_url = "http://expereact.ethz.ch/searchstock?for=chemexper&bl=100&so=Field10.15&search=+AND+Field10.6%2B%40%3D" \
             "%22GBOD%22+AND+Field10.15%3D%2225%22&bl=10000&from=1&for=report&mime_type=application/vnd.ms-excel"
db_path = '../db.sqlite3'
# MAIN
if __name__ == '__main__':
    table = parse_expereact(source_url)
    df = convert_table_to_df(table)
    df_clean = cleanup(df)
    # df_db = get_db_content(db_path)
    commit_df_to_db_detail(df_clean, db_path)
