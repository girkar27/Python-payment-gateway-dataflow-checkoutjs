import flask
from flask import Flask, redirect, render_template, request, url_for
from random import randint
import hashlib
import requests
import json

app = Flask(__name__)

    
@app.route('/', methods = ['GET', "POST"])
def ingenico_request(): 
    f = open('ingenico_data.json',)
    json_data = json.load(f)    

    data = {}
    merchantTxnRefNumber = str(randint(1,1000000))
    Amount = "1.00"
    CustomerId = 'cons' + str(randint(1,1000000))
    customerMobNumber = "1234567890"
    email = "test@test.com"
    returnUrl = "http://127.0.0.1:5000/response"

    data["mrctCode"] = json_data["mrctCode"]
    data["merchantTxnRefNumber"] = merchantTxnRefNumber
    data["Amount"] = json_data["Amount"]
    data["CustomerId"] = CustomerId
    data["customerMobNumber"] = json_data["customerMobNumber"]
    data["email"] = json_data["email"]
    data["SALT"] = json_data["SALT"]
    data["currency"] = json_data["currency"]
    data["scheme"] =json_data["scheme"]
    data["returnUrl"] = json_data["returnUrl"]

    datastring = data["mrctCode"] + "|" + data["merchantTxnRefNumber"] + "|" + data["Amount"] + "|" + "|" + data["CustomerId"] + "|" + data["customerMobNumber"] + "|" + data["email"] + "||||||||||" + data["SALT"]
    
    hashed = hashlib.sha512(datastring.encode())
    data["token"] = hashed.hexdigest()

    return render_template("ingenico.html", data = data)


@app.route('/response', methods = ['POST'])
def ingenico_response():
    if request.method == "POST":
        data_str = request.values["msg"]
        data = data_str.split('|')
        status = data[0]
        datewithtime = data[8].split(" ")
        date = datewithtime[0]
        tpl_txn_id = data[5]
        url = "https://www.paynimo.com/api/paynimoV2.req"
        myobj = {
            "merchant": {
                "identifier": mrctCode
            },
            "transaction": {
                "deviceIdentifier": "S",
                "currency": currency,
                "dateTime": date,
                "token": tpl_txn_id,
                "requestType": "S"
            }
        }

        post_data = requests.post(url, json = myobj) 
        jsonstr = json.loads(post_data.text)
        scall_status = jsonstr["paymentMethod"]["paymentTransaction"]["statusCode"]

        if status == "0300" and scall_status == "0300":
            return data_str + "----------(Success)"
        else:
            return data_str + "----------(Failure)"

@app.route('/offline', methods = ['GET'])
def offline_ver():
    f = open('ingenico_data.json',)
    json_data = json.load(f)
    myobj = {
      "merchant": {
        "identifier": json_data["mrctCode"]
      },
      "transaction": {
        "deviceIdentifier": "S",
        "currency": json_data["currency"],
        "identifier":json_data["offlineverification"]["identifier"],
        "dateTime": json_data["offlineverification"]["dateTime"],
        "requestType": "O"
      }
    } 

    url = "https://www.paynimo.com/api/paynimoV2.req"

    post_data = requests.post(url, json = myobj) 
    jsonstr = json.loads(post_data.text)
    status = jsonstr["paymentMethod"]["paymentTransaction"]["statusCode"]   
    return jsonstr


@app.route('/refund', methods = ['GET'])
def refund_ver():
    f = open('ingenico_data.json',)
    json_data = json.load(f)
    myobj = {
      "merchant": {
        "identifier": json_data["mrctCode"]
      },
      "cart": {
      },
      "transaction": {
        "deviceIdentifier": "S",
        "amount":json_data["refund"]["refund_amount"],
        "currency": json_data["currency"],
        "dateTime": json_data["refund"]["dateTime"],
        "token": json_data["refund"]["token"],
        "requestType": "R"
      }
    }

    url = "https://www.paynimo.com/api/paynimoV2.req"

    post_data = requests.post(url, json = myobj) 
    jsonstr = json.loads(post_data.text)
    status = jsonstr["paymentMethod"]["paymentTransaction"]["statusCode"]   
    return jsonstr


if __name__ == '__main__':
    app.run(debug=True)