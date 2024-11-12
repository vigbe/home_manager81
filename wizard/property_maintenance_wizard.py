# -*- coding: utf-8 -*-
# Copyright 2020-Today ModuleCreator.
# Part of ModuleCreator. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class PropertyMaintenance(models.TransientModel):
    _name = 'maintenance.wizard'
    _description = 'Crating Maintenance Request'

    name = fields.Char(string='Request', translate=True)
    property_id = fields.Many2one('property.details', string='Property')
    maintenance_type_id = fields.Many2one('product.template',
                                          string='Type',
                                          domain=[('is_maintenance', '=', True)])
    maintenance_team_id = fields.Many2one('maintenance.team', string='Team')

    # Default Get
    @api.model
    def default_get(self, fields):
        res = super(PropertyMaintenance, self).default_get(fields)
        active_id = self._context.get('active_id')
        res['property_id'] = active_id
        return res

    def maintenance_request(self):
        self.env['maintenance.request'].create({
            'name': self.name,
            'landlord_id': self.property_id.landlord_id.id,
            'maintenance_type_id': self.maintenance_type_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'property_id': self.property_id.id,
            'request_date': fields.Date.today()
        })
