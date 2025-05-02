import mysql
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sentence_transformers import SentenceTransformer, util
import random

data_of_paper = {
  "Student ID Card": "To obtain a student ID card, go to the Student Affairs Office. Required documents: enrollment certificate, copy of National ID, one passport-sized photo. Fill out the ID request form. Processing takes 2–3 business days. Collect the card in person.",

  "Enrollment Certificate": "To request an enrollment certificate, visit the Registrar's Office. Required documents: valid student ID, completed request form. The certificate is issued in 1–2 business days, either via email or in person.",

  "Academic Transcript": "To get an academic transcript, go to the Registrar's Office. Required documents: student ID, transcript request form, and payment receipt if applicable. Processing time is 3–5 business days. Transcripts are provided by mail or in person.",

  "Dormitory Housing": "To apply for dormitory housing, submit your application to the Housing Office. Required documents: enrollment certificate, copy of National ID, passport-sized photo, housing application form. Results are announced in 5–10 business days via email or posted notice.",

  "Cafeteria Card": "To receive a cafeteria card, go to the Student Services Office. Required documents: student ID, one passport-sized photo, filled-out cafeteria application form. Processing takes 2 business days.",

  "Internship Authorization Letter": "To get authorization for an internship, visit the Internships Office. Required documents: student ID, internship acceptance letter, internship request form. Letter issued in 3 business days via email or in person.",

  "Degree Certificate": "To collect your degree certificate after graduation, go to the Registrar's Office. Required documents: student ID, completed request form, clearance form (confirms all dues are cleared). Processing takes 10–15 business days.",

  "Re-Issuance of Lost Student Card": "To replace a lost student card, go to the Student Affairs Office. Required documents: police declaration of loss, one passport-sized photo, copy of National ID, and replacement fee receipt. New card is issued in 3 days.",

  "Student Insurance Registration": "To register for student insurance, go to the Insurance Desk. Required documents: student ID, insurance registration form, passport photo, and copy of National ID. Insurance proof issued in 5 days.",

  "Library Card Registration": "To obtain a library card, go to the university library. Required documents: valid student ID, passport-sized photo, and library registration form. Card is issued immediately.",

  "Change of Major or Program": "To change your major or academic program, consult your academic advisor and submit your request to the Dean’s Office. Required documents: written request, academic transcript, and student ID. Decision given within 7–10 business days.",

  "Leave of Absence Request": "To request a leave of absence, go to the Registrar's Office. Required documents: filled-out leave request form, supporting documents (e.g., medical certificate), and student ID. Processed within 5 business days.",

  "Scholarship Request": "To apply for a scholarship, go to the Financial Aid Office. Required documents: scholarship application form, proof of family income, recent academic transcripts, and student ID. Processing takes 2–4 weeks.",

  "Student Visa Renewal (International Students)": "To renew your visa, visit the International Students Office. Required documents: passport, copy of current visa, proof of enrollment, proof of financial means, housing certificate. Processing takes 15–30 days.",

  "Official Letter for Embassy": "To request an official university letter (e.g., for embassy), visit the Registrar's Office. Required documents: student ID, request form, reason for the letter. Processing takes 2–3 business days."
}
def try_to_find_paper(text, list_of_description):
    comparision = []
    for x in list_of_description:

        score = compare_those_two_declaration(text,x)
        comparision.append([ x, score])

    comparision = sorted(comparision, key=lambda item: item[1])
    return comparision[-1][0]



fst_data = {
  "Mathematics": {
    "description": "From the main entrance (Rue Habib Chatti), walk straight along the central building. The Department of Mathematics is in the building to the left after the Khawarizmi Computing Center, located in the northeast corner of the campus.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "1st floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "2nd floor",
      "class 19": "2nd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "3rd floor",
      "class 23": "3rd floor",
      "class 24": "3rd floor",
      "class 25": "4th floor",
      "class 26": "4th floor",
      "class 27": "4th floor",
      "class 28": "4th floor",
      "class 29": "4th floor"
    }
  },
  "Computer Science": {
    "description": "From the main entrance, turn left and walk to the end of the campus. The Computer Science Department is in the Informatics Block, near the sports hall in the northwest corner.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "2nd floor",
      "class 19": "2nd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "3rd floor",
      "class 23": "3rd floor",
      "class 24": "3rd floor",
      "class 25": "4th floor",
      "class 26": "4th floor",
      "class 27": "4th floor",
      "class 28": "4th floor",
      "class 29": "4th floor"
    }
  },
  "Physics": {
    "description": "From the main entrance, walk straight toward Amphi B, then turn left. The Physics Department is in the TP and TD Physics blocks, behind the central mosque.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "2nd floor",
      "class 19": "2nd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "3rd floor",
      "class 23": "3rd floor",
      "class 24": "4th floor",
      "class 25": "4th floor",
      "class 26": "4th floor",
      "class 27": "4th floor",
      "class 28": "4th floor"
    }
  },
  "Biology": {
    "description": "From the main entrance, take the main road to the right, pass the central building, and turn left. The Biology Department is located at the southeast edge of campus, sharing space with the Geology building.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "2nd floor",
      "class 19": "3rd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "3rd floor",
      "class 23": "3rd floor",
      "class 24": "4th floor",
      "class 25": "4th floor",
      "class 26": "4th floor",
      "class 27": "4th floor",
      "class 28": "4th floor"
    }
  },
  "Preparatory": {
    "description": "From the main entrance, walk straight to reach Amphi B. The Preparatory Department is just next to it, in the center of the campus.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "3rd floor",
      "class 19": "3rd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "4th floor",
      "class 23": "4th floor",
      "class 24": "4th floor",
      "class 25": "4th floor"
    }
  },
  "Chemistry": {
    "description": "From the main entrance, walk straight and turn left after Amphi B. The Chemistry Department is in the large marked building in the southwest corner, under the Tunisian Chemical Society sign.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "1st floor",
      "class 14": "1st floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "2nd floor",
      "class 18": "2nd floor",
      "class 19": "3rd floor",
      "class 20": "3rd floor",
      "class 21": "3rd floor",
      "class 22": "3rd floor",
      "class 23": "4th floor",
      "class 24": "4th floor",
      "class 25": "4th floor",
      "class 26": "4th floor"
    }
  },
  "Geology": {
    "description": "From the main entrance, walk straight and turn left toward the Chemistry Department. The Geology Department is next to it, slightly south-central on campus.",
    "floors": {
      "class 1": "Ground floor",
      "class 2": "Ground floor",
      "class 3": "Ground floor",
      "class 4": "Ground floor",
      "class 5": "Ground floor",
      "class 6": "Ground floor",
      "class 7": "Ground floor",
      "class 8": "Ground floor",
      "class 9": "1st floor",
      "class 10": "1st floor",
      "class 11": "1st floor",
      "class 12": "1st floor",
      "class 13": "2nd floor",
      "class 14": "2nd floor",
      "class 15": "2nd floor",
      "class 16": "2nd floor",
      "class 17": "3rd floor",
      "class 18": "3rd floor",
      "class 19": "3rd floor",
      "class 20": "3rd floor",
      "class 21": "4th floor",
      "class 22": "4th floor",
      "class 23": "4th floor"
    }
  }
}


response_beginnings = [
    "Sure, I can help with that.",
    "Absolutely! Let’s take a look.",
    "Of course, here’s what I found.",
    "No problem—here’s the info.",
    "Got it! Let me explain.",
    "Thanks for asking! Here’s the answer.",
    "Okay, here’s how it works.",
    "Great question. Here’s what I know:",
    "Let’s break this down.",
    "You're right to ask that. Here's the detail.",
    "Here’s what I came up with:",
    "Right away! Here's the result.",
    "Yes, and here’s why:",
    "Good point. Let me elaborate:",
    "Okay! Here's a simple explanation:",
    "You're asking the right question. Here it is:",
    "I'm glad you asked! Here's some insight:",
    "Interesting topic! Let's explore it:",
    "Let’s go over that step by step:",
    "I’ve looked into it. Here’s what I found:",
    "Let me walk you through it:",
    "Here’s a breakdown for you:",
    "This might help clarify:",
    "Certainly. Here's an overview:",
    "Allow me to explain it in detail:",
    "I’d be happy to explain that:",
    "Here is the response you’re looking for:",
    "Here’s what you need to know:",
    "Let’s dive into the answer:",
    "Let me guide you through that:"
]


response_endings = [
    "Let me know if you’d like more details.",
    "I hope that clears it up!",
    "Does that answer your question?",
    "Let me know if you need help with anything else.",
    "Feel free to ask more about this.",
    "Hope that helps!",
    "Let me know if anything's unclear.",
    "Would you like a summary?",
    "I'm here if you have follow-up questions.",
    "Just ask if you need more examples.",
    "I can go deeper if you’d like!",
    "Do you want to explore another topic?",
    "Tell me if you'd like it explained differently.",
    "Let’s continue if you have more questions.",
    "That should cover the basics.",
    "Let me know if you need clarification.",
    "I'm happy to explain more if needed.",
    "Need a real-world example?",
    "If that’s all, we’re good to go!",
    "Was that what you were looking for?",
    "I can give you the source if you need it.",
    "Would you like a visual explanation?",
    "Let me know if I should rephrase it.",
    "Any specific part you’d like more on?",
    "Just say the word if you want to continue.",
    "I hope that was helpful.",
    "Ready for the next one?",
    "Let’s move on if you're good with that.",
    "Tell me if you'd like to repeat anything.",
    "Shall we go further into this?"
]


import tensorflow as tf
tf.debugging.set_log_device_placement(True)

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sentence_transformers import SentenceTransformer
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
model = SentenceTransformer('all-MiniLM-L6-v2')

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
    from Main import get_contextual_response,retrieve_relevant_texts
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
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
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
