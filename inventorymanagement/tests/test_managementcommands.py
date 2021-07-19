from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from ..management.commands.parseexpereact import parse_expereact, convert_table_to_df


class ParseExpereactTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # we call this only once since it takes ca. 15 seconds (we still call it a second time in the integration test)
        # This should be run with debug = False every once in a while to assure the expereact layout has not changed.
        cls.parsed_data = parse_expereact(debug=True)

    def test_parseexpereact_runs_successfully(self):
        out = StringIO()
        call_command('parseexpereact', stdout=out)
        self.assertIn('SUCCESS', out.getvalue())

    def test_parseexpereact_parse_returns_list(self):
        self.assertIs(type(self.parsed_data), list)

    def test_parseexpereact_parsed_list_has_length_14_on_second_axis(self):
        """
        We should receive a nested list where the first axis length is equal to the numbers of bottles in the database
        and the second axis length is 14.
        We specifically test for this as we depend on it by a hardcoded constraint.
        """
        for i in self.parsed_data:
            self.assertEqual(len(i), 14)

    def test_parseexpereact_gives_intermediary_dataframe_with_correct_column_names(self):
        df = convert_table_to_df(self.parsed_data)
        self.assertEqual(df.columns.to_list(), ['Supplier', 'Catalogue Nr', 'Product Description', 'Group Code',
       'User Name', 'Location', 'Bottle Nr', 'Order Nr', 'Quantity',
       'Price (CHF)', 'Order Date', 'Reception Date', 'Status', 'Comment'])

