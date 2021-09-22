from odoo.tests import HttpCase
from odoo.addons.saas.tools import jsonrpc
from odoo.addons.saas.tests.common_saas_test import Common
from slugify import slugify

DB_PREFIX = "saas_domain_names_test_"
DB_TEMPLATE_NAME = DB_PREFIX + "template"
DB_NAME = slugify(DB_PREFIX + "db")


class TestMain(HttpCase, Common):
    def get_operator(self):
        return self.env.ref("saas.local_operator")

    def test_domain_workflow(self):
        self.drop_dbs([DB_TEMPLATE_NAME, DB_NAME])

        env = self.env(context=dict(self.env.context, test_queue_job_no_delay=True))
        operator = self.get_operator()

        # create template and template operator
        template = env["saas.template"].create(
            {"template_module_ids": [(0, 0, {"name": "test_saas_build"})]}
        )

        template_operator = env["saas.template.operator"].create(
            {
                "operator_id": operator.id,
                "template_id": template.id,
                "operator_db_name": DB_TEMPLATE_NAME,
            }
        )

        # deploy template database
        env["saas.template.operator"].preparing_template_next()

        # create build from template
        db = template_operator.create_db({}, DB_NAME)

        # for any case - unmap domain from operator
        # that happens after running previous test
        operator.unmap_domain("test1.localhost")

        # create domain record
        dn = env["saas.domain.name"].create(
            {"name": "test1.localhost", "operator_id": operator.id}
        )

        # make sure, that before setting database it is assigned to build
        response = self.url_open(
            "http://test1.localhost:8069/test_saas_build/get_db_name"
        )
        self.assertEqual(response.status_code, 404)

        # assign domain name to build
        db.write({"domain_name_id": dn.id})

        # make sure, you can access to build using assigned domain name
        response = self.url_open(
            "http://test1.localhost:8069/test_saas_build/get_db_name"
        )
        self.assertEqual(response.text, DB_NAME)
