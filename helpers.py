allowed_extensions={'pdf'}
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

#method to format the word: lowercase and remove special chars
def format(w):
    w=w.lower()
    badchars=['.', ',', ';', '!', '(', ')']
    for i in badchars:
        w=w.replace (i, '')
    return w
