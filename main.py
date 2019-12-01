from flask import Flask, request, render_template
import json
import os
from flask_sqlalchemy import SQLAlchemy

project_dir=os.path.dirname(os.path.abspath(__file__))
database_file="sqlite:///{}".format(os.path.join(project_dir, "tapsearch.db"))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)


#format of dictionary : (key, value) == (UID, paragraph)
dictionary={}

#format of word_dict: (key, value) == (word, list containing UID of paragraphs the word appears in)
word_dict={}



class Paragraphs (db.Model):
    uid = db.Column (db.Integer, primary_key = True)
    paragraph=db.Column(db.Text())
    def __init__(self, paragraph, uid):
        self.paragraph=paragraph
        self.uid=uid

class Words (db.Model):
    uid = db.Column (db.Integer, primary_key = True)
    word=db.Column(db.Text())
    uids=db.Column(db.Text())
    def __init__ (self,word, uids):
        self.word=word
        self.uids=uids

@app.route ("/")
def home ():
    return render_template ("footer.html")

@app.route ("/index/")
def index():
    clear()
    return render_template ("index.html", result=word_dict)

#this route indexes the paragraphs and words
@app.route('/index_process/', methods = ['POST'])
def index_process():
    text=request.form['Text']
    paragraphs=text.splitlines()
    word_dict={}
    #Note: Since splitlines splits only at '\n'
    #Every alternate string should be an empty string
    #assign index
    for i in range (0,len(paragraphs), 2):
        ind = int (i/2)
        db.session.add (Paragraphs(paragraphs[i], ind))
        db.session.commit()

        words=paragraphs[i].split()
        for w in words:
            w=w.lower ()
            if w in word_dict:
                #to prevent repition in same paragraph
                if ind not in word_dict[w]: 
                    word_dict[w].append(ind)
            else:
                word_dict[w]=[ind]
    #store all the UIDs in a string format
    for key, value in word_dict.items ():
        l=''
        for i in value:
            l = l + str (i) + ' '
        db.session.add (Words(key,l))
        db.session.commit()

    return render_template ('footer.html', message='Done indexing')

@app.route ("/search/")
def search():
    return render_template ("search.html")


#this route is used to search for the word
@app.route ("/search_process/", methods =['GET'])
def search_process():
    key = request.args['key']
    key=key.lower()
    word_dict = Words.query.filter_by (word=key).first()
    if word_dict is None:
        return render_template ('footer.html', message = 'Not found')
    else:
        uids=word_dict.uids
        #uids is space separated IDs of the paragraphs that the word appears in
        ls=uids.split (' ')
        #delete the last element as it is only a space character
        ls=ls[:-1]
        paras_list=[]
        for num in ls:
            print (num)
            uid=int(num)
            paragraph=Paragraphs.query.filter_by(uid=uid).first()
            paras_list.append(paragraph.paragraph)
        return render_template('footer.html', list = paras_list)

@app.route ("/clear/")
def clear():
    db.drop_all()
    db.create_all()
    return render_template ('footer.html', message = 'Index cleared')

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run ()