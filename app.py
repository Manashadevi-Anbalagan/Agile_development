from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campus.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["GET", "POST"])
def report():

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        location = request.form["location"]
        description = request.form["description"]

        count = Issue.query.count() + 1
        issue_id = f"KCET-{datetime.now().year}-{count:04d}"

        new_issue = Issue(
            issue_id=issue_id,
            title=title,
            category=category,
            location=location,
            description=description
        )

        db.session.add(new_issue)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("report.html")


@app.route("/dashboard")
def dashboard():

    issues = Issue.query.order_by(
        Issue.created_at.desc()
    ).all()

    return render_template("dashboard.html", issues=issues)


@app.route("/update/<int:issue_id>", methods=["POST"])
def update(issue_id):

    issue = Issue.query.get_or_404(issue_id)

    issue.status = request.form["status"]

    db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/delete/<int:issue_id>", methods=["POST"])
def delete(issue_id):

    issue = Issue.query.get_or_404(issue_id)

    db.session.delete(issue)
    db.session.commit()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
