import datetime
import sqlite3
import lxml.html as lh
import pandas as pd
import requests


def parse_expereact(url):
    """
    Download a list of all GBOD... chemicals from expereact,
    parse the html table inside there and return a variable holding the parsed data
    """
    debug = False  # set to True to avoid reloading expereact data (takes some 20 seconds)
    # fetch expereact export (omitted if debug is True)
    if debug is False:
        file = requests.get(url)  # source url from outer scope
        with open('expereact_source.dat', 'wb') as newfile:
            newfile.write(file.content)  # download to local file
            # (intermediate download is necessary for reliable parsing)
    with open('expereact_source.dat', 'rb') as file:  # load local file
        # Parse html into variable doc
        doc = lh.parse(file)
    # extract table contents and return
    return doc.xpath('//tr')


def convert_table_to_df(table):
    """
    Convert the parsed html table into a pandas dataframe.
    Some assumptions specific to the data are made. (e.g. number of columns == 14)
    TODO get rid of this ^ hardcoded limitation
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


def filter_groups(df):
    """
    Take the DataFrame parsed from Expereact that holds data for all groups' chemicals
    and filter for the groups that want to use the system
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    # the regex matches group base names + two caps
    # regex for different groups are chained with | (<-- bitwise OR)
    regex = 'GBOD[A-Z]{2,2}|' \
            'GYAM[A-Z]{2,2}|' \
            'GZEN[A-Z]{2,2}'
    return df.loc[df['code'].str.fullmatch(regex)]


def single_sql_query_to_df(cursor_fetchall, name: str):
    """
    Helper function for commit_df_to_db_detail.
    Iterates over the results from the sql query and turns them into a Dataframe
    :param cursor_fetchall: iterable function
    :return: pandas.DataFrame
    """
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
        for delete_item in list_delete:
            cur.execute('DELETE FROM inventorymanagement_bottle WHERE id=?', (delete_item,))
        conn.commit()
        df_new.to_sql('inventorymanagement_bottle', conn, if_exists='append', index=False, dtype='varchar(200)')
        # print some output to confirm success
        print(f'These bottles were deleted from the db: {list_delete}')
        print(f'These bottles were added to the db: {df_new["id"].to_list()}')
    return


def update_locations(df_expereact, db_path):
    """
    update locations in sqlite database from a dataframe parsed from expereact.
    The method simply overwrites every location with the current one by iterating over
    df_expereact and updating the one db entry with the same id every iteration.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        # fetch data with old locations from sql
        df_sql = pd.read_sql("SELECT id, location from inventorymanagement_bottle", conn)
        # update information
        for code in df_sql['id'].array:  # iterate over all the bottle codes in db
            # lookup the new (current) location. Return the value
            new_location = df_expereact.loc[df_expereact['id'] == code].reset_index().at[0, 'location']
            # or update database directly (OPTION 2)
            cur.execute('UPDATE inventorymanagement_bottle SET location = ? WHERE id=?', (new_location, code,))
    return


# variables
source_url = "http://expereact.ethz.ch/searchstock?for=chemexper&bl=1000000&so=Field10.15&search=+AND+Field10.15%3D%2225%22&for=report&mime_type=application/vnd.ms-excel"
# source_url_BODE = "http://expereact.ethz.ch/searchstock?for=chemexper&bl=100&so=Field10.15&search=+AND+Field10.6%2B%40%3D%22GBOD%22+AND+Field10.15%3D%2225%22&bl=10000&from=1&for=report&mime_type=application/vnd.ms-excel"
db_path = '../db.sqlite3'
# MAIN
if __name__ == '__main__':
    print('####################################################\n'
          'Running database update from updateFromExpereact.py\n'
          '####################################################')
    print(f'Date: {datetime.date.today().strftime("%d.%m.%Y")}')
    print(f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
    table = parse_expereact(source_url)
    df_parsed = convert_table_to_df(table)
    df_clean = cleanup(df_parsed)
    df_filtered = filter_groups(df_clean)
    commit_df_to_db_detail(df_filtered, db_path)
    update_locations(df_filtered, db_path)
    print(f'updateFromExpereact.py finished at {datetime.datetime.now().strftime("%H:%M:%S")}\n'
          f'##################################################\n\n')
