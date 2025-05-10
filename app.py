import mysql
import nltk
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sentence_transformers import SentenceTransformer, util
import random
from configdata import data_of_paper,response_beginnings,response_endings,fst_data
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
model = SentenceTransformer('all-MiniLM-L6-v2')
def try_to_find_paper(text, list_of_description):
    comparision = []
    for x in list_of_description:

        score = compare_those_two_declaration(text,x)
        comparision.append([ x, score])

    comparision = sorted(comparision, key=lambda item: item[1])
    return comparision[-1][0]

import tensorflow as tf
tf.debugging.set_log_device_placement(True)

departments = ["Mathematics", "Physics", "Computer Science", "Preparatory", "Biology", "Chemistry"]
# Stem all the department names
stemmed_departments = {stemmer.stem(department) for department in departments}

# Custom stop words: remove all words not in the stemmed department list
def filter_departments_with_stemmer(user_input):
    # Convert input to lowercase, tokenize, and stem
    words = nltk.word_tokenize(user_input.lower())
    
    # Stem the words and filter out those not in the department list
    filtered_words = [word for word in words if stemmer.stem(word) in stemmed_departments]
    
    # Join the remaining words back into a string
    return ' '.join(filtered_words)
def filter_class(user_input,clas) :
  stemmed_class = {stemmer.stem(x) for x in clas}
  words = nltk.word_tokenize(user_input.lower())
  filtered_words = [word for word in words if stemmer.stem(word) in stemmed_class]
  return ' '.join(filtered_words)


def try_to_find_dep(text, list_of_description):
    comparision = []
    text = filtered_text(text)
    for x in list_of_description:
        
        score = compare_those_two_declaration(text,x)
        comparision.append([ x, score])
    
    comparision = sorted(comparision, key=lambda item: item[1])
    
    return comparision[-1][0]
def try_to_find_class_floor(text, list_of_description) :
    comparision = []
    text = filtered_text(text)
    for x in list_of_description:
        
        score = compare_those_two_declaration(text,x)
        comparision.append([ x, score])
    
    comparision = sorted(comparision, key=lambda item: item[1])
    
    return comparision[-1][0]



descriptions=[] #description of all lost_items
descriptions1=[] #description of all found_items
def filtered_text(text) :
  stop_words = set(stopwords.words('english'))
  stemmer = PorterStemmer()
  custom_stop_stems = {stemmer.stem(w) for w in ['find', 'found', 'lost', 'lose', 'losing', 'loses']}
  words = word_tokenize(text)
  filtered_text = ' '.join(stemmer.stem(word) for word in words
    if word.lower() not in stop_words and stemmer.stem(word.lower()) not in custom_stop_stems)
  return filtered_text

def compare_those_two_declaration(text1,text2) :
  model = SentenceTransformer('all-MiniLM-L6-v2')
  emb1=model.encode(text1,convert_to_tensor=True)
  emb2 = model.encode(text2,convert_to_tensor=True)
  score = util.pytorch_cos_sim(emb1, emb2)
  return score

def try_to_find(text, list_of_description, seil):
    if (len(list_of_description)==0):
        return -1
    comparision = []
    text = filtered_text(text)
    i=0
    for x in list_of_description:
        score = compare_those_two_declaration(text,x)
        comparision.append([score,i])
    
    comparision = sorted(comparision, key=lambda item: item[0])
    if comparision[-1][0] < seil:
        return -1
    
    return comparision[-1][1]
app = Flask(__name__)
global_final_data = None
n=1
app.config['SECRET_KEY'] = 'mysecretkey1234'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gearsofwar3'
app.config['MYSQL_DB'] = 'hackaton'
mysql = MySQL(app)
@app.route('/')
def home():
    return render_template('accueil.html')

@app.route('/interface')
def interface():
    return render_template('interface.html')

@app.route('/chat',methods=['POST'])
def chat():
    from Main import retrieve_relevant_texts
    user_input = request.json.get("message")
    context = retrieve_relevant_texts(user_input,n)
    response = context
    
    # Retourner la réponse sous forme de JSON
    return jsonify({"response": response})


@app.route('/chat2',methods=['POST'])
def chat2():
    global descriptions1
    cur = mysql.connection.cursor()
    cur.execute("SELECT description FROM found_items")
    rows = cur.fetchall()
    cur.close()
    descriptions1 = [row[0] for row in rows]
    #print (rows[1][1])
    user_input = request.json.get("message")
    k=try_to_find(user_input,descriptions1, 0.75)
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    if k == -1:
        # 🗃️ Insertion dans la base si l’objet est introuvable
        cur.execute(
            "INSERT INTO lost_items (user_id, description) VALUES (%s, %s)",
            (user_id, filtered_text(user_input))
        )
        mysql.connection.commit()
        cur.close()
        response = "This item is not found yet. We have saved your report."
    else:
        cur.execute("SELECT phone FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        response="This item is found in our Database.You can reach the person who found it at:\n"+str(result[0])
        #query = "DELETE FROM found_items WHERE user_id = %s AND description = %s"
        #cur.execute(query, (user_id))
        cur.close()
    # Retourner la réponse sous forme de JSON
    return jsonify({"response": response})
@app.route('/index')
def index():
    return render_template('index.html')
# 📝 Inscription
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    phone=request.form['phone']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        flash("Utilisateur déjà existant", "danger")
        return redirect(url_for('home'))

    cur.execute("INSERT INTO users (username, email, password,phone) VALUES (%s, %s, %s,%s)",
                (username, email, password,phone))
    mysql.connection.commit()
    cur.close()

    flash("Inscription réussie 🎉", "success")
    return redirect(url_for('home'))
# 🔐 Connexion
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    for item in descriptions1:
        print(item)
    if user and check_password_hash(user[3], password):
        #session['username'] = username
        #flash("Connexion réussie ✅", "success")
        session['user_id'] = user[0]
        return redirect(url_for('interface'))
    else:
        flash("Identifiants incorrects ❌", "danger")
        return redirect(url_for('home'))
    
@app.route('/navigate', methods=['POST'])
def Navigate():
    global n
    n=1 
    return '', 204

@app.route('/inquire', methods=['POST'])
def inquire():
    global n
    n=2
    return '', 204
@app.route('/lost-found')
def lost_found():
    return render_template('index2.html')

@app.route('/assistant')
def found():
   return render_template('index3.html')

@app.route('/chat3',methods=['POST'])
def chat3():
    user_id = session.get('user_id')
    user_input = request.json.get("message")
    cur = mysql.connection.cursor()
    cur.execute(
            "INSERT INTO found_items (user_id, description) VALUES (%s, %s)",
            (user_id, filtered_text(user_input))
        )
    mysql.connection.commit()
    cur.close()
    response="This item is added to the database of found_items. "
    return jsonify({"response": response})
@app.route('/Lost')
def Lost():
        global descriptions
        cur = mysql.connection.cursor()
        cur.execute("SELECT description FROM lost_items")
        rows = cur.fetchall()
        cur.close()
        descriptions = [row[0] for row in rows]
        


@app.route('/Found')
def Found():
        global descriptions1
        cur = mysql.connection.cursor()
        cur.execute("SELECT description FROM found_items")
        rows = cur.fetchall()
        cur.close()
        descriptions1 = [row[0] for row in rows]



@app.route('/chat4',methods=['POST'])
def chat4():
    user_input = request.json.get("message")
    words = user_input.split()  # Divise la chaîne en mots
    beginning = random.choice(response_beginnings)
    ending = random.choice(response_endings)
    for word in words:
        if word.lower() == "class":
            res=try_to_find_dep(user_input,departments)
            response = beginning
            response += fst_data[res]["description"]
            res50 = try_to_find_class_floor(user_input,fst_data[res]["floors"])
            response+=res50 + "is located in" + fst_data[res]["floors"][res50]
            response+=ending
            return jsonify({"response": response})
    
    res=try_to_find_dep(user_input,departments)
    response = fst_data[res]["description"]
    return jsonify({"response": response})

@app.route('/chat5',methods=['POST'])
def chat5():
    beginning = random.choice(response_beginnings)
    ending = random.choice(response_endings)
    user_input = request.json.get("message")
    response=beginning
    response+=data_of_paper[try_to_find_paper(user_input,data_of_paper.keys())]
    response+=ending
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=False)
