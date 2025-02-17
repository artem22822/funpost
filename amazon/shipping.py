from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json


class CreateShipping():
    @classmethod
    @csrf_exempt
    def post(cls, request):
        # if request.method == 'POST':
            enpoint = 'https://sandbox.sellingpartnerapi-eu.amazon.com/shipping/v2/oneClickShipment'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'apikey',
                'x-amzn-shipping-business': 'AMZN_US',
                'x-amz-access-token': '',
            }
            payload = {
                'shipTo': 'address',
                'shipFrom': 'address',  # equired
                'returnTo': 'address',
                'shipDate': 'string (date-time)',
                'packages': 'see to amazon documentation',  # equired
                'valueAddedServicesDetails': 'see to amazon documentation',
                'taxDetails': 'see to amazon documentation',
                'channelDetails': 'see to amazon documentation',  # equired
                'labelSpecifications': 'see to amazon documentation',  # equired
                'serviceSelection': 'see to amazon documentation',  # equired
                'shipperInstruction': 'see to amazon documentation',
                'destinationAccessPointDetails': 'see to amazon documentation',
            }

            try:
                r = requests.post(enpoint, data=json.dumps(payload), headers=headers)
                return HttpResponse('XX')
            except:
                return HttpResponse('Error creating shipment', status=500)


class TrackShipping():
    @classmethod
    @csrf_exempt
    def get(cls, request):
        if request.method == 'GET':
            enpoint = 'https://sandbox.sellingpartnerapi-eu.amazon.com/shipping/v2/tracking'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'apikey',
                'x-amzn-shipping-business': 'AMZN_US',
                'x-amz-access-token': '',
            }
            params = {
                'trackingId': '',  # required
                'carrierId': '',  # required

            }

            try:
                r = requests.get(enpoint, params=params, headers=headers)
            except:
                return 'Error'
