db_host = "ec2-3-20-141-107.us-east-2.compute.amazonaws.com"
db_user = "kwoods"
db_pass = "ybQ7wxusL7sS7qNXBqQL"
db_name = "kwoods" 
db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
print(db_uri)