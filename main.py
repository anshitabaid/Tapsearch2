from flask import Flask, request, render_template
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from werkzeug.utils import secure_filename
from helpers import *
#set up database
project_dir=os.path.dirname(os.path.abspath(__file__))
database_file="sqlite:///{}".format(os.path.join(project_dir, "tapsearch.db"))
upload_folder = project_dir + '/uploads/'
allowed_extensions={'pdf'}

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']=upload_folder
heroku = Heroku(app)
db = SQLAlchemy(app)


#contains UID for each paragraph, and the paragraph itself
class Paragraphs (db.Model):
    uid = db.Column (db.Integer, primary_key = True)
    paragraph=db.Column(db.Text())
    def __init__(self, paragraph, uid):
        self.paragraph=paragraph
        self.uid=uid

#contains the word, and a space separated string of UID of paragraphs the word appears in
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
    return render_template ("index.html")


#this route indexes the paragraphs and words
@app.route('/index_process/', methods = ['POST'])
def index_process():
    text = ''
    #check if pdf was uploaded
    if request.files['file']:
        file=request.files['file']
        if allowed_file (file.filename):
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            text=convert_pdf_to_txt(upload_folder +  filename)
    #no file was uploaded
    else:
        text=request.form['Text']
    paragraphs=text.split('\r\n\r\n')
    word_dict={}

    for i in range (0,len(paragraphs)):
        if  paragraphs[i]==' ' or paragraphs[i]=='\r' or paragraphs[i]=='\r\n' or paragraphs[i]=='':
            continue
        print (paragraphs[i])
        print ('....')
        #add paragraph and UID to database
        db.session.add (Paragraphs(paragraphs[i], i))
        db.session.commit()

        words=paragraphs[i].split()
        for w in words:
            w=format (w)
            if w in word_dict:
                #to prevent repition in same paragraph
                if i not in word_dict[w]: 
                    word_dict[w].append(i)
            else:
                word_dict[w]=[i]
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
        #display corresponding paragraph for each UID of the paragraph the word appears in
        for i in range (min(10, len(ls))):
            uid=int(ls[i])
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