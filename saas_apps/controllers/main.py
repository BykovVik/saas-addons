# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo import http
from odoo.addons.saas_public.controllers.saas_public import SaaSPublicController
import urllib.parse

DB_TEMPLATE = 'new_build_'

class SaaSAppsController(Controller):


    @route('/price', type='http', auth='public', website=True)
    def user_page(self, **kw):
        apps = http.request.env['saas.line'].sudo()
        return http.request.render('saas_apps.index', {
            'apps': apps.search([('allow_to_sell', '=', True)])
        })

    @http.route(['/refresh'], type='json', auth='public')
    def catch_app_click(self, **kw):
        apps = http.request.env['saas.line']
        apps.refresh_lines()
        return {}

    @http.route(['/what_dependencies'], type='json', auth='public')
    def what_dependencies(self, **kw):
        app_tech_name = kw['args'][0]
        app = http.request.env['saas.line'].sudo().search([('name', '=', app_tech_name)])
        return {
            'dependencies': app.dependencies_info('root')
        }

    # @http.route(['/what_dependencies_optimized'], type='json', auth='public')
    # def what_dependencies_optimized(self, **kw):
    #     apps = []
    #     for app_name in kw['args'][0]:
    #         app = http.request.env['saas.line'].sudo().search([('name', '=', app_name)])
    #         apps.append({app_name: app.dependencies_info('root')})
    #     return {
    #         'dependencies': apps
    #     }

class SaaSAppsPublicController(SaaSPublicController):
    @http.route(['/create_saas_template'], type='json', auth='public', website=True)
    def create_saas_template(self, **kw):
        templates = http.request.env['saas.template']
        installing_modules_names = kw['args'][0]
        saas_template = templates.sudo().create({
            'name': 'Template ' + str(len(templates.sudo().search([])) - 1),
            'template_demo': True,
            'public_access': True
        })
        for name in installing_modules_names:
            saas_template.template_module_ids += http.request.env['saas.module'].sudo().search([('name', '=', name)])
        saas_operator = http.request.env['saas.operator'].sudo().search([('db_url_template', '=', 'http://{db_name}.{db_id}.127.0.0.1.nip.io')])
        saas_template_operator = http.request.env['saas.template.operator'].sudo().create({
            'template_id': saas_template.id,
            'operator_id': saas_operator.id,
            'operator_db_name': DB_TEMPLATE + str(len(http.request.env['saas.template.operator'].sudo().search([])) + 1),
        })
        http.request.env['saas.template.operator'].sudo().preparing_template_next()
        # message = '''Template\'s deployment with name {} is creating
        # and will be ready in a few minutes.'''.format(r.operator_db_name)
        # self.operator_id.notify_users(message, message_type='info')
        return {
            'template': saas_template.id,
            'template_operator': saas_template_operator.id,
            'link': '0',
            'Error': '0',
            'state': 'Database creating...'
        }

    @http.route(['/check_saas_template'], type='json', auth='public', website=True)
    def is_build_created(self, **kw):
        template = http.request.env['saas.template'].sudo().browse(kw['args'][0]['template'])
        template_operator = http.request.env['saas.template.operator'].sudo().browse(kw['args'][0]['template_operator'])
        if len(template) > 0 and template_operator.random_ready_operator_check():
            kwargs = {}
            if template and template.public_access:
                template_operator_id = template.operator_ids.random_ready_operator()
                build = template_operator_id.create_db(kwargs, with_delay=False)
                build_url = build.get_url()
                token_obj = request.env['auth_quick_master.token'].sudo().create({
                    'build': build.id,
                    'build_login': 'admin',
                })
                return {
                    'template': '0',
                    'template_operator': '0',
                    'link': urllib.parse.urljoin(build_url, '/auth_quick/check-token?token={}'.format(token_obj.token)),
                    'Error': '0',
                    'state': template_operator.state
                }
            else:
                return {
                    'template': '0',
                    'template_operator': '0',
                    'link': '0',
                    'Error': '1',
                    'state': template_operator.state
                }
        else:
            return {
                'template': template.id,
                'template_operator': template_operator.id,
                'link': '0',
                'Error': '0',
                'state': template_operator.state
            }
