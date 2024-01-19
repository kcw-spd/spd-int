import requests

API_URL = "https://api-inference.huggingface.co/models/templates/tabular-classification"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.content
response = query({
	"inputs": {"data": '{"Height":[11.52,12.48],"Length1":[23.2,24.0],"Length2":[25.4,26.3],"Species": ["Bream","Bream"]}'},
})