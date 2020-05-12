# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaasDb(models.Model):

    _inherit = "saas.db"

    max_users_limit = fields.Integer("Max Users Allowed")
    users_count = fields.Integer("Current No. Of Users", readonly=1)

    @api.constrains("max_users_limit")
    def _check_max_users_limit(self):
        for record in self:
            if record.max_users_limit < 1:
                raise ValidationError("Number of allowed max users must be at least 1")

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        if not self.max_users_limit:
            return

        _, model, res_id = self.xmlid_lookup("access_limit_max_users.max_users_limit")

        self.execute_kw(
            model, "write", [res_id],
            {"max_records": self.max_users_limit}
        )

    def read_values_from_build(self):
        vals = super(SaasDb, self).read_values_from_build()

        vals.update(
            users_count=self.execute_kw("res.users", "search_count", [])
        )

        if not self.max_users_limit:
            _, model, res_id = self.xmlid_lookup("access_limit_max_users.max_users_limit")
            vals.update(
                max_users_limit=self.execute_kw(model, "search_count", [("id", "=", res_id)], ["max_records"])[0]["max_records"]
            )

        return vals
