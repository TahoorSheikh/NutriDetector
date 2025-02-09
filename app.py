# Imports
from flask import Flask, render_template, redirect, request,url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cohere
from Tkey import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)

# My App
app = Flask(__name__)
Scss(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

# Data Class - row of data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    #ai_reply = db.Column(db.String(100))
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"


# Routes to Webpages
# homepage
@app.route("/",methods=["POST","GET"])
def index():
  
    # Add a task
    if request.method == "POST":
        current_task = request.form['content']
        responce = co.generate(model="command",prompt=current_task,max_tokens=50)
        ai_text = responce.generations[0].text.strip()
        new_task = MyTask(content=f"Input: {current_task},\nOutput: {ai_text}")
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"

    # See all current task
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/index', methods=['GET', 'POST'])
def target_page():
    if request.method == 'POST':
        # Handle the button action here
        return render_template('index.html')  # Replace with your template
    return redirect(url_for('home'))  # Redirect if accessed via GET

@app.route('/info_page', methods=['GET', 'POST'])
def info_page():
    return render_template('infoPage.html')

if __name__ == '__main__':
    app.run(debug=True)


# Delete an item
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR:{e}"



# Runner and Debugger
if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)