import logging
from odoo import fields, SUPERUSER_ID, api
from odoo.http import request, route
from odoo import http, tools, _
from xlrd.timemachine import xrange
from io import BytesIO
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

_logger = logging.getLogger(__name__)


# My Portal Sell and Rent Contract Count
class RentalCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        sell_contract = request.env['property.vendor']
        rent_contract = request.env['tenancy.details']

        domain = [('customer_id', '=', request.env.user.partner_id.id)]
        tenancy_domain = [('tenancy_id', '=', request.env.user.partner_id.id)]

        # sell contract count
        if 'sell_contract_count' in counters:
            values['sell_contract_count'] = sell_contract.sudo().search_count(domain)

        # rent contract count
        if 'rent_contract_count' in counters:
            values['rent_contract_count'] = rent_contract.sudo().search_count(tenancy_domain)

        # maintenance count
        if 'maintenance_count' in counters:
            tenancies = rent_contract.sudo().search(tenancy_domain).mapped('id')
            maintenance_count = request.env['maintenance.request'].sudo().search_count([('tenancy_id', 'in', tenancies)])
            values['maintenance_count'] = maintenance_count
        return values


# Controllers
class RentalPortalWebsite(http.Controller):
    # Tree view sale Contract
    @http.route(['/my/sell-contract/',
                 '/my/sell-contract/page/<int:page>'], type='http', auth="user", website=True)
    def rental_user_sell_contract(self, page=0, **kw):
        customer_id = request.env.user.partner_id.id

        sell_contract_sudo = request.env['property.vendor'].sudo()
        domain = [('customer_id', '=', customer_id)]

        sell_contract_count = sell_contract_sudo.search_count(domain)

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=sell_contract_count,
            page=page,
            step=15,
            url_args=''
        )

        sell_contracts = sell_contract_sudo.search(domain, offset=pager['offset'], limit=15)

        values = {
            'contract': sell_contracts,
            'page_name': 'sell_contract_list_view',
            'pager': pager,
        }
        return request.render('rental_management.rental_user_sell_contract_info', values)

    # Form View Sale Contract
    @http.route(['/my/sell-contract/information/<model("property.vendor"):b>'], type='http', auth="user",
                website=True)
    def rental_user_sell_contract_detail(self, b):
        if b.customer_id.id == request.env.user.partner_id.id:
            sell_contract_sudo = request.env['property.vendor'].sudo()
            sell_contract_ids = sell_contract_sudo.search([('customer_id', '=', request.env.user.partner_id.id)]).ids

            main_index = sell_contract_ids.index(b.id)
            prev_url = None
            next_url = None

            if main_index != 0:
                prev_record = sell_contract_sudo.browse(sell_contract_ids[main_index - 1])
                prev_url = f'/my/sell-contract/information/{request.env["ir.http"]._slug(prev_record)}'

            if main_index != (len(sell_contract_ids) - 1):
                next_record = sell_contract_sudo.browse(sell_contract_ids[main_index + 1])
                next_url = f'/my/sell-contract/information/{request.env["ir.http"]._slug(next_record)}'

            values = {
                'sell_contract': b.sudo(),
                'page_name': 'sell_contract_form_view',
                'prev_record': prev_url,
                'next_record': next_url,
            }
            return request.render('rental_management.rental_user_sell_contract_details', values)
        else:
            return request.redirect('/')

    # Tree View Rent Contract
    @http.route(['/my/rent-contract/',
                 '/my/rent-contract/page/<int:page>'], type='http', auth="user", website=True)
    def rental_user_rent_contract(self, page=0, **kw):

        rent_contract_sudo = request.env['tenancy.details'].sudo()
        domain = [('tenancy_id', '=', request.env.user.partner_id.id)]

        rent_contract_count = rent_contract_sudo.search_count(domain)

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=rent_contract_count,
            page=page,
            step=15,
            url_args=''
        )

        rent_contracts = rent_contract_sudo.search(domain, offset=pager['offset'], limit=15)

        ctx = {
            'contract': rent_contracts,
            'page_name': 'rent_contract_list_view',
            'pager': pager,
        }

        return request.render('rental_management.rental_user_rent_contract_info',  ctx)

    # Form View Rent Contract
    @http.route(['/my/rent-contract/information/<model("tenancy.details"):rc>'], type='http', auth="user",
                website=True)
    def rental_user_rent_contract_detail(self, rc):
        maintenance_rec = request.env['product.template'].sudo().search(
            [('is_maintenance', '=', True)])
        if rc.tenancy_id.id == request.env.user.partner_id.id:

            rent_contract_sudo = request.env['tenancy.details'].sudo()
            rent_contract_ids = rent_contract_sudo.search([('tenancy_id', '=', request.env.user.partner_id.id)]).ids

            main_index = rent_contract_ids.index(rc.id)
            prev_url = None
            next_url = None

            if main_index != 0:
                prev_record = rent_contract_sudo.browse(rent_contract_ids[main_index - 1])
                prev_url = f'/my/rent-contract/information/{request.env["ir.http"]._slug(prev_record)}'

            if main_index != (len(rent_contract_ids) - 1):
                next_record = rent_contract_sudo.browse(rent_contract_ids[main_index + 1])
                next_url = f'/my/rent-contract/information/{request.env["ir.http"]._slug(next_record)}'

            values = {
                'rent': rc.sudo(),
                'maintenance_type': maintenance_rec,
                'page_name': 'rent_contract_form_view',
                'prev_record': prev_url,
                'next_record': next_url,
            }
            return request.render('rental_management.rental_user_rent_contract_details', values)
        else:
            return request.redirect('/')

    # Maintenance Request Creation
    @http.route(['/my/rent-contract/information/maintenance-request'], type='http', auth="user",
                website=True)
    def rental_rent_maintenance_request(self, **kw):
        tenancy_id = request.env['tenancy.details'].sudo().browse(
            int(kw.get('rent')))
        name = kw.get('request') if kw.get('request') else (
            str(tenancy_id.tenancy_seq) + " Maintenance Request")
        maintenance_type_id = int(kw.get('maintenance_type_id'))
        maintenance_rec = {
            'maintenance_type_id': maintenance_type_id if maintenance_type_id else False,
            'name': name,
            'landlord_id': tenancy_id.property_landlord_id.id,
            'property_id': tenancy_id.property_id.id,
            'tenancy_id': tenancy_id.id,
            'description': kw.get('desc')
        }
        maintenance_id = request.env['maintenance.request'].sudo().create(
            maintenance_rec)
        return request.redirect('/my/maintenance-request/')

    # Tree View of Maintenance request
    @http.route(['/my/maintenance-request/',
                 '/my/maintenance-request/page/<int:page>'], type='http', auth="user", website=True)
    def rental_user_maintenance_request(self, page=0, **kw):

        tenancies = request.env['tenancy.details'].sudo().search(
            [('tenancy_id', '=', request.env.user.partner_id.id)]).mapped('id')

        maintenance_sudo = request.env['maintenance.request'].sudo()
        domain = [('tenancy_id', 'in', tenancies)]

        maintenance_count = maintenance_sudo.search_count(domain)

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=maintenance_count,
            page=page,
            step=15,
            url_args=''
        )

        maintenance_requests = maintenance_sudo.search(domain, offset=pager['offset'], limit=15)

        ctx = {
            'maintenance_rec': maintenance_requests,
            'page_name': 'maintenance_request_list_view',
            'pager': pager,
        }
        return request.render('rental_management.rental_user_maintenance_info', ctx)

    # From Maintenance Request
    @http.route(['/my/maintenance-request/information/<model("maintenance.request"):mr>'], type='http', auth="user", website=True)
    def rental_user_maintenance_request_details(self, mr):

        tenancies = request.env['tenancy.details'].sudo().search([('tenancy_id', '=', request.env.user.partner_id.id)]).mapped('id')

        maintenance_request_sudo = request.env['maintenance.request'].sudo()
        maintenance_request_ids = maintenance_request_sudo.search([('tenancy_id', 'in', tenancies)]).ids

        main_index = maintenance_request_ids.index(mr.id)
        prev_url = None
        next_url = None

        if main_index != 0:
            prev_record = maintenance_request_sudo.browse(maintenance_request_ids[main_index - 1])
            prev_url = f'/my/maintenance-request/information/{request.env["ir.http"]._slug(prev_record)}'

        if main_index != (len(maintenance_request_ids) - 1):
            next_record = maintenance_request_sudo.browse(maintenance_request_ids[main_index + 1])
            next_url = f'/my/maintenance-request/information/{request.env["ir.http"]._slug(next_record)}'

        ctx = {
            'mr': mr.sudo(),
            'page_name': 'maintenance_request_form_view',
            'prev_record': prev_url,
            'next_record': next_url,
        }
        return request.render('rental_management.rental_user_maintenance_details', ctx)
