import testing_utilities as tu
import appconfig
import multi_dump as md
import random


class TestCmdTemplate:
    @classmethod
    def setup_class(cls):
        tu.pgts.get_and_patch_temporary_bkp_dir()

    def test__dump_cmd_template(self):
        backup_name = md.get_default_bkp_name()
        file_name = md.get_file_name(tu.TESTING_DATABASE)
        path_config = {
            'backup_path': appconfig.BKP_BASE_PATH,
            'backup_name': f'{backup_name}',
            'db_name': tu.TESTING_DATABASE,
            'file_name': file_name
        }
        file_path = md.compose_bkp_file_path(**path_config)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        template_config = {
            'db': tu.pgts.testing_pgc,
            'db_name': tu.TESTING_DATABASE,
            'file_path': file_path,
            'bkp_name': md.get_default_bkp_name(),
            'caller': 'test_script'
        }
        print(md._dump_cmd_template(**template_config))


    def test__dump_cmd_template_schema(self):
        backup_name = md.get_default_bkp_name()
        file_name = md.get_file_name(tu.TESTING_DATABASE)
        path_config = {
            'backup_path': appconfig.BKP_BASE_PATH,
            'backup_name': f'{backup_name}',
            'db_name': tu.TESTING_DATABASE,
            'file_name': file_name
        }
        file_path = md.compose_bkp_file_path(**path_config)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        template_config = {
            'db': tu.pgts.testing_pgc,
            'db_name': tu.TESTING_DATABASE,
            'file_path': file_path,
            'bkp_name': md.get_default_bkp_name(),
            'caller': 'test_script',
            'schema': random.choice(tu.SampleData.schema_names)
        }
        print(md._dump_cmd_template(**template_config))

