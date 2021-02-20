# importing the requests library 
import requests 
  
# defining the api-endpoint  
API_ENDPOINT = "http://localhost:8000/billing/addproduct/"

data = {'name':"someProduct", 
        'brandName':"someBrand", 
        'price':200,} 

r = requests.post(url = API_ENDPOINT, data = data) 