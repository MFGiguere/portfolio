"""
source venv/Scripts/activate
export FLASK_DEBUG=1
flask run
"""

from flask import Flask, render_template, make_response
import csv, re
from .ngram import Ngram

activities = []
with open('static/articles.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=";", quotechar='|')
    for row in spamreader:
        activities.append(row)

text = []
with open('static/text.txt', encoding='utf-8') as f:
    lines = (line.rstrip() for line in f) 
    lines = list(line for line in lines if line)
    for line in lines:
        print(line)
        if line[0].isdigit():
            line = "</div><div class='card col-12'><h5>"+line+"</h5>"
        else:
            line = "<p>"+line+"</p>"
        text.append(line)
text = "<div>"+(''.join(text))+"</div>"

with open("static/nietzsche.txt", "r", encoding="utf-8") as f:
    textComplete = f.read()
textComplete = textComplete[15025:-1054]
model = Ngram(textComplete, 3)

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')

@app.route("/nietzsche")
def nietzsche():
    return render_template("nietzsche.html", quote=model.generate(5))

@app.route('/cv/<theme>')
def cv(theme):
    posts = [post for post in activities if post[0] == f"{theme}"]
    #return str(posts)
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("\W--([A-Za-z\_\-À-ÿ]+)--\W", fr"<a href='/subject/\1'> \1 </a>", post[6])
    return render_template('cv.html', posts = posts, theme=theme)

@app.route('/subject/<activity>')
def subject(activity):
    #Selects either organisation or  title
    theme = [post[0] for post in activities if post[1] == f"{activity}" or post[2] == f"{activity}"][0]
    posts = [post for post in activities if post[0] == f"{theme}"]
    #return str(posts)
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("\W--([A-Za-z\_\-À-ÿ]+)--\W", fr"<a href='/subject/\1'> \1 </a>", post[6])
    return render_template('cv.html', posts = posts, theme=theme)


@app.route('/projet')
def project():
    return make_response(render_template('projet.html', text=text))

if __name__ == '__main__':
   app.run()    