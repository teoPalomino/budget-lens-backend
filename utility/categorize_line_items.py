from veryfi import Client
import json
from item.models import Item
from category.models import Category

client_id = 'vrfSF8foCT17EJT3UgcSLY3YUbztTJOCnbA6wXM'
client_secret = 'S07fCdCCPIUa2wrCapt3COCaWIFsItrevAnVzTnglaxXI8EO7F1FvEcVy0riH8zZ3U2YkkVy21hKo6wgIu0zuNKWH0jSemV0bhXTiztNGUMrwnRuoPGK3WTdKkswyJEf'
username = 'amir4'
api_key = 'fcff4aa0b6f33e7826e467319d76985b'
def categorize_line_items(receipt):
    if os.getenv('APP_ENV') != 'test':
        # This submits document for processing (takes 3-5 seconds to get response)
        veryfi_client = Client(client_id, client_secret, username, api_key)
        response = veryfi_client.process_document(receipt.receipt_image.path)

        for x in response['line_items']:
            item = Item.objects.filter(receipt_id=receipt.id, name=x['description'])
            category = Category.objects.get(user_id=receipt.user.id, category_name=x['type'])
            other = Category.objects.get(user_id=receipt.user.id, category_name='Other')
            for i in item:
                if x['type'] is not '':
                    i.category_id = category
                else:
                    i.category_id = other
                i.save()

