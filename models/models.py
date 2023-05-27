# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import random
import string
from datetime import datetime, date
import random
import string


class FileUpload(models.Model):
    _name = 'm2st_hk_roadshipping.roadshipping_file_upload'
    _description = 'File Upload'

    cni_doc = fields.Binary(string='National identity card or Passport')
    cni_name = fields.Char(string='cni name')
    travel_id = fields.Many2one('m2st_hk_roadshipping.roadshipping')


class RoadShipping(models.Model):
    _name = 'm2st_hk_roadshipping.roadshipping'
    _description = 'Management of road shipments'

    user_partner_id = fields.Many2one('res.partner')
    travel_type = fields.Char(string='Travel type', default='road')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ], string='Status', default='pending')
    disable = fields.Boolean(string='Travel disable', compute='_compute_disable', store=True, default=False,
                             readonly=False)
    departure_town = fields.Char(string='Departure town', required=True)
    arrival_town = fields.Char(string='Arrival town', required=True)
    departure_date = fields.Date(string='Departure date', required=True)
    arrival_date = fields.Date(string='Arrival date', required=True)
    position = fields.Text(string='Position')
    type_of_luggage_accepted = fields.Text(string='Type of luggage accepted')
    files_uploaded_id = fields.One2many('m2st_hk_roadshipping.roadshipping_file_upload', 'travel_id')


class TravelBooking(models.Model):
    _name = 'm2st_hk_roadshipping.travel_booking'
    _description = 'Booking of travels'

    sender_id = fields.Many2one('res.partner')
    travel_id = fields.Many2one('m2st_hk_roadshipping.roadshipping', required=True)
    message_ids = fields.One2many('m2st_hk_roadshipping.message', 'travel_booking_id', string='Messages')
    receiver_partner_id = fields.Many2one('res.partner', string='Receiver')
    receiver_name = fields.Char(string='Receiver Name')
    receiver_email = fields.Char(string='Receiver Email')
    receiver_phone = fields.Char(string='Receiver Phone')
    receiver_address = fields.Text(string='Receiver Address')
    type_of_luggage = fields.Text(string='Type of luggage you want to send', required=True)
    luggage_image1 = fields.Binary(string='Luggage images1')
    luggage_image2 = fields.Binary(string='Luggage images2')
    luggage_image3 = fields.Binary(string='Luggage images3')
    luggage_width = fields.Float(string='Luggage width', required=True)
    luggage_height = fields.Float(string='Luggage height', required=True)
    luggage_dimension = fields.Float(string='Luggage dimension', readonly=True)
    booking_price = fields.Float(string='Booked price', default=0)
    luggage_weight = fields.Float(string='Luggage Weight', required=True)
    disable = fields.Boolean(string='Disable Booking', default=False)
    code = fields.Char(string='Booking code', readonly=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed')
    ], string='Status', default='pending')

    @api.onchange('luggage_width', 'luggage_height')
    def _onchange_dimension(self):
        if self.luggage_width and self.luggage_height:
            self.luggage_dimension = self.luggage_width * self.luggage_height

    @api.onchange('receiver_partner_id')
    def _onchange_receiver_partner_id(self):
        if self.receiver_partner_id:
            self.receiver_name = self.receiver_partner_id.name
            self.receiver_email = self.receiver_partner_id.email
            self.receiver_phone = self.receiver_partner_id.phone or ''
            self.receiver_address = self.receiver_partner_id.street or ''

    @api.onchange('receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address')
    def _onchange_receiver_info(self):
        if self.receiver_partner_id:
            self.receiver_partner_id = False

    @api.constrains('receiver_partner_id', 'receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address')
    def _check_receiver_info(self):
        for booking in self:
            if not booking.receiver_partner_id and not (
                    booking.receiver_name and booking.receiver_email and booking.receiver_phone):
                raise exceptions.ValidationError("Receiver information is incomplete.")


class Message(models.Model):
    _name = 'm2st_hk_roadshipping.message'
    _description = 'Messaging Model'

    travel_booking_id = fields.Many2one('m2st_hk_roadshipping.travel_booking', string='Travel Booked', required=True)
    sender_id = fields.Many2one('res.partner', string='Sender', required=True)
    receiver_id = fields.Many2one('res.partner', string='Receiver', required=True)
    message = fields.Float(string='Message(Price)', required=True)
    date = fields.Datetime(string='Date')

    # def send_message(self, sender_id, receiver_id, message, travel_booking_id):
    #     # Create a new message record
    #     new_message = self.sudo().create({
    #         'sender_id': sender_id,
    #         'receiver_id': receiver_id,
    #         'message': message,
    #         'travel_booking_id': travel_booking_id,
    #     })
    #     return new_message
    #
    # def get_messages(self, travel_booking_id):
    #     # Retrieve messages for a specific travel booking
    #     messages = self.sudo().search([('travel_booking_id', '=', travel_booking_id)])
    #     return messages


class ResUsers(models.Model):
    _inherit = 'res.partner'

    roadshipping_ids = fields.One2many('m2st_hk_roadshipping.roadshipping', 'user_partner_id')
    booking_ids = fields.One2many('m2st_hk_roadshipping.travel_booking', 'sender_id')
    # image_1920 = fields.Binary(string='Image', attachment=True)


class m2st_hk_airshipping(models.Model):
    _inherit = 'm2st_hk_airshipping.airshipping'
