from extentions import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) #store hashed password
    collections = db.relationship('CollectionItem', backref='user', lazy=True)
    decks = db.relationship('Deck', backref='user', lazy=True)
    
    def set_password(self, password):
        # Use Flask-Bcrypt to generate a password hash
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        # Use Flask-Bcrypt to check the password against the stored hash
        return bcrypt.check_password_hash(self.password_hash, password)
    
class CollectionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.String(120), nullable=False)  

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))

class DeckItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    card_id = db.Column(db.String(120), nullable=False)     