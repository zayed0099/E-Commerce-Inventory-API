import requests as req
import random
import string

characters = string.ascii_letters + string.digits

def generate_short_desc(product_name):
	# just generated some generic description using chatgpt
	desc = [
		"The {product_name} offers reliable performance, modern features, and a sleek design suitable for everyday home or office use.",
		"Designed for convenience and efficiency, the {product_name} delivers dependable functionality and a user-friendly experience.",
		"The {product_name} combines durability, practical features, and modern technology to support everyday tasks with ease.",
		"Enjoy smooth performance and simple usability with the {product_name}, built for reliable daily operation.",
		"With a balanced mix of performance, design, and reliability, the {product_name} fits seamlessly into everyday life."
	]

	any_desc = random.choice(desc)
	return any_desc.format(product_name=product_name)

def create_product_data():
	products_list = ["Laptop", "Tablet", "Smartphone", "Microwave", "Washing Machine", "AC"]
	brands = ["LG", "Panasonic", "HP", "Hitachi", "Gree", "Xiaomi", "Huawei"]

	product = random.choice(products_list)
	brand = random.choice(brands)

	rndm_str = ''.join(random.choices(characters, k=5))
	base_url = "https://www.ecommbd.com/cdn-cgi/image/products/"

	product_name = brand + " " + product + " " + rndm_str
	prod_name = product + "-" + rndm_str

	image_link = base_url + prod_name.replace(" ", "-")
	short_desc = generate_short_desc(product_name)
	current_price = random.choice([30000, 35000, 40000, 45000, 50000])
	in_stock = random.choice([True, False])
	catg_id = 1 # for now electronics id = 1
	supplier_id = random.randint(1, 20)
	
	sku = f"{brand.upper()}-{product.upper()}-{rndm_str.upper()}"
	current_product_stock = random.randint(1, 50)


	if product in ["Laptop", "Tablet", "Smartphone"]:
		ram = random.choice(["4GB", "8GB", "16GB"])
		storage = random.choice(["128GB", "256GB", "512GB", "1TB"])
		display = random.choice(["IPS LCD", "AMOLED", "VA LCD"])
		battery = str(random.choice([4500, 5000, 5500, 6000])) + "mAh"

		attributes = {
			"ram" : ram, "storage" : storage, "display" : display, "battery" : battery
		}

	elif product == "Microwave":
		capacity = "45L"
		convection = random.choice(["bake", "roast", "grill", "all"])
		power_wattage = str(random.choice([700, 800, 900, 1000, 1100, 1200])) + "W"
		speciality = random.choice(["reheating", "defrosting", "simple_cooking"])

		attributes = {
			"capacity" : capacity, "convection" : convection,
			"power_wattage" : power_wattage, "speciality" : speciality
		}

	elif product.lower() == "washing machine":
		loading_type = random.choice(["top_load", "front_load"])
		capacity = str(random.choice([5, 10, 15, 20, 25, 30, 35, 40])) + "KG"
		programs = random.choice(["normal", "delicate", "heavy", "quick wash"])

		attributes = {
			"loading_type" : loading_type, "capacity" : capacity, "programs" : programs
		}

	elif product == "AC":
		compressor = random.choice(["indoor", "outdoor"])
		capacity = str(random.choice([1, 1.5, 2, 2.5, 3])) + "Ton"
		EER = str(random.choice([100, 200, 300, 400, 500, 600, 700]))

		attributes = {
			"compressor" : compressor, "capacity" : capacity, "EER" : EER
		}

	product_payload = {
		"product_name": product_name,
		"short_desc": short_desc,
		"image_link": image_link,
		"current_price": current_price,
		"in_stock": in_stock,
		"supplier_id": supplier_id,
		"catg_id": 1
	}

	variant_payload = {
		"sku" : sku,
		"in_stock" : random.choice([True, False]) if in_stock == True else False,
		"current_product_stock" : current_product_stock,
		"attributes" : attributes
	}

	return product_payload, variant_payload

def post_data_to_endpoint(product_payload: dict, variant_payload: dict):
	url_product = "http://127.0.0.1:8000/api/v1/internal/product/new"
	product_response = req.post(url_product, json=product_payload)

	if not product_response.status_code in [200, 201]:
		print("Product Entry Failed!")
		exit()

	data_from_product_entry = product_response.json()
	product_id = data_from_product_entry["product_id"]

	# adding product id to variant payload
	variant_payload.setdefault("product_id", product_id)

	if not isinstance(product_id, int):
		print ({
			"err" : "Invalid product Id", 
			"p_id" : product_id, "data_from_product_entry" : data_from_product_entry})

	url_variant = "http://127.0.0.1:8000/api/v1/internal/product/add-variant"
	variant_response = req.post(url_variant, json=variant_payload)

	if not variant_response.status_code in [200, 201]:
		print({"err" : "Product variant entry failed!","rsn" : variant_response.text})
		exit()

	print("Product and Product Variant Data Entry Successful!")


product_amnt = int(input("How many product entry do you want? : "))

for _ in range(product_amnt):
	product_payload, attributes = create_product_data()
	post_data_to_endpoint(product_payload, attributes)