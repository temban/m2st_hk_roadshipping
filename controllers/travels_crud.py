from odoo import http, fields
from odoo.http import request
import json
import base64
from datetime import datetime, timedelta

from datetime import date
from odoo import http
from werkzeug.wrappers import Response


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class TravelFiles(http.Controller):

    # Controller that uploads and update travel documents
    @http.route('/road/travel/document/upload', type='http', auth='user', website=True, csrf=False, methods=['POST'],
                cors='*')
    def create_file_upload(self, **kwargs):

        check_doc = request.env['m2st_hk_roadshipping.roadshipping_file_upload'].sudo().search(
            [('travel_id', '=', int(kwargs.get('travel_id')))])
        cni_doc_data = kwargs['cni_doc'].read()
        cni_doc_name = kwargs['cni_doc']
        cni_doc_base64 = base64.b64encode(cni_doc_data).decode('utf-8') if cni_doc_data else False

        values = {
            'cni_doc': cni_doc_base64,
            'cni_name': cni_doc_name.filename,
            'travel_id': kwargs.get('travel_id')
        }
        print(kwargs.get('travel_id'))
        print(check_doc)
        if check_doc:
            return json.dumps({'Error': 'Travel documents already exist!'})
        else:
            # Read the file data and convert to base64
            new_file_upload = request.env['m2st_hk_roadshipping.roadshipping_file_upload'].sudo().create(values)
            return json.dumps({'status': 200, 'file_upload_id': new_file_upload.id, 'message': 'success'})
        # return json.dumps({'file_upload_id': new_file_upload.cni_doc.decode('utf-8')})

    @http.route('/road/update/travel/document/upload/<int:file_upload_id>', type='http', auth='user', website=True,
                csrf=False, methods=['POST'], cors='*')
    def road_update_file_upload(self, file_upload_id, **kwargs):
        file_upload = request.env['m2st_hk_roadshipping.roadshipping_file_upload'].sudo().browse(file_upload_id)
        # Read the file data and convert to base64
        cni_doc_data = kwargs['cni_doc'].read()
        cni_doc_name = kwargs['cni_doc']
        cni_doc_base64 = base64.b64encode(cni_doc_data).decode('utf-8') if cni_doc_data else False

        values = {
            'cni_doc': cni_doc_base64,
            'cni_name': cni_doc_name.filename,
        }
        updated_file_upload = file_upload.write(values)
        return json.dumps({'status': 200, 'message': 'success'})


class TravelCrud(http.Controller):
    # function that disable due travels
    def road_update_due_travels_disable(self):
        due_travels = http.request.env['m2st_hk_roadshipping.roadshipping'].sudo().search([])
        if due_travels:
            for due_travel in due_travels:
                current_date = datetime.now().date()
                if due_travel.departure_date and (due_travel.departure_date - timedelta(days=1)) <= current_date:
                    due_travel.disable = True
                    print("due_departure_date", (due_travel.departure_date - timedelta(days=1)), '<=', "previous_date",
                          current_date, 'sattus', due_travel.disable)
                else:
                    'still valid'

    # Controller that creates a new travel
    @http.route('/road/api/travel/create', type='json', auth='user', website=True, csrf=False, methods=['POST'],
                cors='*')
    def road_travel_create(self, **kwargs):
        travel = {
            'user_partner_id': http.request.env.user.partner_id.id,
            'departure_town': kwargs.get('departure_town').lower(),
            'arrival_town': kwargs.get('arrival_town').lower(),
            'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
            'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
            'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted'),
        }
        travel_info = request.env['m2st_hk_roadshipping.roadshipping'].sudo().create(travel)
        if travel_info:
            return {'status': 'success',
                    'travel': {
                        'id': travel_info.id,
                        'user_partner_id': http.request.env.user.partner_id.id,
                        'travel_type': travel_info.travel_type,
                        'departure_town': travel_info.departure_town,
                        'arrival_town': travel_info.arrival_town,
                        'status': travel_info.status,
                        'departure_date': travel_info.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': travel_info.arrival_date.strftime('%Y-%m-%d'),
                        'type_of_luggage_accepted': travel_info.type_of_luggage_accepted,
                    }}
        else:
            return "Request failed!"

    @http.route('/api/all/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def all_travels(self, **kwargs):
        road_shippings = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])
        air_shippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])

        # *****************first procedure read directly************************************************
        # Prepare the data as a dictionary
        # data = {
        #     'road_shippings': road_shippings.read(),
        #     'air_shippings': air_shippings.read(),
        # }

        # *****************Secnd procedure read fields*****************************************************
        # # Select specific fields to include in the response
        # road_shipping_fields = ['departure_town', 'arrival_town', 'departure_date', 'arrival_date', 'travel_type', 'user_partner_id.id', 'user_partner_id.name', 'user_partner_id.email']
        # air_shipping_fields = ['departure_town', 'arrival_town', 'departure_date', 'arrival_date', 'kilo_qty']
        #
        # # Prepare the data as a dictionary
        # data = {
        #     'road_shippings': road_shippings.read(road_shipping_fields),
        #     'air_shippings': air_shippings.read(air_shipping_fields),
        # }

        # ********************Third procedure read with relations**********************************************
        # Select specific fields to include in the response
        # road_shipping_fields = ['user_partner_id', 'departure_town', 'arrival_town', 'departure_date', 'arrival_date']
        # air_shipping_fields = ['user_partner_id', 'departure_town', 'arrival_town', 'departure_date', 'arrival_date',
        #                        'kilo_qty']
        # # Prepare the data as a dictionary
        # road_shippings_data = road_shippings.read(road_shipping_fields)
        # air_shippings_data = air_shippings.read(air_shipping_fields)
        #
        # # Include user_partner_id's ID in the data
        # for road_shipping in road_shippings_data:
        #     road_shipping['user_partner_id'] = road_shipping['user_partner_id'][0]
        #
        # for air_shipping in air_shippings_data:
        #     air_shipping['user_partner_id'] = air_shipping['user_partner_id'][0]
        #
        # data = {
        #     'road_shippings': road_shippings_data,
        #     'air_shippings': air_shippings_data,
        # }

        # **********************last option ********************************************************************
        # Prepare the data as a dictionary
        road_shippings_data = []
        air_shippings_data = []

        # Iterate over road_shippings and create sender field structure
        for road_shipping in road_shippings:
            sender = {
                'sender_id': road_shipping.user_partner_id.id,
                'sender_name': road_shipping.user_partner_id.name,
                'sender_email': road_shipping.user_partner_id.email,
                'sender_phone': road_shipping.user_partner_id.phone,
            }
            road_shippings_data.append({
                'id': road_shipping.id,
                'travel_type': road_shipping.travel_type,
                'departure_town': road_shipping.departure_town,
                'arrival_town': road_shipping.arrival_town,
                'departure_date': str(road_shipping.departure_date),
                'arrival_date': str(road_shipping.arrival_date),
                'position': road_shipping.position,
                'type_of_luggage_accepted': road_shipping.type_of_luggage_accepted,
                'sender': sender,
            })

        # Iterate over air_shippings and create sender field structure
        for air_shipping in air_shippings:
            sender = {
                'sender_id': air_shipping.user_partner_id.id,
                'sender_name': air_shipping.user_partner_id.name,
                'sender_email': air_shipping.user_partner_id.email,
                'sender_phone': air_shipping.user_partner_id.phone,
            }
            air_shippings_data.append({
                'id': air_shipping.id,
                'travel_type': air_shipping.travel_type,
                'departure_town': air_shipping.departure_town,
                'arrival_town': air_shipping.arrival_town,
                'departure_date': str(air_shipping.departure_date),
                'arrival_date': str(air_shipping.arrival_date),
                'kilo_qty': air_shipping.kilo_qty,
                'price_per_kilo': air_shipping.price_per_kilo,
                'type_of_luggage_accepted': air_shipping.type_of_luggage_accepted,
                'sender': sender,
            })

        data = {
            'road_shippings': road_shippings_data,
            'air_shippings': air_shippings_data,
        }

        # Serialize the data to JSON
        json_data = json.dumps(data, cls=DateEncoder)

        # Set the response content type as JSON

        return json_data

    @http.route('/all/travels/search', type='json', auth='public', csrf=False, website=True, methods=['POST'], cors='*')
    def all_travel_search(self, **kw):
        print(kw)
        departure_town = kw.get('departure_town')
        arrival_town = kw.get('arrival_town')
        travel_type = kw.get('travel_type')
        print(kw)
        road_shippings = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search([
            ('travel_type', '=', travel_type),
            ('departure_town', '=', departure_town),
            ('arrival_town', '=', arrival_town),
            ('status', '=', 'accepted'),
            ('disable', '=', False)
        ])
        air_shippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search([
            ('travel_type', '=', travel_type),
            ('departure_town', '=', departure_town),
            ('arrival_town', '=', arrival_town),
            ('status', '=', 'accepted'),
            ('disable', '=', False)
        ])
        # Prepare the data as a dictionary
        road_shippings_data = []
        shippings = []
        # Iterate over road_shippings and create sender field structure
        for road_shipping in road_shippings:
            sender = {
                'sender_id': road_shipping.user_partner_id.id,
                'sender_name': road_shipping.user_partner_id.name,
                'sender_email': road_shipping.user_partner_id.email,
                'sender_phone': road_shipping.user_partner_id.phone,
            }
            shippings.append({
                'id': road_shipping.id,
                'travel_type': road_shipping.travel_type,
                'departure_town': road_shipping.departure_town,
                'arrival_town': road_shipping.arrival_town,
                'departure_date': str(road_shipping.departure_date),
                'arrival_date': str(road_shipping.arrival_date),
                'position': road_shipping.position,
                'type_of_luggage_accepted': road_shipping.type_of_luggage_accepted,
                'sender': sender
            })

        # Iterate over air_shippings and create sender field structure
        for air_shipping in air_shippings:
            sender = {
                'sender_id': air_shipping.user_partner_id.id,
                'sender_name': air_shipping.user_partner_id.name,
                'sender_email': air_shipping.user_partner_id.email,
                'sender_phone': air_shipping.user_partner_id.phone,
            }
            shippings.append({
                'id': air_shipping.id,
                'travel_type': air_shipping.travel_type,
                'departure_town': air_shipping.departure_town,
                'arrival_town': air_shipping.arrival_town,
                'departure_date': str(air_shipping.departure_date),
                'arrival_date': str(air_shipping.arrival_date),
                'kilo_qty': air_shipping.kilo_qty,
                'price_per_kilo': air_shipping.price_per_kilo,
                'type_of_luggage_accepted': air_shipping.type_of_luggage_accepted,
                'sender': sender,
            })

        data = {
            'status': 200,
            'shippings': shippings,
            'message': 'success'
        }
        return data

    # Controller that gets all travels
    @http.route('/road/all/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def road_travels(self, **kwargs):
        self.road_update_due_travels_disable()
        travels = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])
        travels_list = []
        if travels:
            for travel in travels:
                files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
                travels_dict = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'position': travel.position,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode(
                            'utf-8') if travel.user_partner_id.image_1920 else None
                    }
                }
                travels_list.append(travels_dict)
                data = {'status': 200, 'response': travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that search travels by source and destination
    @http.route('/road/search/travel', type='json', auth='public', csrf=False, website=True, methods=['POST'], cors='*')
    def road_travel_search(self, **kw):
        print(kw)
        departure_town = kw.get('departure_town').lower()
        arrival_town = kw.get('arrival_town').lower()
        travel_type = kw.get('travel_type')
        print(kw)
        roadshippings = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('travel_type', '=', travel_type), ('departure_town', '=', departure_town),
             ('arrival_town', '=', arrival_town), ('status', '=', 'accepted'), ('disable', '=', False)])
        travels_search = []
        if roadshippings:
            for travel in roadshippings:
                files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
                travels_results = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'position': travel.position,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode(
                            'utf-8') if travel.user_partner_id.image_1920 else None
                    }
                }
                travels_search.append(travels_results)
            result = {'status': 200, 'response': travels_search, 'message': 'success'}
            return result
        else:
            return 'Empty!'

    # controller that gets a travel by id
    @http.route('/road/travel/view/<int:travel_id>', type='http', auth='user', csrf=False, website=True,
                methods=['GET'],
                cors='*')
    def view_road_travel(self, travel_id, **kw):
        self.road_update_due_travels_disable()
        travel = request.env['m2st_hk_roadshipping.roadshipping'].sudo().browse(travel_id)
        if travel:
            files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
            travel_result = {
                'id': travel.id,
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'status': travel.status,
                'disable': travel.disable,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'position': travel.position,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'files_uploaded_id': files_uploaded_id,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                    'image_1920': travel.user_partner_id.image_1920.decode(
                        'utf-8') if travel.user_partner_id.image_1920 else None
                }
            }
            result = {'status': 200, 'response': travel_result, 'message': 'success'}
            return json.dumps(result)
        else:
            return 'Not found!'

    # Controller that get all current user travels by partner id
    @http.route('/road/api/current/user/travels', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def current_user_road_travel_list(self, **kw):
        self.road_update_due_travels_disable()
        travels = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('user_partner_id', '=', http.request.env.user.partner_id.id), ('disable', '=', False)])
        user_travels_list = []

        if travels:
            for user_travel in travels:
                files_uploaded_id = user_travel.files_uploaded_id[0].id if user_travel.files_uploaded_id else None
                travels_dict = {
                    'id': user_travel.id,
                    'files_uploaded_id': files_uploaded_id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'disable': user_travel.disable,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'position': user_travel.position,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted
                }
                user_travels_list.append(travels_dict)

            data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
            return json.dumps(data)
        else:
            return 'Empty'

    # Controller that get all current user travels by partner id
    @http.route('/road/api/user/all/travels/<int:partner_id>', type='http', auth='user', csrf=False, website=True,
                methods=['GET'], cors='*')
    def user_road_travel_list(self, partner_id, **kw):
        self.road_update_due_travels_disable()
        travels = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('user_partner_id', '=', partner_id), ('disable', '=', False)])
        user_travels_list = []
        if travels:
            for user_travel in travels:
                files_uploaded_id = user_travel.files_uploaded_id[0].id if user_travel.files_uploaded_id else None
                travels_dict = {
                    'id': user_travel.id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'position': user_travel.position,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,
                    'user': {
                        'user_id': user_travel.user_partner_id.id,
                        'user_name': user_travel.user_partner_id.name,
                        'user_email': user_travel.user_partner_id.email,
                        'image_1920': user_travel.user_partner_id.image_1920.decode(
                            'utf-8') if user_travel.user_partner_id.image_1920 else None
                    }
                }
                user_travels_list.append(travels_dict)
                data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that delete a travel
    @http.route('/road/api/travel/delete/<int:roadshipping_id>', auth='user', csrf=False, website=True,
                methods=['DELETE'],
                cors='*')
    def delete_road_travel(self, roadshipping_id, **kw):
        travel = request.env['m2st_hk_roadshipping.roadshipping'].sudo().browse(roadshipping_id)
        if travel.status == 'accepted':
            error_response = {
                'success': False,
                'error_message': 'This travel has already been accepted!.'
            }
            return error_response
        if travel:
            print(travel)
            travel.sudo().write({
                'disable': True,
            })
            return json.dumps({'status': 200, 'message': 'deleted'})
        else:
            return 'Request Failed'

    @http.route('/road/travel/position/update/<int:travel_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def update_traveler_position(self, travel_id, **kw):
        position = kw.get('position')
        travel = request.env['m2st_hk_roadshipping.roadshipping'].sudo().browse(travel_id)
        if travel:
            travel.sudo().write({
                'position': position,
            })
            travel_position_updated = {'position': travel.position}
            # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.luggage_dimension)")
            return {'status': 200, 'data': travel_position_updated, 'message': 'Traveler position updated.'}
        else:
            return 'Request Failed'

    # Controller that update a travel by id
    @http.route('/road/travel/update/<int:travel_id>', type='json', auth='user', methods=['PUT'], website=True,
                csrf=False)
    def update_road_travel(self, travel_id, **kwargs):
        travel = request.env['m2st_hk_roadshipping.roadshipping'].sudo().browse(travel_id)
        print(travel.user_partner_id.id)
        print(http.request.env.user.partner_id.id)
        if travel.status == 'accepted':
            error_response = {
                'success': False,
                'error_message': 'This travel has already been accepted!.'
            }
            return error_response
        if travel.disable:
            error_response = {
                'success': False,
                'error_message': 'This travel does not exist!.'
            }
            return error_response
        if travel.user_partner_id.id == http.request.env.user.partner_id.id:
            travel.write({
                'departure_town': kwargs.get('departure_town'),
                'arrival_town': kwargs.get('arrival_town'),
                'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
                'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
                'status': 'pending',
                'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted')
            })
            travel_updated = {
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
            }
            data = {'status': 200, 'response': travel_updated, 'message': 'success'}
            return data
        else:
            return 'Something went wrong!'


    @http.route('/api/list/all/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def all_list_travels(self, **kwargs):
        road_shippings = request.env['m2st_hk_roadshipping.roadshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])
        air_shippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])

        # *****************first procedure read directly************************************************
        # Prepare the data as a dictionary
        # data = {
        #     'road_shippings': road_shippings.read(),
        #     'air_shippings': air_shippings.read(),
        # }

        # *****************Secnd procedure read fields*****************************************************
        # # Select specific fields to include in the response
        # road_shipping_fields = ['departure_town', 'arrival_town', 'departure_date', 'arrival_date', 'travel_type', 'user_partner_id.id', 'user_partner_id.name', 'user_partner_id.email']
        # air_shipping_fields = ['departure_town', 'arrival_town', 'departure_date', 'arrival_date', 'kilo_qty']
        #
        # # Prepare the data as a dictionary
        # data = {
        #     'road_shippings': road_shippings.read(road_shipping_fields),
        #     'air_shippings': air_shippings.read(air_shipping_fields),
        # }

        # ********************Third procedure read with relations**********************************************
        # Select specific fields to include in the response
        # road_shipping_fields = ['user_partner_id', 'departure_town', 'arrival_town', 'departure_date', 'arrival_date']
        # air_shipping_fields = ['user_partner_id', 'departure_town', 'arrival_town', 'departure_date', 'arrival_date',
        #                        'kilo_qty']
        # # Prepare the data as a dictionary
        # road_shippings_data = road_shippings.read(road_shipping_fields)
        # air_shippings_data = air_shippings.read(air_shipping_fields)
        #
        # # Include user_partner_id's ID in the data
        # for road_shipping in road_shippings_data:
        #     road_shipping['user_partner_id'] = road_shipping['user_partner_id'][0]
        #
        # for air_shipping in air_shippings_data:
        #     air_shipping['user_partner_id'] = air_shipping['user_partner_id'][0]
        #
        # data = {
        #     'road_shippings': road_shippings_data,
        #     'air_shippings': air_shippings_data,
        # }

        # **********************last option ********************************************************************
        # Prepare the data as a dictionary
        road_shippings_data = []
        shippings = []

        # Iterate over road_shippings and create sender field structure
        for road_shipping in road_shippings:
            sender = {
                'sender_id': road_shipping.user_partner_id.id,
                'sender_name': road_shipping.user_partner_id.name,
                'sender_email': road_shipping.user_partner_id.email,
                'sender_phone': road_shipping.user_partner_id.phone,
            }
            shippings.append({
                'id': road_shipping.id,
                'travel_type': road_shipping.travel_type,
                'departure_town': road_shipping.departure_town,
                'arrival_town': road_shipping.arrival_town,
                'departure_date': str(road_shipping.departure_date),
                'arrival_date': str(road_shipping.arrival_date),
                'position': road_shipping.position,
                'type_of_luggage_accepted': road_shipping.type_of_luggage_accepted,
                'sender': sender,
            })

        # Iterate over air_shippings and create sender field structure
        for air_shipping in air_shippings:
            sender = {
                'sender_id': air_shipping.user_partner_id.id,
                'sender_name': air_shipping.user_partner_id.name,
                'sender_email': air_shipping.user_partner_id.email,
                'sender_phone': air_shipping.user_partner_id.phone,
            }
            shippings.append({
                'id': air_shipping.id,
                'travel_type': air_shipping.travel_type,
                'departure_town': air_shipping.departure_town,
                'arrival_town': air_shipping.arrival_town,
                'departure_date': str(air_shipping.departure_date),
                'arrival_date': str(air_shipping.arrival_date),
                'kilo_qty': air_shipping.kilo_qty,
                'price_per_kilo': air_shipping.price_per_kilo,
                'type_of_luggage_accepted': air_shipping.type_of_luggage_accepted,
                'sender': sender,
            })

        data = {
            'shippings': shippings,
        }

        # Serialize the data to JSON
        json_data = json.dumps(data, cls=DateEncoder)

        # Set the response content type as JSON

        return json_data
