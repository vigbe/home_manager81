# -*- coding: utf-8 -*-
# Copyright 2020-Today ModuleCreator.
# Part of ModuleCreator. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class RentalConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_days = fields.Integer(string='Days', default=5,
                                   config_parameter='rental_management.reminder_days')
    sale_reminder_days = fields.Integer(string="Days ", default=3,
                                        config_parameter='rental_management.sale_reminder_days')
    invoice_post_type = fields.Selection([('manual', 'Invoice Post Manually'),
                                          ('automatically', 'Invoice Post Automatically')], string="Invoice Post",
                                         default='manual', config_parameter='rental_management.invoice_post_type')

    # Default Account Product
    installment_item_id = fields.Many2one('product.product', string="Installment Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_1', raise_if_not_found=False),
                                          config_parameter='rental_management.account_installment_item_id')
    deposit_item_id = fields.Many2one('product.product', string="Deposit Item",
                                      default=lambda self: self.env.ref('rental_management.property_product_2', raise_if_not_found=False),
                                      config_parameter='rental_management.account_deposit_item_id')
    broker_item_id = fields.Many2one('product.product', string="Broker Commission Item",
                                     default=lambda self: self.env.ref('rental_management.property_product_3', raise_if_not_found=False),
                                     config_parameter='rental_management.account_broker_item_id')
    maintenance_item_id = fields.Many2one('product.product', string="Maintenance Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_4', raise_if_not_found=False),
                                          config_parameter='rental_management.account_maintenance_item_id')
