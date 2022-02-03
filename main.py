import pickle
import re
import os
from flask import Flask,jsonify,request,send_file
from dotenv import load_dotenv
import os
import json

# Load models
fittedModel= pickle.load(open('models/category.pickle','rb'))
binarizer= pickle.load(open('models/binarizer.pickle','rb'))
vectorizer= pickle.load(open(   'models/vectorizer.pickle','rb' ))

def clean_text(text):
    # remove backslash-apostrophe 
    text = re.sub("\'", "", text) 
    # remove everything except alphabets 
    text = re.sub("[^a-zA-Z]"," ",text) 
    # remove whitespaces 
    text = ' '.join(text.split()) 
    # convert text to lowercase 
    text = text.lower() 
    
    return text

def predict(d):
    #d = input("Enter Description: ")
    #print("")
    d = clean_text(d)
    d = [d]
    x = vectorizer.transform(d)
    z = fittedModel.predict(x)
    z_pred_prob=fittedModel.predict_proba(x)
    z_pred_new=(z_pred_prob>=0.1).astype(int)

    #print("Predicted Industries: ")
    return binarizer.inverse_transform(z_pred_new)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# set env for secret key
load_dotenv()

secret_id = os.getenv('AI_SERVICE_SECRET_KEY')

# print(secret_id)
def check_for_secret_id(request_data):    
    try:
        if 'secret_id' not in request_data.keys():
            return False, "Secret Key Not Found."
        
        else:
            if request_data['secret_id'] == secret_id:
                return True, "Secret Key Matched"
            else:
                return False, "Secret Key Does Not Match. Incorrect Key."
    except Exception as e:
        message = "Error while checking secret id: " + str(e)
        return False,message

@app.route('/industry_prd',methods=['POST'])  #main function
def main():
    params = request.get_json()
    desc= params['data']
    desc = desc[0]['description']
    key = params['secret_key']

    request_data = {'secret_id' : key}
    secret_id_status,secret_id_message = check_for_secret_id(request_data)
    print ("Secret ID Check: ", secret_id_status,secret_id_message)
    if not secret_id_status:
        return jsonify({'message':"Secret Key Does Not Match. Incorrect Key.",
                        'success':False}) 
    else:
        # predict category of description
        prediction= predict(desc)
        dictonary = {"Prediction": prediction}
    return dictonary

if __name__ == '__main__':
    app.run()    
  