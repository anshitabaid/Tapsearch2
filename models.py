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
