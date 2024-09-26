from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


# Video Model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)


# Create the database tables
with app.app_context():
    db.create_all()


# Home route (Login/Sign up page)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = username
                if username == "kingyork" and password == "1116":
                    return redirect(url_for('admin'))
                return redirect(url_for('main'))
            else:
                return "Invalid credentials. Please try again."
        elif 'signup' in request.form:
            username = request.form['new_username']
            password = request.form['new_password']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return "Username already exists. Please choose a different one."
            else:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('index'))
    return render_template("index.html")


# Main page to show available videos
@app.route("/main")
def main():
    videos = Video.query.order_by(Video.date_uploaded.desc()).all()
    return render_template("main.html", videos=videos)


# Admin panel to upload videos
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if 'username' not in session or session['username'] != 'kingyork':
        return redirect(url_for('index'))

    if request.method == "POST":
        title = request.form['title']
        url = request.form['url']

        # Extract Google Drive file ID and convert it into an embeddable link
        file_id = url.split("/d/")[1].split("/")[0]
        embed_url = f"https://drive.google.com/file/d/{file_id}/preview"

        new_video = Video(title=title, url=embed_url)
        db.session.add(new_video)
        db.session.commit()
        return redirect(url_for('main'))

    return render_template("admin.html")


# Admin panel to upload videos
@app.route("/admin_page", methods=["GET", "POST"])
def admin_page():
    # admin functionality
    pass

    if 'username' not in session or session['username'] != 'kingyork':
        return redirect(url_for('index'))

    if request.method == "POST":
        title = request.form['title']
        url = request.form['url']
        new_video = Video(title=title, url=url)
        db.session.add(new_video)
        db.session.commit()
        return redirect(url_for('main'))

    return render_template("admin.html")


# Logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
