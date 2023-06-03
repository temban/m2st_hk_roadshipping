import json

from odoo import http, fields
from odoo.http import request
import json


class MessageController(http.Controller):

    @http.route('/road/send_message', type='json', auth='user', website=True,
                csrf=False, methods=['POST'], cors='*')
    def send_message(self, travel_booking_id, receiver_id, message):
        date = fields.Datetime.now()

        message = request.env['m2st_hk_roadshipping.message'].sudo().create({
            'travel_booking_id': travel_booking_id,
            'sender_id': http.request.env.user.partner_id.id,
            'receiver_id': receiver_id,
            'message': message,
            'date': date
        })

        return {'status': 200, 'message_id': message.id, 'message': 'success'}

    @http.route('/road/message_history/<int:travel_booking_id>', type='http', auth='user', website=True,
                csrf=False, methods=['GET'], cors='*')
    def message_history(self, travel_booking_id):
        travel_booking = request.env['m2st_hk_roadshipping.travel_booking'].sudo().browse(travel_booking_id)
        messages = travel_booking.message_ids.sorted('date')

        message_history = []
        for message in messages:
            message_data = {
                'msg_id': message.id,
                'sender_id': message.sender_id.id,
                'receiver_id': message.receiver_id.id,
                'message': message.message,
                'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                'travel_booking': {
                    'id': message.travel_booking_id.id,
                    'luggage_weight': message.travel_booking_id.luggage_weight,
                    'luggage_width': message.travel_booking_id.luggage_width,
                    'luggage_height': message.travel_booking_id.luggage_height,
                    'luggage_dimension': message.travel_booking_id.luggage_dimension,
                    'booking_price': message.travel_booking_id.booking_price,
                    'status': message.travel_booking_id.status,
                    'disable': message.travel_booking_id.disable,
                    'type_of_luggage': message.travel_booking_id.type_of_luggage,
                    'sender': {
                        'sender_id': message.travel_booking_id.sender_id.id,
                        'sender_name': message.travel_booking_id.sender_id.name,
                        'sender_email': message.travel_booking_id.sender_id.email,
                        'sender_phone': message.travel_booking_id.sender_id.phone,
                    },
                    'receiver': {
                        'receiver_partner_id': message.travel_booking_id.receiver_partner_id.id,
                        'receiver_name': message.travel_booking_id.receiver_name,
                        'receiver_email': message.travel_booking_id.receiver_email,
                        'receiver_phone': message.travel_booking_id.receiver_phone,
                        'receiver_address': message.travel_booking_id.receiver_address,
                    },
                    'travel': {
                        'id': message.travel_booking_id.travel_id.id,
                        'travel_type': message.travel_booking_id.travel_id.travel_type,
                        'departure_town': message.travel_booking_id.travel_id.departure_town,
                        'arrival_town': message.travel_booking_id.travel_id.arrival_town,
                        'status': message.travel_booking_id.travel_id.status,
                        'disable': message.travel_booking_id.travel_id.disable,
                        'departure_date': message.travel_booking_id.travel_id.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': message.travel_booking_id.travel_id.arrival_date.strftime('%Y-%m-%d'),
                        'type_of_luggage_accepted': message.travel_booking_id.travel_id.type_of_luggage_accepted,
                        'files_uploaded_id': message.travel_booking_id.travel_id.files_uploaded_id.id,
                        'traveler': {
                            'user_id': message.travel_booking_id.travel_id.user_partner_id.id,
                            'user_name': message.travel_booking_id.travel_id.user_partner_id.name,
                            'user_email': message.travel_booking_id.travel_id.user_partner_id.email,
                            'image_1920': message.travel_booking_id.travel_id.user_partner_id.image_1920.decode(
                                'utf-8') if message.travel_booking_id.travel_id.user_partner_id.image_1920 else None
                        }
                    }
                }
            }
            message_history.append(message_data)

        return json.dumps({'status': 200, 'response': message_history, 'message': 'success'})

    # @http.route('/road/update_message_status/<int:message_id>', type='json', auth='user', website=True,
    #             csrf=False, methods=['PUT'], cors='*')
    # def update_message_status(self, message_id, status):
    #     message = request.env['m2st_hk_roadshipping.message'].browse(message_id)
    #     message.write({'status': status})
    #
    #     return {'success': True}
