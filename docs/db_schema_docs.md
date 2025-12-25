# E-Commerce-Inventory-API
	All the deatils of planning stage is placed here.

### DB Schema's
- User Table
- Employee Table [For internal Use]
- Order Management Table's [ideally order data comes from the frontend]
- Inventory and Product Table
- Category Table
- Inventory
- Supplier Table

### Detailed Db Schema's
	Default Columns in all : id(pk), created_at, updated_at
- **OrderItem [Mainly for warehouse to process items]**
	- tracking_id (fk from #3)
	- product_id (fk)
	- catg_id (fk)
	- quantity
	- is_processed
	- is_confirmed 
	*This table is mainly for the employees who are affiliated to processing the orders. If a order is not confirmed then it wont be processed and after processing the order, 'is_processed' will be true.*

- **OrderSummary**
	- orderitem_id (fk from #1)
	- price_at_order
	- tracking_id (fk from #3)
	- user_id

- **OrderTracking**
	- tracking_number (randomly generated number)
	- user_id (fk)
	- pay_method
	- payment_status (cod/paid)
	- order_status (confirmed/canelled/placed)
	- delivery_status

- **Products** 
	- product name
	- short_desc (50 words)
	- current_price
	- image_link
	- in_stock (bool)
	- catg_id (fk) 
	*in_stock will be changed using a background job. The bg job will check the Inventory db and if the current_stock column is '0' then it will turned False and the product will be shown as 'out of stock'*
	
- **Category**
	- category
	- category_normal (for indexing purposes)

- **Inventory**
	- sku (generated based on catg + color + size. ex: TS-BLU-M)
	- product_id (fk from #4)
	- current_stock (available)
	- on_hold (orders placed but not confirmed)
	- confirmed_stock (orders that are confirmed.)

- **ProductVariant**
	- sku_id (fk from #6)
	- product_id (fk from #4)
	- attribute (via user input. ex: size, color etc)
	- attr_value (ex: 42, red etc)

- **ProductSupplierlink**
	- product_id
	- supp_id
	- rate
	- unit_supplied
	- transport_method (warehouse_delivery/ own_cost)

- **Supplier**
	- name
	- type (manufacturer, distributor, dropshipper, white_label) 
	- email
	- phone
	- is_supplying (bool)

- **SupplierDetails**
	- supp_id (fk from #)
	- address_line
	- postal_code
	- city
	- country
	- sec_phone
	- sec_email


	
