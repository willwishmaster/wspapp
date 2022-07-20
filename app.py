from datetime import datetime
from operator import rshift
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://broot:broot@cluster0.tdnuk.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get","post"])
def reply():
    content = request.form.get("Body")
    number = request.form.get("From")
    # number = number.replace("whatsapp:", "")[:-2]
    print(number)
    res= MessagingResponse()
    user = users.find_one({"number": number})
    
    if bool(user) == False:
        res.message('''Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below:
          \n*Type*\n\n1️⃣To *contact* us\n2️⃣To *order* snacks\n3️⃣To know our *working hours*\n4️⃣To get our *address*''')
        users.insert_one({"number":number, "status":"main", "messages":[]})
    elif user["status"] == "main":
        try:
            option = int(content)
        except:
            res.message("Please choose a valid option!")
            return str(res)
        if option == 1:
            res.message("You can contact us through phone or e-mail.\n\n*Phone*: 9484848\n*E-mail*: bakery@valverde.com")
        elif option == 2:
            res.message("You have entered *ordering mode*.")            
            users.update_one({"number":number},{"$set":{"status":"ordering"}})
            res.message('''You can select one of the following cakes to order:
                        \n1️⃣Red Velvet\n2️⃣Dark Forest\n3️⃣Ice Cream Cake\n4️⃣Plum Cake\n5️⃣Sponge Cake\n6️⃣Genoise Cake\n7️⃣Angel Cake\n8️⃣Carrot Cake''')
        elif option == 3:
            res.message("We open every day from *9 AM to 9 PM*")
        elif option == 4:
            res.message("We have many centres across the city. Our main center is at *4/50, New York City*")
    elif user["status"] == "ordering":
        try:
            option = int(content)
        except:
            res.message("Please choose a valid option!")
            return str(res)
        if option == 0:
            users.update_one({"number":number},{"$set":{"status":"main"}})
            res.message('''Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below:
                        \n*Type*\n\n1️⃣To *contact* us\n2️⃣To *order* snacks\n3️⃣To know our *working hours*\n4️⃣To get our *address*''')
        elif 1<=option <= 9:
            cakes = ["Red Velvet","Dark Forest","Ice Cream Cake","Plum Cake","Sponge Cake","Genoise Cake","Angel Cake","Carrot Cake"]
            selected = cakes[option -1 ]
            users.update_one({"number":number},{"$set":{"status":"address"}})
            users.update_one({"number":number},{"$set":{"item":selected}})
            res.message("Great choice 😛")
            res.message("Please Enter your address to confirm the order")
        else:
            res.message("Please choose a valid option!")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for trust on us!")
        res.message(f"Your order for {selected} has been received and will be delivered within an hour")
        orders.insert_one({"number":number, "item": selected, "address":content,"order_time": datetime.now()})
        users.update_one({"number":number},{"$set":{"status":"ordered"}})
    elif user["status"] == "ordered":
        res.message('''Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below:
          \n*Type*\n\n1️⃣To *contact* us\n2️⃣To *order* snacks\n3️⃣To know our *working hours*\n4️⃣To get our *address*''')
        users.update_one({"number":number},{"$set":{"status":"main"}})
        
    users.update_one({"number":number},{"$push":{"messages":{"content": content, "date": datetime.now()}}})
    return str(res)

if __name__ == '__main__':
    app.run()
