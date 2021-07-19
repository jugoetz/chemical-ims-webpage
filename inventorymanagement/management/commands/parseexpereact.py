from django.core.management.base import BaseCommand
from inventorymanagement.models import Bottle
import datetime

import lxml.html as lh
import pandas as pd
import requests


def parse_expereact(debug):
    """
    Download a list of all chemicals from expereact,
    parse the html table inside there and return a variable holding the parsed data
    :param debug: set to True for development to avoid reloading expereact data (takes some 20 seconds)
    :type debug: bool
    """
    # fetch expereact export
    if debug is False:
        source_url = "https://expereact.ethz.ch/searchstock?for=chemexper&bl=1000000&so=Field10.15&search=+AND" \
                     "+Field10.15%3D%2225%22&for=report&mime_type=application/vnd.ms-excel "
        file = requests.get(source_url)  # source url from outer scope
        with open('inventorymanagement/expereact_source.dat', 'wb') as newfile:
            newfile.write(file.content)  # download to local file
            # (intermediate download to local file is necessary for reliable parsing)
    with open('inventorymanagement/expereact_source.dat', 'rb') as file:  # load local file
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
            'LEHR[A-Z]{2,2}|' \
            'GZEN[A-Z]{2,2}'
    return df.loc[df['code'].str.fullmatch(regex)]


class Command(BaseCommand):
    help = 'Parses Expereact and updates DB entries and locations.'

    def handle(self, *args, **options):

        def update_records(df_expereact):
            """
            Commit a pandas.DataFrame to database through the Bottle model:
            - Add items with 'id' that is not present in the database.
            - Remove items from the database where 'id' is not present in the supplied DataFrame
            - Update items where the id is already in database. Only location and owner (and consequently code) are
                expected to change. The implementation would however allow for overwriting supplier, price, description,
                and quantity as well.
            :param df_expereact: pandas.DataFrame
            """
            bottles_for_deletion = Bottle.objects.exclude(id__in=df_expereact['id'])
            deleted_ids = [bottle.id for bottle in bottles_for_deletion]
            bottles_for_deletion.delete()
            bottles = []
            for i, row in df_expereact.iterrows():
                bottles.append(Bottle(id=row['id'],
                                      owner=row['owner'],
                                      location=row['location'],
                                      supplier=row['supplier'],
                                      price=row['price'],
                                      description=row['description'],
                                      quantity=row['quantity'],
                                      ))
            for bottle in bottles:
                """
                Note: This is inefficient since we do len(bottles) roundtrips to the DB. However, it is convenient 
                because save() will handle both INSERT and UPDATE use-cases simultaneously. bulk_create() and
                bulk_update(), AFAIK, don't do that.
                """
                bottle.save()

            return deleted_ids

        self.stdout.write('####################################################\n'
                          'Running database update from updateFromExpereact.py\n'
                          '####################################################')
        self.stdout.write(f'Date: {datetime.date.today().strftime("%d.%m.%Y")}')
        self.stdout.write(f'Time: {datetime.datetime.now().strftime("%H:%M:%S")}')
        initial_id_in_db = list(Bottle.objects.only('id'))

        debug = True
        if debug is True:
            self.stdout.write(self.style.WARNING('WARNING: Debug mode turned on. Using local copy of Expereact data.'))
        table = parse_expereact(debug=debug)
        df_parsed = convert_table_to_df(table)
        df_clean = cleanup(df_parsed)
        df_filtered = filter_groups(df_clean)
        deleted_ids = update_records(df_filtered)
        final_id_in_db = list(Bottle.objects.only('id'))

        self.stdout.write(f'Deleted records: {deleted_ids}')
        self.stdout.write(f'Deleted records (by comparing state before and after): {list(set(initial_id_in_db) - set(final_id_in_db))}')
        self.stdout.write(f'New records: {list(set(final_id_in_db) - set(initial_id_in_db))}')
        self.stdout.write(self.style.SUCCESS(f'SUCCESS: updateFromExpereact.py finished at '
                                             f'{datetime.datetime.now().strftime("%H:%M:%S")}\n'))
