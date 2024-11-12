# -*- coding: utf-8 -*-
# Copyright 2023-Today ModuleCreator.
# Part of ModuleCreator. See LICENSE file for full copyright and licensing details.
import base64
from odoo import api, fields, models, tools, _
from odoo.tools.image import is_image_size_above
from odoo.exceptions import ValidationError
from odoo.addons.web_editor.tools import get_video_embed_code, get_video_thumbnail


class PropertyProject(models.Model):
    _name = "property.project"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Property Project Details"

    # Project Details
    name = fields.Char(string="Name", required=True, translate=True)
    project_sequence = fields.Char(string="Code", required=True)
    image_1920 = fields.Image(string="Image")
    is_sub_project = fields.Boolean(default=True)
    project_for = fields.Selection([("rent", "Rent"),
                                    ("sale", "Sale")],
                                   string="Project For",
                                   required=True)
    property_type = fields.Selection([("residential", "Residential"),
                                      ("commercial", "Commercial"),
                                      ("industrial", "Industrial"),
                                      ("land", "Land"), ],
                                     string="Property Type",
                                     required=True)
    property_subtype_id = fields.Many2one("property.sub.type",
                                          string="Property Subtype",
                                          required=True,
                                          domain="[('type','=',property_type)]")
    status = fields.Selection([("draft", "Draft"),
                               ("available", "Available"),
                               ("cancel", "Cancel"),
                               ("closed", "Closed"), ],
                              default="draft")
    landlord_id = fields.Many2one("res.partner",
                                  string="Landlord",
                                  domain="[('user_type','=','landlord')]")
    # Company & Currency
    company_id = fields.Many2one("res.company",
                                 string="Company",
                                 default=lambda self: self.env.company,
                                 required=True)
    currency_id = fields.Many2one("res.currency",
                                  related="company_id.currency_id",
                                  string="Currency",
                                  store=True)

    # Additional Details
    date_of_project = fields.Date(string="Date of Project", required=True)
    construction_year = fields.Char(string="Construction Year")
    property_brochure = fields.Binary(string="Brochure")
    brochure_name = fields.Char(string="Brochure Name")
    website = fields.Char(string='Website')

    # Address
    region_id = fields.Many2one("property.region", string="Region")
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street2", translate=True)
    city_id = fields.Many2one('property.res.city')
    zip = fields.Char(string="Zip", translate=True)
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 ondelete='restrict')

    # Lat Long
    longitude = fields.Char(string='Longitude')
    latitude = fields.Char(string='Latitude')

    # Documents
    document_ids = fields.One2many("project.document.line",
                                   "project_id", string="Docs")

    # Availability
    avail_description = fields.Boolean(string="Descriptions")
    avail_amenity = fields.Boolean(string="Amenities")
    avail_specification = fields.Boolean(string="Specifications")
    avail_image = fields.Boolean(string="Images")
    avail_nearby_connectivity = fields.Boolean(string="Nearby Connectivity")

    # SubProject
    sub_project_ids = fields.One2many(
        "property.sub.project", "property_project_id")

    # Basic Details
    sale_lease = fields.Selection([("rent", "Rent"),
                                   ("sale", "Sale")],
                                  string="Sale Lease", default="rent")
    total_floors = fields.Integer(string="Total Floors")
    units_per_floor = fields.Integer(string="Units per Floor")
    total_subproject = fields.Integer(string="Total Sub Project",
                                      compute="_compute_sub_project_count")
    total_area = fields.Float(string="Total Property Area",
                              compute="compute_properties_statics")
    available_area = fields.Float(string="Available Area",
                                  compute="compute_properties_statics")
    total_values = fields.Monetary(string="Total Value of Project",
                                   compute="compute_properties_statics")
    total_maintenance = fields.Monetary(string="Total Maintenance",
                                        compute="compute_properties_statics")
    total_collection = fields.Monetary(string="Total Collection",
                                       compute="compute_properties_statics")
    scope_of_collection = fields.Monetary(string="Scope of Collection",
                                          compute="compute_properties_statics")

    # Description
    description = fields.Html(string="Description")

    # Amenities
    property_amenity_ids = fields.Many2many("property.amenities")

    # Specifications
    property_specification_ids = fields.Many2many("property.specification")

    # Images
    project_image_ids = fields.One2many("project.images.line", "project_id",
                                        string="images")
    # Connectivity
    project_connectivity_ids = fields.One2many("project.connectivity.line",
                                               "project_id")

    # Other Details
    license_number = fields.Char(string="License No.")
    date_of_license = fields.Date(string="Date of License")

    # Count
    document_count = fields.Integer(compute="compute_count")
    sub_project_count = fields.Integer()
    unit_count = fields.Integer(compute="compute_count")
    available_unit_count = fields.Integer(compute="compute_count")
    sold_count = fields.Integer(compute="compute_count")
    rent_count = fields.Integer(compute="compute_count")

    # Units
    property_unit_ids = fields.One2many("property.details",
                                        "property_project_id")
    floor_created = fields.Integer()

    # On delete
    @api.ondelete(at_uninstall=False)
    def _unlink_property_project(self):
        for rec in self:
            if rec.is_sub_project and rec.sub_project_ids:
                raise ValidationError(_("Cannot delete project, please delete corresponding subproject before deletion"))
            elif not rec.is_sub_project and rec.property_unit_ids:
                raise ValidationError(_("Cannot delete project, please delete corresponding units before deletion"))

    # Compute
    # Smart Button Count
    @api.depends('is_sub_project')
    def compute_count(self):
        for rec in self:
            rec.document_count = self.env["project.document.line"].search_count(
                [("project_id", "in", [rec.id])])
            rec.unit_count = self.env['property.details'].search_count(
                [('property_project_id', 'in', [rec.id])])
            rec.available_unit_count = self.env['property.details'].search_count(
                [('property_project_id', 'in', [rec.id]), ('stage', '=', 'available')])
            rec.sold_count = self.env['property.details'].search_count(
                [('property_project_id', 'in', [rec.id]), ('stage', 'in', ['sale', 'sold'])])
            rec.rent_count = self.env['property.details'].search_count(
                [('property_project_id', 'in', [rec.id]), ('stage', '=', 'on_lease')])

    @api.depends("sub_project_ids")
    def _compute_sub_project_count(self):
        for rec in self:
            rec.total_subproject = (self.env["property.sub.project"].search_count(
                [("property_project_id", "in", [rec.id])]))

    @api.depends('sale_lease', 'is_sub_project')
    def compute_properties_statics(self):
        for rec in self:
            total_area = 0.0
            available_area = 0.0
            total_values = 0.0
            total_maintenance = 0.0
            total_collection = 0.0
            scope_of_collection = 0.0
            properties = self.env['property.details'].sudo()
            project_domain = [('property_project_id', 'in', [rec.id])]
            subprojects = self.env['property.sub.project'].sudo().search(
                [('property_project_id', 'in', [rec.id])]).mapped('id')
            properties_ids = self.env['property.details'].sudo().search(
                project_domain).mapped('id')
            properties_sale = self.env['property.vendor'].sudo().search(
                [('property_id', 'in', properties_ids)])
            properties_tenancy = self.env['tenancy.details'].sudo().search(
                [('property_id', 'in', properties_ids)])
            if rec.sale_lease == 'sale':
                sale_domain = project_domain + \
                              [('sale_lease', '=', 'for_sale')]
                if rec.is_sub_project:
                    sale_domain = sale_domain + \
                                  [('subproject_id', 'in', subprojects)]
                total_area = sum(properties.search(
                    sale_domain).mapped('total_area'))
                available_area = sum(properties.search(
                    sale_domain + [('stage', '=', 'available')]).mapped('total_area'))
                total_values = sum(properties.search(
                    sale_domain).mapped('price'))
                total_maintenance = sum(properties.search(
                    sale_domain + [('is_maintenance_service', '=', True)]).mapped('total_maintenance'))
                total_collection = sum(properties_sale.mapped('paid_amount'))
                scope_of_collection = sum(
                    properties_sale.mapped('remaining_amount'))
            if rec.sale_lease == 'rent':
                tenancy_domain = [
                                     ('sale_lease', '=', 'for_tenancy')] + project_domain
                if rec.is_sub_project:
                    tenancy_domain = tenancy_domain + \
                                     [('subproject_id', 'in', subprojects)]
                total_area = sum(properties.search(
                    tenancy_domain).mapped('total_area'))
                available_area = sum(properties.search(
                    tenancy_domain + [('stage', '=', 'available')]).mapped('total_area'))
                total_values = sum(properties.search(
                    tenancy_domain).mapped('price'))
                total_maintenance = sum(properties.search(
                    tenancy_domain + [('is_maintenance_service', '=', True)]).mapped('total_maintenance'))
                total_collection = sum(
                    properties_tenancy.mapped('paid_tenancy'))
                scope_of_collection = sum(
                    properties_tenancy.mapped('remain_tenancy'))
            rec.total_area = total_area
            rec.available_area = available_area
            rec.total_values = total_values
            rec.total_maintenance = total_maintenance
            rec.total_collection = total_collection
            rec.scope_of_collection = scope_of_collection

    # Onchange
    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    # Property Sub Type Domain
    @api.onchange('property_type')
    def onchange_property_sub_type(self):
        for rec in self:
            rec.property_subtype_id = False

    # Default Valuation
    @api.onchange('project_for')
    def onchange_valuation_sale_lease(self):
        for rec in self:
            rec.sale_lease = rec.project_for

    # Button
    # Smart Button

    def action_document_count(self):
        action = {
            "name": "Documents",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,list,form",
            "domain": [("project_id", "=", self.id)],
            "res_model": "project.document.line",
            "target": "current",
        }
        if self.status == "draft":
            action['context'] = {'default_project_id': self.id}
            return action
        else:
            action['context'] = {'create': False, 'edit': False}
            return action

    def action_sub_project_count(self):
        return {
            "name": "Sub Projects",
            "type": "ir.actions.act_window",
            "domain": [("property_project_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": "property.sub.project",
            "target": "current",
        }

    def action_view_unit(self):
        return {
            "name": "Units",
            "type": "ir.actions.act_window",
            "domain": [("property_project_id", "=", self.id)],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": "property.details",
            "target": "current",
        }

    def action_view_available_unit(self):
        return {
            "name": "Available Units",
            "type": "ir.actions.act_window",
            "domain": [("property_project_id", "=", self.id), ('stage', '=', 'available')],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": "property.details",
            "target": "current",
        }

    def action_view_sold_unit(self):
        return {
            "name": "Sold / Sale Units",
            "type": "ir.actions.act_window",
            "domain": [("property_project_id", "=", self.id), ('stage', 'in', ['sold', 'sale'])],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": "property.details",
            "target": "current",
        }

    def action_view_rent_unit(self):
        return {
            "name": "Rent Units",
            "type": "ir.actions.act_window",
            "domain": [("property_project_id", "=", self.id), ('stage', '=', 'on_lease')],
            "view_mode": "list,form",
            'context': {'create': False},
            "res_model": "property.details",
            "target": "current",
        }

    # G-map Location
    def action_gmap_location(self):
        if self.longitude and self.latitude:
            longitude = self.longitude
            latitude = self.latitude
            http_url = 'https://maps.google.com/maps?q=loc:' + latitude + ',' + longitude
            return {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': http_url,
            }
        else:
            raise ValidationError(
                "! Enter Proper Longitude and Latitude Values")

    def action_status_draft(self):
        self.status = 'draft'

    def action_status_available(self):
        self.status = 'available'


# Project Document
class ProjectDocumentLine(models.Model):
    _name = "project.document.line"
    _description = "Documents for Project"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    document_name = fields.Char(string="Document Name")
    document_file = fields.Binary(string="Document", required=True)
    user_id = fields.Many2one("res.users", string="Added by", required=True)
    project_id = fields.Many2one("property.project")


# Project Connectivity Line
class ProjectConnectivityLine(models.Model):
    _name = 'project.connectivity.line'
    _description = "Project Connectivity Line"

    project_id = fields.Many2one('property.project')
    connectivity_id = fields.Many2one('property.connectivity',
                                      string="Nearby Connectivity")
    name = fields.Char(string="Name", translate=True)
    image = fields.Image(related="connectivity_id.image", string='Images')
    distance = fields.Char(string="Distance", translate=True)


# Property Images
class ProjectImagesLine(models.Model):
    _name = 'project.images.line'
    _description = 'Project Image Line'
    _inherit = ["image.mixin"]
    _order = "sequence, id"

    title = fields.Char(string='Title', translate=True)
    sequence = fields.Integer(default=10)
    project_id = fields.Many2one('property.project')
    image = fields.Image(string='Images')
    video_url = fields.Char("Video URL",
                            help="URL of a video for showcasing your property.")
    embed_code = fields.Html(compute="_compute_embed_code",
                             sanitize=False)
    can_image_1024_be_zoomed = fields.Boolean(string="Can Image 1024 be zoomed",
                                              compute="_compute_can_image_1024_be_zoomed",
                                              store=True)

    @api.depends("image", "image_1024")
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = (
                    image.image and is_image_size_above(image.image, image.image_1024))

    @api.onchange("video_url")
    def _onchange_video_url(self):
        if not self.image:
            thumbnail = get_video_thumbnail(self.video_url)
            self.image = thumbnail and base64.b64encode(thumbnail) or False

    @api.depends("video_url")
    def _compute_embed_code(self):
        for image in self:
            image.embed_code = get_video_embed_code(image.video_url) or False

    @api.constrains("video_url")
    def _check_valid_video_url(self):
        for image in self:
            if image.video_url and not image.embed_code:
                raise ValidationError(
                    _(
                        "Provided video URL for '%s' is not valid. Please enter a valid video URL.",
                        image.name,
                    )
                )
