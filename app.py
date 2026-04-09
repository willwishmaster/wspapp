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
        res.message('''Hola, gracias por contactar a *The Red Velvet*.\nPuedes elegir una de las opciones debajo:
          \n*Tipo*\n\n1️⃣Para *contacto* us\n2️⃣Para *ordenar* bocaditos\n3️⃣Para conocer nuestro *horario de trabajo*\n4️⃣Para obtener nuestra *dirección *''')
        users.insert_one({"number":number, "status":"main", "messages":[]})
    elif user["status"] == "main":
        try:
            option = int(content)
        except:
            res.message("Por favor elige una opcion!")
            return str(res)
        if option == 1:
            res.message("Puedes contactarnos al telefono o e-mail.\n\n*Celular*: 9484848\n*E-mail*: bakery@valverde.com")
        elif option == 2:
            res.message("Has ingresado a *modo de pedido*.")            
            users.update_one({"number":number},{"$set":{"status":"ordering"}})
            res.message('''Puedes seleccionar uno de los siguientes pasteles para pedir:
                        \n1️⃣Red Velvet\n2️⃣Dark Forest\n3️⃣Ice Cream Cake\n4️⃣Plum Cake\n5️⃣Sponge Cake\n6️⃣Genoise Cake\n7️⃣Angel Cake\n8️⃣Carrot Cake''')
        elif option == 3:
            res.message("Abrimos todos los días de *9 AM a 9 PM*")
        elif option == 4:
            res.message("Tenemos muchos centros en toda la ciudad. Nuestro centro principal está en *4/50, New York City*")            
    elif user["status"] == "ordering":
        try:
            option = int(content)
        except:
            res.message("¡Por favor, elige una opción válida!")
            return str(res)
        if option == 0:
            users.update_one({"number":number},{"$set":{"status":"main"}})
            res.message('''Hola, gracias por contactar con *The Red Velvet*.\nPuedes elegir una de las siguientes opciones:                        
                        \n*Tipo*\n\n1️⃣Para *contactarnos*\n2️⃣Para *pedir* snacks\n3️⃣Para conocer nuestro *horario de atención*\n4️⃣Para obtener nuestra *dirección*''')
        elif 1<=option <= 9:
            cakes = ["Red Velvet","Dark Forest","Ice Cream Cake","Plum Cake","Sponge Cake","Genoise Cake","Angel Cake","Carrot Cake"]
            selected = cakes[option -1 ]
            users.update_one({"number":number},{"$set":{"status":"address"}})
            users.update_one({"number":number},{"$set":{"item":selected}})
            res.message("¡Gran elección 😛!")
            res.message("Por favor, ingresa tu dirección para *confirmar* el pedido")
        else:            
            res.message("¡Por favor, elige una opción válida!")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Gracias por confiar en nosotros!")
        res.message(f"Tu pedido de {selected} ha sido recibido y será entregado dentro de una hora")
        orders.insert_one({"number":number, "item": selected, "address":content,"order_time": datetime.now()})
        users.update_one({"number":number},{"$set":{"status":"ordered"}})
    elif user["status"] == "ordered":
        res.message('''Hola, gracias por contactar con *The Red Velvet*.\nPuedes elegir una de las siguientes opciones:                        
                        \n*Tipo*\n\n1️⃣Para *contactarnos*\n2️⃣Para *pedir* snacks\n3️⃣Para conocer nuestro *horario de atención*\n4️⃣Para obtener nuestra *dirección*''')
        users.update_one({"number":number},{"$set":{"status":"main"}})
        
    users.update_one({"number":number},{"$push":{"messages":{"content": content, "date": datetime.now()}}})
    return str(res)

if __name__ == '__main__':
    app.run()
