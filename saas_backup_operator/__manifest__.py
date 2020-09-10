# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": """SaaS: Backup operator""",
    "summary": """SHORT INTRO""",
    "category": "Hidden",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=13.0",
    "images": [],
    "version": "13.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/13.0/saas_backup_operator/",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "saas", "odoo_backup_sh",
        "odoo_backup_sh_google_disk",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/saas_db.xml',
        'data/ir_cron.xml',
        'views/odoo_backup_sh_views.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "SaaS: Backup operator",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "SHORT INTRO",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}