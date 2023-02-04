import os
import random

import requests
from django.core.management import BaseCommand
from faker import Faker

from apps.models import Product, Store, Category, ProductImage

fake = Faker()


class Command(BaseCommand):
    help = '''
        You can create dummy data. Like this:
    * Products      -> 1000
    * Categories    -> 15
    * Store          -> 20
    '''

    def add_arguments(self, parser):
        parser.add_argument('-p', '--product', type=int, help='Define a product number prefix', )
        parser.add_argument('-s', '--store', type=int, help='Define a store number prefix', )
        parser.add_argument('-c', '--category', type=int, help='Define a category number prefix', )

    def handle(self, *args, **options):

        p = options['product'] if options['product'] else 0
        c = options['category'] if options['category'] else 0
        s = options['store'] if options['store'] else 0

        if c:
            # Create 10 dummy data Category
            print('\n\n\t\tCREATING Category')
            for i in range(c):
                title = ' '.join(fake.text().split()[:3])
                print(title, end=' ')
                try:
                    img = download_image(fake.image_url(), 'category')
                except:
                    print('No answer')
                    continue
                catagory = Category.objects.create(title=title, image=img)
                catagory.save()
                print('category added')

        if s:
            # Create 20 dummy data Store
            print('\n\n\t\tCREATING Store')
            for i in range(s):
                name = fake.unique.company()
                description = ' '.join(fake.unique.text().split()[:20]) + '.'
                print(name, end=' ')
                image = download_image(fake.unique.image_url(), "store")
                store = Store.objects.create(image=image,
                                             name=name,
                                             short_des=description)
                print('store added')
        if p:
            # Create 1000 dummy data Product
            print('\n\n\t\tCREATING Product')
            stores = Store.objects.all()
            categories = Category.objects.all()
            for i in range(p):
                title = ' '.join(fake.text().split()[:3])
                print(title, end=' ')
                description = ' '.join(fake.unique.text().split()[:40]) + '.'
                price = abs(int(fake.longitude())) * 1000
                created_at = fake.date_time()
                bonus = price // 100
                free_delivery = fake.boolean()
                reserve = abs(int(fake.longitude()))
                store = random.choice(stores)
                category = random.choice(categories)
                product = Product.objects.create(title=title,
                                                 description=description,
                                                 price=price,
                                                 created_at=created_at,
                                                 bonus=bonus,
                                                 free_delivery=free_delivery, reserve=reserve, store=store,
                                                 category=category)

                print('product added')
                # Create image for product
                for j in range(random.randint(1, 6)):
                    image = download_image(fake.image_url(), 'product')
                    ProductImage.objects.create(image=image, product_id=product.id)
                    print(product.title, ' added image')


def download_image(url, place_url):
    place_url = f'fake/{place_url}'
    if not os.path.exists(f'media/{place_url}'):
        os.makedirs(f'media/{place_url}')

    with open(f'media/{place_url}/{url.split("/")[-1]}.jpg', 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            pass
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

    return place_url + '/' + url.split("/")[-1] + '.jpg'
