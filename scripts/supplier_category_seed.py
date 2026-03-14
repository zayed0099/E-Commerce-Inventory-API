import requests as req
import random
import string
from faker import Faker
characters = string.ascii_letters + string.digits

# url_catg = "http://127.0.0.1:8000/api/v1/internal/category/new"
# catg_response = req.post(url_catg, json={"category" : "Electronics"})

# if not catg_response.status_code in [200, 201]:
# 	print("Category Entry Failed!")
# 	print(catg_response)
# 	exit()
# print("Catgory Entry Successful!")
# print(catg_response)

fake = Faker()

def create_supplier_data():
	name = fake.first_name() + " " + fake.first_name() + " " + random.choice(["Ltd", "Pvt", "Inc", "LLC"])
	
	phone = "+123" + str(random.randint(100000000, 999999999))
	sec_phone = "+123" + str(random.randint(100000000, 999999999))
	
	f_name = fake.first_name().lower()
	l_name = fake.last_name().lower()

	email_provider = random.choice(["gmail.com", "hotmail.com", "yahoo.com"])
	sec_email_provider = random.choice(["gmail.com", "hotmail.com", "yahoo.com"])

	email = f_name + "@" + email_provider
	sec_email = l_name + "@" + sec_email_provider

	address_line = fake.street_address()
	postal_code = fake.zipcode()
	city = fake.city()
	country = fake.country()
	supp_type = random.choice(['manufacturer', 'distributor', 'dropshipper', 'white_label'])
	
	supplier_data = {
	    "is_supplying": random.choice([True, False]),
	    "name": name,
	    "phone": phone,
	    "sec_phone": sec_phone,
	    "email": email,
	    "sec_email": sec_email,
	    "address_line": address_line,
	    "postal_code": postal_code,
	    "city": city,
	    "country": country,
	    "supp_type" : supp_type
	}

	return supplier_data

def post_supplier_data(supplier_data):
	url_supplier = "http://127.0.0.1:8000/api/v1/internal/supplier/new"

	supp_response = req.post(url_supplier, json=supplier_data)

	if not supp_response.status_code in [200, 201]:
		# return("Supplier Entry Failed!")
		return(supp_response.text)
		exit()
	return("Supplier Entry Successful!")
	return(supp_response)

count = int(input("How many suppier data for entry? :- "))

for _ in range(count):
	supplier_data = create_supplier_data()
	print(post_supplier_data(supplier_data))



