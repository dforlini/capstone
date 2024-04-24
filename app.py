from flask import Flask, render_template, request, redirect, session, url_for, flash
from dotenv import load_dotenv
import os
from extentions import db, bcrypt
from pokemon_api import get_pokemon_cards
from utils import login_required
from models import User, CollectionItem, Deck, DeckItem

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'ANGELA'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt.init_app(app)


load_dotenv()
api_key = os.getenv('POKEMON_TCG_API_KEY')



@app.route('/')
def welcome():
    return render_template('welcome.html', hide_nav=True)    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Successfully Registered!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/main')
def main():
    if 'username' in session:
        return render_template('main.html', username=session['username']) 
    return redirect(url_for('login'))

@app.route('/pokemon_cards', methods=['GET', 'POST'])
@login_required
def pokemon_cards():
    query = request.args.get('query', '')
    cards = get_pokemon_cards(api_key, query)
    if cards:
        return render_template('pokemon_cards.html', cards=cards.get('data', []), query=query)
    else:
        flash('Error: Could not fetch data from the Pokémon TCG API')
        return redirect(url_for('main'))
    
@app.route('/add_to_collection/<card_id>', methods=['POST'])
@login_required
def add_to_collection(card_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    new_item = CollectionItem(user_id=session['user_id'], card_id=card_id)
    db.session.add(new_item)
    db.session.commit()
    flash('Card added to your collection!')
    return redirect(url_for('pokemon_cards'))

@app.route('/collection')
@login_required
def view_collection():
    user_id = session['user_id']
    collection_items = CollectionItem.query.filter_by(user_id=user_id).all()
    # Fetch card details from the Pokémon API or cache based on the card IDs in collection_items
    return render_template('collection.html', collection_items=collection_items)

@app.route('/deck_builder', methods=['GET', 'POST'])
@login_required
def deckbuilder():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_deck = Deck(user_id=session['user_id'], name=name, description=description)
        db.session.add(new_deck)
        db.session.commit()
        flash('New deck created!')
        return redirect(url_for('view_decks'))
    return render_template('deckbuilder.html')

@app.route('/decks')
@login_required
def view_decks():
    user_id = session['user_id']
    decks = Deck.query.filter_by(user_id=user_id).all()
    return render_template('decks.html', decks=decks)

@app.route('/add_card_to_deck/<int:deck_id>/<string:card_id>', methods=['POST'])
@login_required
def add_card_to_deck(deck_id, card_id):
    # Ensure the deck belongs to the current user to prevent unauthorized additions
    deck = Deck.query.filter_by(id=deck_id, user_id=session['user_id']).first()
    if deck:
        new_deck_item = DeckItem(deck_id=deck_id, card_id=card_id)
        db.session.add(new_deck_item)
        db.session.commit()
        flash('Card added to deck successfully!')
    else:
        flash('Deck not found or access denied.', 'error')
    return redirect(url_for('view_deck', deck_id=deck_id))

@app.route('/remove_card_from_deck/<int:deck_item_id>', methods=['POST'])
@login_required
def remove_card_from_deck(deck_item_id):
    # Join DeckItem with Deck and filter by the current user's ID and deck_item_id
    deck_item = DeckItem.query.join(Deck, DeckItem.deck_id == Deck.id).filter(DeckItem.id == deck_item_id, Deck.user_id == session['user_id']).first()
    if deck_item:
        db.session.delete(deck_item)
        db.session.commit()
        flash('Card removed from deck successfully!')
        return redirect(url_for('view_deck', deck_id=deck_item.deck_id))
    else:
        flash('Deck item not found or access denied.', 'error')
        # Redirect to a generic page if deck_item is not found, as deck_id is unknown in this case
        return redirect(url_for('main'))

@app.route('/view_deck/<int:deck_id>')
@login_required
def view_deck(deck_id):
    
    deck = Deck.query.filter_by(id=deck_id, user_id=session['user_id']).first_or_404()
    deck_items = DeckItem.query.filter_by(deck_id=deck_id).all()
    cards_details = [get_pokemon_cards(card.card_id) for card in deck_items] 
    
    return render_template('view_deck.html', deck=deck, deck_items=cards_details)    

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)       
                