# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaasDb(models.Model):

    _inherit = 'saas.db'

    expiration_date = fields.Datetime("Expiration date", default=lambda self: datetime.now() + timedelta(days=7))

    def write_values_to_build(self, build_env):
        super(SaasDb, self).write_values_to_build(build_env)
        build_env['ir.config_parameter'].set_param("saas_expiration_date", self.expiration_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))