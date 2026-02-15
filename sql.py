from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

with open("sqluri.txt", "r") as file:
    app.config["SQLALCHEMY_DATABASE_URI"] = file.read().strip()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Relationships(db.Model):
    __tablename__ = "relationships"  # match your table name exactly

    user_id = db.Column(db.String(255), primary_key=True)
    friend_id = db.Column(db.String(255), primary_key=True)
    friend_desc = db.Column(db.String(255))

def exists_context(my_user, other_user) -> bool:
    with app.app_context():
        entry = Relationships.query.filter_by(
            user_id=my_user,
            friend_id=other_user
        ).first()
        print(entry)
        print(entry is not None)
        return entry is not None

def get_context(my_user, other_user):
    with app.app_context():
        entry = Relationships.query.filter_by(
            user_id=my_user,
            friend_id=other_user
        ).first()
        return entry.friend_desc

def update_context(my_user, other_user, new_context):
    with app.app_context():
        entry = Relationships.query.filter_by(
            user_id=my_user,
            friend_id=other_user
        ).first()

        if entry:
            entry.friend_desc = new_context
            db.session.commit()

        if not entry:
                new_entry = Relationships(
                    user_id=my_user,
                    friend_id=other_user,
                    friend_desc=new_context
                )

                db.session.add(new_entry)
                db.session.commit()

@app.route("/")
def home():
    return "Database connected!"
