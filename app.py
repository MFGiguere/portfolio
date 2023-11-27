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

with open("static/data/nietzsche.txt", "r", encoding="utf-8") as f:
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
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("(\W)__([A-Za-z\sÀ-ÿ-·']+)__(\W)", fr"\1<a href='/subject/\2'>\2</a>\3", post[6])
    return render_template('cv.html', posts = posts, theme=theme)

@app.route('/subject/<activity>')
def subject(activity):
    #Selects either organisation or  title
    theme = [post[0] for post in activities if post[1].split("'")[0] == f"{activity}" or post[2] == f"{activity}"][0]
    posts = [post for post in activities if post[0] == f"{theme}"]
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("(\W)__([A-Za-z\sÀ-ÿ-·']+)__(\W)", fr"\1<a href='/subject/\2'>\2</a>\3", post[6])
        if post[1] == f"{activity}" or post[2] == f"{activity}":
            activity = post[1][0:20]
    return render_template('cv.html', posts = posts, theme=theme, activity = activity)


@app.route('/projet/<theme>')
def project(theme):
    text = []
    try: 
        with open(f'static/texts/{theme}.txt', encoding='utf-8') as f:
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
        title = theme
    except:
        with open(f'static/texts/abstract.txt', encoding='utf-8') as f:
            lines = (line.rstrip() for line in f) 
            lines = list(line for line in lines if line)
            for line in lines:
                line = """<p class="lead my-3">"""+line+"</p>"
                text.append(line)
        text = (''.join(text))
        title = "Résumé"
    return make_response(render_template('projet.html', text=text, title=title))

if __name__ == '__main__':
   app.run()    