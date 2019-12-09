import testing_utilities as tu
from mdr import multi_dump as md


class TestDump:
    @classmethod
    def setup_class(cls):
        tu.pgts.get_and_patch_temporary_bkp_dir()
        tu.pgts.init_db()

    @classmethod
    def teardown_class(cls):
        tu.pgts.del_db()

    def test_get_schema_names(self):
        result = md.get_schema_list(tu.pgts.testing_pgc, tu.TESTING_DATABASE)
        assert set(result) == set(['public'] + tu.SampleData.schema_names)

