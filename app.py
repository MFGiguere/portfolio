"""
source venv/Scripts/activate
export FLASK_DEBUG=1
flask run
"""

from flask import Flask, render_template, make_response
import csv, re, os
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

def load():
    """
    Load all csv files from static into data as their name
    """
    d = {}
    directory = os.getcwd()
    static = os.path.join(directory,"static")
    for file in os.listdir(static):
        if file.endswith(".csv"):
            with open(f"{static}/{file}", 'r', encoding='utf-8') as csvfile:
                name = os.path.basename(file).split(".")[0]
                spamreader = csv.DictReader(csvfile, delimiter=";", quotechar='|')
                print(spamreader)
                #next(spamreader, None)
                rows = []
                for row in spamreader:
                    rows.append(row)
                print(rows)
                d[name] = rows
    return d

data = load()

data["skills"].sort(key=lambda x: int(x["Years"]), reverse=True)
data["communications"].sort(key=lambda x: x["Date"], reverse=True)
data["experiences"].sort(key=lambda x: x["StartDate"], reverse=True)


app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')

@app.route("/nietzsche")
def nietzsche():
    return render_template("nietzsche.html", quote=model.generate(5))

@app.route('/portfolio/<theme>')
def portfolio(theme):
    posts = [post for post in activities if post[0] == f"{theme}"]
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("(\W)__([A-Za-z\sÀ-ÿ-·'«»]+)__(\W)", fr"\1<a href='/subject/\2'>\2</a>\3", post[6])
    return render_template('portfolio.html', posts = posts, theme=theme)

@app.route('/resume')
def newresume():
    emplois = [post for post in data["experiences"] if post["Theme"] == "emplois"]
    return render_template('resume.html', data=data, emplois = emplois)

@app.route('/subject/<activity>')
def subject(activity):
    #Selects either organisation or  title
    theme = [post[0] for post in activities if post[1].split("'")[0] == f"{activity}" or post[2] == f"{activity}"][0]
    posts = [post for post in activities if post[0] == f"{theme}"]
    for idx, post in enumerate(posts):
        posts[idx][6] = re.sub("(\W)__([A-Za-z\sÀ-ÿ-·']+)__(\W)", fr"\1<a href='/subject/\2'>\2</a>\3", post[6])
        if post[1] == f"{activity}" or post[2] == f"{activity}":
            activity = post[1][0:20]
    return render_template('portfolio.html', posts = posts, theme=theme, activity = activity)


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