# -*- coding: utf-8 -*-
# Copyright 2020-Today ModuleCreator.
# Part of ModuleCreator. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
import xlwt
import base64
from io import BytesIO


class PropertyXlsReport(models.TransientModel):
    _name = 'property.report.wizard'
    _description = 'Create Property Report'
    _rec_name = 'type'

    type = fields.Selection(
        [('tenancy', 'Rent'), ('sold', 'Property Sold')], string="Report For")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def action_property_xls_report(self):
        if self.type == "tenancy":
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet(
                'Rent Contract Details', cell_overwrite_ok=True)
            domain = [("start_date", ">=", self.start_date),
                      ("start_date", "<=", self.end_date)]
            record = self.env["tenancy.details"].search(domain)
            self.action_create_rent_contract_report(
                sheet=sheet1, record=record, workbook=workbook)
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<< SECOND SHEET>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            sheet2 = workbook.add_sheet(
                "Running Contracts", cell_overwrite_ok=True)
            record_running = self.env["tenancy.details"].search(
                domain + [("contract_type", "=", "running_contract")])
            self.action_create_rent_contract_report(
                sheet=sheet2, record=record_running, workbook=workbook)
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FORTH SHEET >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            sheet4 = workbook.add_sheet(
                "Closed Contracts", cell_overwrite_ok=True)
            record_closed = self.env["tenancy.details"].search(
                domain + [("contract_type", "=", "close_contract")])
            self.action_create_rent_contract_report(
                sheet=sheet4, record=record_closed, workbook=workbook)
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FIFTH SHEET >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            sheet5 = workbook.add_sheet(
                "Expired Contracts", cell_overwrite_ok=True)
            record_expired = self.env["tenancy.details"].search(
                domain + [("contract_type", "=", "expire_contract")])
            self.action_create_rent_contract_report(
                sheet=sheet5, record=record_expired, workbook=workbook)

            stream = BytesIO()
            workbook.save(stream)
            out = base64.encodebytes(stream.getvalue())

            attachment = self.env['ir.attachment'].sudo()
            filename = 'Rent Details' + ".xls"
            attachment_id = attachment.create(
                {'name': filename,
                 'type': 'binary',
                 'public': False,
                 'datas': out})
            if attachment_id:
                report = {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/%s?download=true' % (attachment_id.id),
                    'target': 'self',
                }
                return report

        elif self.type == "sold":
            workbook = xlwt.Workbook(encoding='utf-8')
            domain = [("date", ">=", self.start_date),
                      ("date", "<=", self.end_date)]
            sheet1 = workbook.add_sheet(
                'Property Sell Information', cell_overwrite_ok=True)
            sheet2 = workbook.add_sheet(
                'Sold Properties', cell_overwrite_ok=True)
            records = self.env["property.vendor"].search(domain)
            sold_record = self.env["property.vendor"].search(
                domain + [('stage', '=', 'sold')])
            self.action_create_sold_report(
                sheet=sheet1, record=records, workbook=workbook)
            self.action_create_sold_report(
                sheet=sheet2, record=sold_record, workbook=workbook)
            stream = BytesIO()
            workbook.save(stream)
            out = base64.encodebytes(stream.getvalue())
            attachment = self.env['ir.attachment'].sudo()
            filename = 'Sold Information' + ".xls"
            attachment_id = attachment.create(
                {'name': filename,
                 'type': 'binary',
                 'public': False,
                 'datas': out})
            if attachment_id:
                report = {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/%s?download=true' % (attachment_id.id),
                    'target': 'self',
                }
                return report

    def get_rent_stage(self, status):
        name = ""
        if status == "running_contract":
            name = "Running"
        elif status == "cancel_contract":
            name = "Cancel"
        elif status == "close_contract":
            name = "Close"
        elif status == "expire_contract":
            name = "Expire"
        else:
            name = "Draft"
        return name

    def get_property_type(self, type):
        name = ""
        if type == "residential":
            name = "Residential"
        elif type == "industrial":
            name = "Industrial"
        elif type == "commercial":
            name = "Commercial"
        elif type == "land":
            name = "Land"
        return name

    def get_measure_unit(self, measure_unit):
        unit = ""
        if measure_unit == "sq_ft":
            unit = "ft²"
        elif measure_unit == "sq_m":
            unit = "m²"
        elif measure_unit == "sq_yd":
            unit = "yd²"
        elif measure_unit == "cu_ft":
            unit = "ft³"
        else:
            unit = "m³"
        return unit

    def get_status(self, stage):
        name = ""
        if stage == "booked":
            name = "Booked"
        elif stage == "refund":
            name = "Refund"
        elif stage == "sold":
            name = "Sold"
        return name

    def get_payment_term(self, term):
        name = ""
        if term == "monthly":
            name = "Monthly"
        elif term == "full_payment":
            name = "Full Payment"
        elif term == "quarterly":
            name = "Quarterly"
        return name

    def action_create_rent_contract_report(self, sheet, record, workbook):
        border_squre = xlwt.Borders()
        border_squre.top = xlwt.Borders.HAIR
        border_squre.left = xlwt.Borders.HAIR
        border_squre.right = xlwt.Borders.HAIR
        border_squre.bottom = xlwt.Borders.HAIR
        border_squre.top_colour = xlwt.Style.colour_map["gray50"]
        border_squre.bottom_colour = xlwt.Style.colour_map["gray50"]
        border_squre.right_colour = xlwt.Style.colour_map["gray50"]
        border_squre.left_colour = xlwt.Style.colour_map["gray50"]
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        al.vert = xlwt.Alignment.VERT_CENTER
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'mm/dd/yyyy'
        date_format.font.name = "Century Gothic"
        date_format.borders = border_squre
        date_format.alignment = al
        sheet.row(0).height = 1000
        sheet.row(1).height = 600
        sheet.col(0).width = 400
        sheet.col(1).width = 5000
        sheet.col(2).width = 6000
        sheet.col(3).width = 6000
        sheet.col(4).width = 3500
        sheet.col(5).width = 3500
        sheet.col(6).width = 3000
        sheet.col(7).width = 3500
        sheet.col(8).width = 5000
        sheet.col(9).width = 5000
        sheet.col(10).width = 6000
        sheet.col(11).width = 5555
        sheet.col(12).width = 5000
        sheet.col(13).width = 5500
        sheet.col(14).width = 5500
        sheet.col(15).width = 5000
        sheet.col(16).width = 5500
        # sheet.col(17).width = 4000
        # sheet.col(18).width = 5000
        # sheet.col(19).width = 3000
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)
        sheet.set_horz_split_pos(2)
        sheet.set_vert_split_pos(1)
        sheet.show_grid = False
        xlwt.add_palette_colour("custom_red", 0x21)
        workbook.set_colour_RGB(0x21, 240, 210, 211)
        xlwt.add_palette_colour("custom_green", 0x22)
        workbook.set_colour_RGB(0x22, 210, 241, 214)
        title = xlwt.easyxf(
            "font: height 440, name Century Gothic, bold on, color_index blue_gray;"
            " align: vert center, horz center;"
            "border: bottom thick, bottom_color sea_green;")
        sub_title = xlwt.easyxf(
            "font: height 185, name Century Gothic, bold on, color_index gray80; "
            "align: vert center, horz center; "
            "border: top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        border_all_right = xlwt.easyxf(
            "align:horz right, vert center;"
            "font:name Century Gothic;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        border_all_center = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:name Century Gothic;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        running_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:name Century Gothic, color_index sea_green, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        cancel_close_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:bold on, name Century Gothic, color_index dark_red;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        draft_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:name Century Gothic, color_index dark_blue, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        total_paid_text = xlwt.easyxf(
            "pattern: pattern solid, fore_colour custom_green;"
            "align:horz right, vert center;"
            "font:name Century Gothic, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        total_remaining_text = xlwt.easyxf(
            "pattern: pattern solid, fore_colour custom_red;"
            "align:horz right, vert center;"
            "font:name Century Gothic, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        expire_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:name Century Gothic, color_index olive_ega, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")

        sheet.write_merge(0, 0, 1, 17, "RENT CONTRACT DETAILS", title)
        sheet.write(1, 1, "Reference", sub_title)
        sheet.write(1, 2, "Property", sub_title)
        sheet.write(1, 3, "Property Type", sub_title)
        sheet.write(1, 4, "Customer", sub_title)
        sheet.write(1, 5, "Landlord", sub_title)
        sheet.write(1, 6, "Broker", sub_title)
        sheet.write(1, 7, "Total Area", sub_title)
        sheet.write(1, 8, "Start Date", sub_title)
        sheet.write(1, 9, "End Date", sub_title)
        sheet.write(1, 10, "Payment Term", sub_title)
        sheet.write(1, 11, "Rent", sub_title)
        sheet.write(1, 12, "Security Deposit", sub_title)
        sheet.write(1, 13, "Broker Commission", sub_title)
        sheet.write(1, 14, "Total Amount", sub_title)
        sheet.write(1, 15, "Paid Amount", sub_title)
        sheet.write(1, 16, "Remaining Amount", sub_title)
        sheet.write(1, 17, "Status", sub_title)

        row = 2
        col = 1
        main_total_payable = 0.0
        main_total_remaining = 0.0

        for rec in record:
            main_total_payable += rec.paid_tenancy
            main_total_remaining += rec.remain_tenancy
            type = self.get_property_type(rec.property_type)
            unit = self.get_measure_unit(rec.measure_unit)
            stage = self.get_rent_stage(rec.contract_type)
            term = self.get_payment_term(rec.payment_term)
            sheet.row(row).height = 400
            sheet.write(row, col, rec.tenancy_seq, border_all_center)
            sheet.write(row, col + 1, rec.property_id.name, border_all_center)
            sheet.write(
                row, col + 2, f"{type} / {rec.property_subtype_id.name}", border_all_center)
            sheet.write(row, col + 3, rec.tenancy_id.name, border_all_center)
            sheet.write(row, col + 4, rec.property_landlord_id.name,
                        border_all_center)
            if rec.broker_id:
                sheet.write(row, col + 5, rec.broker_id.name,
                            border_all_center)
            else:
                sheet.write(row, col + 5, " ", border_all_center)
            sheet.write(
                row, col + 6, f"{rec.total_area} {unit}", border_all_right)
            sheet.write(row, col + 7, rec.start_date, date_format)
            sheet.write(row, col + 8, rec.end_date, date_format)
            sheet.write(row, col + 9, term, border_all_center)
            sheet.write(row, col + 10, f"{rec.total_rent} {self.env.company.currency_id.symbol} / {rec.rent_unit}",
                        border_all_center)
            sheet.write(
                row, col + 11, f"{rec.deposit_amount} {self.env.company.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 12, f"{rec.commission} {self.env.company.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 13, f"{rec.total_amount} {self.env.company.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 14, f"{rec.paid_tenancy} {self.env.company.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 15, f"{rec.remain_tenancy} {self.env.company.currency_id.symbol}", border_all_right)
            if rec.contract_type == "new_contract":
                sheet.write(row, col + 16, stage, draft_text)
            elif rec.contract_type == "running_contract":
                sheet.write(row, col + 16, stage, running_text)
            elif rec.contract_type in ["cancel_contract", "close_contract"]:
                sheet.write(row, col + 16, stage, cancel_close_text)
            elif rec.contract_type == "expire_contract":
                sheet.write(row, col + 16, stage, expire_text)

            row += 1
        sheet.row(row).height = 400
        sheet.write(row, 14, "Totals", sub_title)
        sheet.write(
            row, 15, f"{main_total_payable} {self.env.company.currency_id.symbol}", total_paid_text)
        sheet.write(
            row, 16, f"{main_total_remaining} {self.env.company.currency_id.symbol}", total_remaining_text)

    def action_create_sold_report(self, sheet, record, workbook):
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)
        sheet.set_horz_split_pos(2)
        sheet.set_vert_split_pos(1)
        sheet.show_grid = False
        sheet.row(0).height = 1000
        sheet.row(1).height = 600
        sheet.col(0).width = 400
        sheet.col(1).width = 5000
        sheet.col(2).width = 6000
        sheet.col(3).width = 6000
        sheet.col(4).width = 3500
        sheet.col(5).width = 3500
        sheet.col(6).width = 3000
        sheet.col(7).width = 3500
        sheet.col(8).width = 5000
        sheet.col(9).width = 4000
        sheet.col(10).width = 6000
        sheet.col(11).width = 5000
        sheet.col(12).width = 5000
        sheet.col(13).width = 5500
        sheet.col(14).width = 4000
        sheet.col(15).width = 5000
        sheet.col(16).width = 5000
        sheet.col(17).width = 4000
        sheet.col(18).width = 5000
        sheet.col(19).width = 3000
        xlwt.add_palette_colour("custom_red", 0x21)
        workbook.set_colour_RGB(0x21, 240, 210, 211)
        xlwt.add_palette_colour("custom_green", 0x22)
        workbook.set_colour_RGB(0x22, 210, 241, 214)
        title = xlwt.easyxf(
            "font: height 440, name Century Gothic, bold on, color_index blue_gray; "
            "align: vert center, horz center;"
            "border: bottom thick, bottom_color sea_green;")
        sub_title = xlwt.easyxf(
            "font: height 185, name Century Gothic, bold on, color_index gray80; "
            "align: vert center, horz center; "
            "border: top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        border_all_right = xlwt.easyxf(
            "align:horz right, vert center;"
            "font:name Century Gothic;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        border_all_center = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:name Century Gothic;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        sold_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:bold on,name Century Gothic, color_index sea_green;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        refund_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:bold on,name Century Gothic, color_index dark_red;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        booked_text = xlwt.easyxf(
            "align:horz center, vert center;"
            "font:bold on,name Century Gothic, color_index dark_blue;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        total_paid_text = xlwt.easyxf(
            "pattern: pattern solid, fore_colour custom_green;"
            "align:horz right, vert center;"
            "font:name Century Gothic, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        total_remaining_text = xlwt.easyxf(
            "pattern: pattern solid, fore_colour custom_red;"
            "align:horz right, vert center;"
            "font:name Century Gothic, bold on;"
            "border:  top hair, bottom hair, left hair, right hair, "
            "top_color gray50, bottom_color gray50, left_color gray50, right_color gray50")
        sheet.write_merge(0, 0, 1, 19, "PROPERTY SELL INFORMATION", title)
        sheet.write(1, 1, "Reference", sub_title)
        sheet.write(1, 2, "Property", sub_title)
        sheet.write(1, 3, "Property Type", sub_title)
        sheet.write(1, 4, "Total Area", sub_title)
        sheet.write(1, 5, "Customer", sub_title)
        sheet.write(1, 6, "Landlord", sub_title)
        sheet.write(1, 7, "Broker", sub_title)
        sheet.write(1, 8, "Broker Commission", sub_title)
        sheet.write(1, 9, "Selling Price", sub_title)
        sheet.write(1, 10, "Customer Ask Price", sub_title)
        sheet.write(1, 11, "Confirm Sell Price", sub_title)
        sheet.write(1, 12, "Book Price", sub_title)
        sheet.write(1, 13, "Total Maintenance", sub_title)
        sheet.write(1, 14, "Utilities Cost", sub_title)
        sheet.write(1, 15, "Payable Amount", sub_title)
        sheet.write(1, 16, "Payment Term", sub_title)
        sheet.write(1, 17, "Paid Amount", sub_title)
        sheet.write(1, 18, "Remaining Amount", sub_title)
        sheet.write(1, 19, "Status", sub_title)
        row = 2
        col = 1
        main_total_payable = 0.0
        main_total_remaining = 0.0
        for rec in record:
            type = self.get_property_type(rec.type)
            unit = self.get_measure_unit(rec.measure_unit)
            stage = self.get_status(rec.stage)
            term = self.get_payment_term(rec.payment_term)
            main_total_payable += rec.paid_amount
            main_total_remaining += rec.remaining_amount
            sheet.row(row).height = 400
            sheet.write(row, col, rec.sold_seq, border_all_center)
            sheet.write(row, col + 1, rec.property_id.name, border_all_center)
            sheet.write(
                row, col + 2, f"{type} / {rec.property_subtype_id.name}", border_all_center)
            sheet.write(
                row, col + 3, f"{rec.total_area} {unit}", border_all_right)
            sheet.write(row, col + 4, rec.customer_id.name, border_all_center)
            sheet.write(row, col + 5, rec.landlord_id.name, border_all_center)
            if rec.is_any_broker:
                sheet.write(row, col + 6, rec.broker_id.name,
                            border_all_center)
            else:
                sheet.write(row, col + 6, " - ", border_all_center)
            sheet.write(
                row, col + 7, f"{rec.broker_final_commission} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 8, f"{rec.price} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 9, f"{rec.ask_price} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 10, f"{rec.sale_price} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 11, f"{rec.book_price} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 12, f"{rec.total_maintenance} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 13, f"{rec.total_service} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 14, f"{rec.payable_amount} {rec.currency_id.symbol}", border_all_right)
            sheet.write(row, col + 15, term, border_all_center)
            sheet.write(
                row, col + 16, f"{rec.paid_amount} {rec.currency_id.symbol}", border_all_right)
            sheet.write(
                row, col + 17, f"{rec.remaining_amount} {rec.currency_id.symbol}", border_all_right)
            if rec.stage == "booked":
                sheet.write(row, col + 18, stage, booked_text)
            elif rec.stage == "sold":
                sheet.write(row, col + 18, stage, sold_text)
            elif rec.stage == "refund":
                sheet.write(row, col + 18, stage, refund_text)
            row += 1
            sheet.row(row).height = 400
            sheet.write(row, 16, "Totals", sub_title)
            sheet.write(
                row, 17, f"{main_total_payable} {self.env.company.currency_id.symbol}", total_paid_text)
            sheet.write(
                row, 18, f"{main_total_remaining} {self.env.company.currency_id.symbol}", total_remaining_text)

    # def action_property_xls_report(self):
        if self.type == "tenancy":
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet(
                'Rent Contract Details', cell_overwrite_ok=True)
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'mm/dd/yyyy'
            sheet1.col(0).width = 7000
            sheet1.write(0, 0, 'Contract Ref.')
            sheet1.write(0, 1, 'Tenant')
            sheet1.write(0, 2, 'Property')
            sheet1.write(0, 3, 'Landlord')
            sheet1.write(0, 4, 'Total Invoiced')
            c = 1

            for group in self.env['account.move'].read_group(
                    [('tenancy_id', '!=', False), ('payment_state', '=', 'paid'),
                     ('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date)],
                    ['tenancy_id', 'amount_total'],
                    ['tenancy_id'], orderby="amount_total DESC"):
                if group['tenancy_id']:
                    active_id = self.env['tenancy.details'].sudo().browse(
                        int(group['tenancy_id'][0]))
                    sheet1.col(c).width = 7000
                    sheet1.write(c, 0, active_id.tenancy_seq)
                    sheet1.write(c, 1, active_id.tenancy_id.name)
                    sheet1.write(c, 2, active_id.property_id.name)
                    sheet1.write(c, 3, active_id.property_landlord_id.name)
                    sheet1.write(c, 4, group['amount_total'])
                    c += 1

            stream = BytesIO()
            workbook.save(stream)
            out = base64.encodebytes(stream.getvalue())

            attachment = self.env['ir.attachment'].sudo()
            filename = 'Rent Details' + ".xls"
            attachment_id = attachment.create(
                {'name': filename,
                 'type': 'binary',
                 'public': False,
                 'datas': out})
            if attachment_id:
                report = {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/%s?download=true' % (attachment_id.id),
                    'target': 'self',
                }
                return report

        elif self.type == "sold":
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet1 = workbook.add_sheet(
                'Property Sold Information', cell_overwrite_ok=True)
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'mm/dd/yyyy'
            sheet1.col(0).width = 7000
            sheet1.write(0, 0, 'Sequence')
            sheet1.write(0, 1, 'Customer')
            sheet1.write(0, 2, 'Property')
            sheet1.write(0, 3, 'Landlord')
            sheet1.write(0, 4, 'Total Invoiced')
            c = 1

            for group in self.env['account.move'].read_group(
                    [('sold_id', '!=', False), ('payment_state', '=', 'paid'),
                     ('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date)],
                    ['sold_id', 'amount_total'],
                    ['sold_id'], orderby="amount_total DESC"):
                if group['sold_id']:
                    active_id = self.env['property.vendor'].sudo().browse(
                        int(group['sold_id'][0]))
                    sheet1.col(c).width = 7000
                    sheet1.write(c, 0, active_id.sold_seq)
                    sheet1.write(c, 1, active_id.customer_id.name)
                    sheet1.write(c, 2, active_id.property_id.name)
                    sheet1.write(c, 3, active_id.property_id.landlord_id.name)
                    sheet1.write(c, 4, group['amount_total'])
                    c += 1

            stream = BytesIO()
            workbook.save(stream)
            out = base64.encodebytes(stream.getvalue())

            attachment = self.env['ir.attachment'].sudo()
            filename = 'Sold Information' + ".xls"
            attachment_id = attachment.create(
                {'name': filename,
                 'type': 'binary',
                 'public': False,
                 'datas': out})
            if attachment_id:
                report = {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/%s?download=true' % (attachment_id.id),
                    'target': 'self',
                }
                return report
