import random
import string
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
db = SQLAlchemy(app)


def now():
    return datetime.now(timezone.utc)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now)
    clicks = db.relationship(
        "Click", backref="url", lazy=True, cascade="all, delete-orphan"
    )


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey("url.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=now)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not Url.query.filter_by(short_code=code).first():
            return code


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original = request.form.get("url", "").strip()
        alias = request.form.get("alias", "").strip()

        if not is_valid_url(original):
            flash("Please enter a valid URL starting with http:// or https://", "error")
            return redirect(url_for("index"))

        if alias:
            if not alias.isalnum() or not 3 <= len(alias) <= 10:
                flash("Alias must be 3-10 letters/numbers only.", "error")
                return redirect(url_for("index"))
            if Url.query.filter_by(short_code=alias).first():
                flash("That alias is already taken.", "error")
                return redirect(url_for("index"))
            code = alias
        else:
            code = generate_code()

        db.session.add(Url(original_url=original, short_code=code))
        db.session.commit()
        flash(f"Short link created: {request.host_url}{code}", "success")
        return redirect(url_for("index"))

    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template("index.html", urls=urls)


@app.route("/<code>")
def redirect_to_url(code):
    url = Url.query.filter_by(short_code=code).first_or_404()
    click = Click(
        url_id=url.id,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        user_agent=(request.user_agent.string or "")[:255],
    )
    db.session.add(click)
    db.session.commit()
    return redirect(url.original_url)


@app.route("/stats/<code>")
def stats(code):
    url = Url.query.filter_by(short_code=code).first_or_404()
    per_day = Counter(c.timestamp.strftime("%Y-%m-%d") for c in url.clicks)
    labels = sorted(per_day)
    values = [per_day[d] for d in labels]
    recent = sorted(url.clicks, key=lambda c: c.timestamp, reverse=True)[:10]
    return render_template(
        "stats.html", url=url, labels=labels, values=values, recent=recent
    )


@app.route("/delete/<code>", methods=["POST"])
def delete(code):
    url = Url.query.filter_by(short_code=code).first_or_404()
    db.session.delete(url)
    db.session.commit()
    flash("Link deleted.", "success")
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
