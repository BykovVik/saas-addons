# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# Copyright 2020-2021 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict
import string

from odoo import models, fields
import odoo.addons.saas_cluster_simple.main as cluster


class SAASOperator(models.Model):
    _name = 'saas.operator'
    _description = 'Database Operator'

    name = fields.Char(required=True)
    # list of types can be extended via selection_add
    type = fields.Selection([
        ('local', 'Same Instance'),
    ], 'Type')
    global_url = fields.Char('Master URL (Server-to-Server)', required=True, help='URL for server-to-server communication ')
    # host = fields.Char()
    # port = fields.Char()
    db_url_template = fields.Char('DB URLs', help='Avaialble variables: {db_name}')
    template_operator_ids = fields.One2many('saas.template.operator', 'operator_id')

    def get_mandatory_modules(self):
        return ["auth_quick"]

    def _create_db(self, template_db, db_name, demo, lang='en_US'):
        """Synchronous db creation"""
        if not self:
            return
        elif self.type != 'local':
            raise NotImplementedError()

        return cluster.create_db(template_db, db_name, demo, lang)

    def _drop_db(self, db_name):
        if not self:
            return
        elif self.type != 'local':
            raise NotImplementedError()

        return cluster.drop_db(db_name)

    def _install_modules(self, db_name, modules):
        if self.type != 'local':
            raise NotImplementedError()

        return cluster.install_modules(db_name, modules)

    def install_modules(self, template_id, template_operator_id):
        self.ensure_one()
        modules = [module.name for module in template_id.template_module_ids]
        modules = [('name', 'in', self.get_mandatory_modules() + modules)]
        self._install_modules(template_operator_id.operator_db_name, modules)
        template_operator_id.state = 'post_init'
        self.with_delay().post_init(template_id, template_operator_id)

    def _post_init(self, db_name, template_post_init):
        if self.type != 'local':
            raise NotImplementedError()

        return cluster.post_init(db_name, template_post_init)

    def post_init(self, template_id, template_operator_id):
        self.ensure_one()
        self._post_init(template_operator_id.operator_db_name, template_id.template_post_init)
        template_operator_id.state = 'done'

    def _map_domain(self, domain, db_name):
        if self.type != "local":
            raise NotImplementedError()

        return cluster.map_domain(domain, db_name)

    def map_domain(self, domain, db_name):
        self.ensure_one()
        # TODO: add check if domain is valid
        self._map_domain(domain, db_name)

    def _unmap_domain(self, domain):
        if self.type != "local":
            raise NotImplementedError()

        return cluster.unmap_domain(domain)

    def unmap_domain(self, domain):
        self.ensure_one()
        if not domain:
            return
        self._unmap_domain(domain)

    def get_db_url(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url_template.format(db_name=db.name)

    def generate_db_name(self):
        self.ensure_one()
        sequence = self.env['ir.sequence'].next_by_code('saas.db')
        return "fast-build-{unique_id}".db_name_template.format(unique_id=sequence)

    def _get_mandatory_args(self, db):
        self.ensure_one()
        return {
            'master_url': self.global_url,
            'build_id': db.id
        }

    @staticmethod
    def _get_mandatory_code():
        master = "env['ir.config_parameter'].create([{{'key': 'auth_quick.master', 'value': '{master_url}'}}])\n"
        build = "env['ir.config_parameter'].create([{{'key': 'auth_quick.build', 'value': '{build_id}'}}])\n"
        return master + build

    def _build_execute_kw(self, db_name, model, method, args, kwargs):
        if self.type != 'local':
            raise NotImplementedError()

        return cluster.execute_kw(db_name, model, method, args, kwargs)

    def build_execute_kw(self, build, model, method, args=None, kwargs=None):
        self.ensure_one()
        args = args or []
        kwargs = kwargs or {}
        return self._build_execute_kw(build.name, model, method, args, kwargs)

    def build_post_init(self, build, post_init_action, key_value_dict):
        key_value_dict.update(self._get_mandatory_args(build))
        code = self._get_mandatory_code() + post_init_action
        action = {
            'name': 'Build Code Eval',
            'state': 'code',
            'model_id': 1,
            'code': string.Formatter().vformat(code, (), SafeDict(**key_value_dict))
        }
        action_ids = self.build_execute_kw(build, 'ir.actions.server', 'create', [action])
        self.build_execute_kw(build, 'ir.actions.server', 'run', [action_ids])

    def write(self, vals):
        if 'global_url' in vals:
            self._update_global_url(vals['global_url'])
        return super(SAASOperator, self).write(vals)

    def _update_global_url(self, url):
        self.ensure_one()
        code = "env['ir.config_parameter'].set_param('auth_quick.master', '{}')\n".format(url)
        builds = self.env['saas.db'].search([('operator_id', '=', self.id), ('type', '=', 'build')])
        action = {
            'name': 'Build Code Eval',
            'state': 'code',
            'model_id': 1,
            'code': code,
        }
        for build in builds.filtered(lambda build: build.state == "done"):
            action_ids = self.build_execute_kw(build, 'ir.actions.server', 'create', [action])
            self.build_execute_kw(build, 'ir.actions.server', 'run', [action_ids])

    def notify_users(self, message, title=None, message_type=None):
        manager_users = self.env.ref('saas.group_manager').users
        if message_type == 'success':
            manager_users.notify_success(message=message, title=title, sticky=True)
        elif message_type == 'info':
            manager_users.notify_info(message=message, title=title, sticky=True)
        else:
            manager_users.notify_default(message=message, title=title, sticky=True)


class SafeDict(defaultdict):
    def __missing__(self, key):
        return '{' + key + '}'
