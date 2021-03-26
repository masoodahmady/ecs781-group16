from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from pycoingecko import CoinGeckoAPI
import dateparser
from datetime import datetime
import pymysql
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
dbpass = os.environ['SQLALCHEMY_DATABASE_URI_PASSWORD']
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://mydb_user:{dbpass}@database-2.c7dbcqwktl7s.us-east-1.rds.amazonaws.com/mydb"
db = SQLAlchemy(app)

class BuyingRecord(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    transaction_date = db.Column('transaction_date', db.DateTime)
    coingecko_id = db.Column('coingecko_id', db.String(32))
    symbol = db.Column('symbol', db.String(8))
    amount = db.Column('amount', db.Float)
    price_usd = db.Column('price_usd', db.Float)
    
    def __repr__(self):
        return {
            'id': self.id,
            'transaction_date': self.transaction_date,
            'coingecko_id': self.coingecko_id,
            'symbol': self.symbol,
            'amount': self.amount,
            'price_usd': self.price_usd
        }

class SellingRecord(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    transaction_date = db.Column('transaction_date', db.DateTime)
    coingecko_id = db.Column('coingecko_id', db.String(32))
    symbol = db.Column('symbol', db.String(8))
    amount = db.Column('amount', db.Float)
    price_usd = db.Column('price_usd', db.Float)
    
    def __repr__(self):
        return {
            'id': self.id,
            'transaction_date': self.transaction_date,
            'coingecko_id': self.coingecko_id,
            'symbol': self.symbol,
            'amount': self.amount,
            'price_usd': self.price_usd
        }

db.create_all()

def coin_id_to_symbol(coin_id):
    coingecko = CoinGeckoAPI()
    
    data = coingecko.get_coin_by_id(coin_id,
                                    localization=False,
                                    tickers=False,
                                    market_data=False,
                                    community_data=False,
                                    developer_data=False,
                                    sparkline=False)
    return data['symbol'].upper()

@app.route("/")
def hello():
    return "Hello World!"

# Get the latest price of a given coin
@app.route('/coins/<coin_id>', methods=['GET'])
def get_coin_by_id(coin_id):
    coingecko = CoinGeckoAPI()
    data = coingecko.get_price(coin_id, 'usd')
    
    if 'error' in data:
        return data, 404
    else:
        return data
    
# Get current portfolio position
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    # Calculate current portfolio position by deducting sold amount from buying records
    coins = {}
    for row in BuyingRecord.query.all():
        if row.coingecko_id not in coins:
            coins[row.coingecko_id] = {
                'amount': row.amount,
                'cost_usd': row.amount * row.price_usd,
                'unit_cost_usd': row.price_usd,
                'symbol': row.symbol
            }
        else:
            coins[row.coingecko_id]['amount'] = \
                coins[row.coingecko_id]['amount'] + row.amount
            coins[row.coingecko_id]['cost_usd'] = \
                coins[row.coingecko_id]['cost_usd'] + \
                (row.amount * row.price_usd)
            coins[row.coingecko_id]['unit_cost_usd'] = \
                coins[row.coingecko_id]['cost_usd'] / \
                coins[row.coingecko_id]['amount']
    
    for row in SellingRecord.query.all():
        if row.coingecko_id not in coins:
            coins[row.coingecko_id] = {
                'amount': -row.amount,
                'cost_usd': -row.amount * row.price_usd,
                'unit_cost_usd': row.price_usd,
                'symbol': row.symbol
            }
        else:
            coins[row.coingecko_id]['amount'] = \
                coins[row.coingecko_id]['amount'] - row.amount
            coins[row.coingecko_id]['cost_usd'] = \
                coins[row.coingecko_id]['cost_usd'] - \
                (row.amount * row.price_usd)
            coins[row.coingecko_id]['unit_cost_usd'] = \
                abs(coins[row.coingecko_id]['cost_usd'] /
                    coins[row.coingecko_id]['amount'])
    
    coingecko = CoinGeckoAPI()
    for k, v in coins.items():
        coin_current_price = coingecko.get_price(k, 'usd')
        coins[k]['current_price_usd'] = coin_current_price[k]['usd']
        coins[k]['current_value_usd'] = coin_current_price[k]['usd'] * \
            coins[k]['amount']
        
    return coins, 201

@app.route('/buy', methods=['GET'])
def get_buy_records():

    data = []
    for row in BuyingRecord.query.all():
        data.append({
            'id': row.id,
            'coingecko_id': row.coingecko_id,
            'symbol': row.symbol,
            'amount': row.amount,
            'price_usd': row.price_usd
        })
    return jsonify(data), 201
    
@app.route('/sell', methods=['GET'])
def get_sell_records():
    # TODO: create a method similar to get_buy_records()
    # to return selling records
    pass
    
# Create a buying record
@app.route('/buy', methods=['POST'])
def create_buy_record():
    
    # 1. Check whether required parameters are supplied in JSON request
    if not request.json or not 'coin_id' in request.json or \
    not 'amount' in request.json or not 'price_usd' in request.json:
        missing = []
        for x in ['coin_id', 'amount', 'price_usd']:
            if x not in request.json:
                missing.append(x)
        
        missing_input = ', '.join(missing)
        return jsonify({'error': f'missing input: {missing_input}'}), 400
    
    # Get the coin symbol using CoinGecko API
    symbol = coin_id_to_symbol(request.json['coin_id'])

    # If transaction_date is not supplied, assumed transaction_date = now
    # Otherwise parse a datetime object from string
    if 'transaction_date' not in request.json:
        transaction_date = datetime.now()
    else:
        transaction_date = dateparser.parse(request.json['transaction_date'])

    # Insert a new buying record into the database
    new_records = BuyingRecord(
        coingecko_id=request.json['coin_id'],
        transaction_date=transaction_date,
        symbol=symbol,
        amount=request.json['amount'],
        price_usd=request.json['price_usd']
    )

    db.session.add(new_records)
    db.session.commit()

    return jsonify({'message': 'success'}), 201

# Create a selling reocrd
@app.route('/sell', methods=['POST'])
def create_sell_record():
    # 1. Check whether required parameters are supplied in JSON request
    if not request.json or not 'coin_id' in request.json or \
            not 'amount' in request.json or not 'price_usd' in request.json:
        missing = []
        for x in ['coin_id', 'amount', 'price_usd']:
            if x not in request.json:
                missing.append(x)

        missing_input = ', '.join(missing)
        return jsonify({'error': f'missing input: {missing_input}'}), 400
    
    # 2. Check whether the current position (all bought - all sold) is 
    #    greater than the selling amount
    coin_bought = 0.0
    coin_sold = 0.0
    
    for row in BuyingRecord.query.filter_by(coingecko_id=request.json['coin_id']).all():
        coin_bought = coin_bought + row.amount
        
    for row in SellingRecord.query.filter_by(coingecko_id=request.json['coin_id']).all():
        coin_sold = coin_sold + row.amount
        
    if coin_bought - coin_sold < float(request.json['amount']):
        return jsonify({'error': 'there is not enough coin to sell'}), 400
    
    # 3. Insert a selling record if there are enough coins to sell.
    #    Otherwise return an error.
        # Get the coin symbol using CoinGecko API
    symbol = coin_id_to_symbol(request.json['coin_id'])

    # If transaction_date is not supplied, assumed transaction_date = now
    # Otherwise parse a datetime object from string
    if 'transaction_date' not in request.json:
        transaction_date = datetime.now()
    else:
        transaction_date = dateparser.parse(request.json['transaction_date'])

    # Insert a new buying record into the database
    new_records = SellingRecord(
        coingecko_id=request.json['coin_id'],
        transaction_date=transaction_date,
        symbol=symbol,
        amount=request.json['amount'],
        price_usd=request.json['price_usd']
    )

    db.session.add(new_records)
    db.session.commit()

    return jsonify({'message': 'success'}), 201

# Read a buying record
@app.route('/buy/<record_id>', methods=['GET'])
def get_buy_record(record_id):
    # TODO: Retrieve the buying record of the given ID
    pass

# Read a selling record
@app.route('/sell/<record_id>', methods=['GET'])
def get_sell_record(record_id):
    # TODO: Retrieve the selling record of the given ID
    pass

# Update a buying record
@app.route('/buy/<record_id>', methods=['PUT'])
def update_buy_record(record_id):
    # TODO: Check if the given record_id exists, if not return an error.
    
    # TODO: Update the record of the given record_id
    pass

# Update a selling record 
@app.route('/sell/<record_id>', methods=['PUT'])
def update_sell_record(record_id):
    # TODO: Check if the given record_id exists, if not return an error.

    # TODO: Update the record of the given record_id
    pass

# Delete a buying record
@app.route('/buy/<record_id>', methods=['DELETE'])
def delete_buy_record():
    # TODO: Check if the given record_id exists, if not return an error.

    # TODO: Delete the record of the given record_id
    pass

# Update a selling record
@app.route('/sell/<record_id>', methods=['DELETE'])
def delete_sell_record():
    # TODO: Check if the given record_id exists, if not return an error.

    # TODO: Delete the record of the given record_id
    pass



if __name__ == "__main__":
    app.run(ssl_context=('adhoc'))
    #app.run()
