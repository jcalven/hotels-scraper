from hotscrape import sql
from tests.test_base import *

class TestSQL(TestBase):

    def test_db_upsert(self):

        search_dict = self.search_dict
        schema = self.schema

        search_dict_ = hs.ensure_search_format(search_dict)
        url = hs.generate_url(**search_dict_)
        soup = hs.get_hotels_page(url, max_scroll=1)
        res = hs.get_attributes(soup, **search_dict_)

        df_search, df_attributes = hs.get_dfs(search_dict_, res)
        conn = sql.create_database("./test_sql", schema)

        sql.to_sql(df_search, "search", conn)
        sql.to_sql(df_attributes, "hotels", conn)

