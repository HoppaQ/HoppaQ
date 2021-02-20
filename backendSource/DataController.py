import mysql.connector
from DatabaseConnection import *

mydb = get_connection()


def get_all_products():
	mycursor = mydb.cursor()

	mycursor.execute("select product.nameproduct, brand.namebrand, product.typeproduct from product, brand where product.idbrand = brand.idbrand")
	brands = mycursor.fetchall()

	mycursor.execute(" select product.nameproduct, product_description.description, product_description.manufacture_date, product_description.expiration_date  from product, product_description where product.idproduct = product_description.idproduct")
	description = mycursor.fetchall()

	mycursor.execute("select product.nameproduct, product_price.priceproduct from  product, product_price where product.idproduct = product_price.idproduct")
	price = mycursor.fetchall()

	mycursor.execute("select product.nameproduct, product_weights.weightproduct from  product, product_weights where product.idproduct = product_weights.idproduct")
	weight = mycursor.fetchall()

	print(brands)
	print(description)
	print(price)
	print(weight)


get_all_products()