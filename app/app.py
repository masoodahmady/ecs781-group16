from flask import Flask, jsonify, json, request
from flask_sqlalchemy import SQLAlchemy
from pycoingecko import CoinGeckoAPI
import dateparser
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class BuyingRecord(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    transaction_date = db.Column('transaction_date', db.DateTime)
    coingecko_id = db.Column('coingecko_id', db.String)
    symbol = db.Column('symbol', db.String)
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
    coingecko_id = db.Column('coingecko_id', db.String)
    symbol = db.Column('symbol', db.String)
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
    # TODO: Calculate current portfolio position by deducting sold amount from buying records
    pass
    
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
    
# Create a buying record
@app.route('/buy', methods=['POST'])
def create_buy_record():
    if not request.json or not 'coin_id' in request.json or \
    not 'amount' in request.json or not 'price_usd' in request.json:
        missing = []
        for x in ['coin_id', 'amount', 'price_usd']:
            if x not in request.json:
                missing.append(x)
        
        missing_input = ', '.join(missing)
        return jsonify({'error': f'missing input: {missing_input}'}), 400
    
    symbol = coin_id_to_symbol(request.json['coin_id'])

    if 'transaction_date' not in request.json:
        transaction_date = datetime.now()
    else:
        transaction_date = dateparser.parse(request.json['transaction_date'])


    new_records = BuyingRecord(
        coingecko_id=request.json['coin_id'],
        transaction_date=transaction_date,
        symbol=symbol,
        amount=request.json['amount'],
        price_usd=request.json['price_usd']
    )

    db.session.add(new_records)
    db.session.commit()

    return jsonify({'message': str(result) }), 201

# Create a selling reocrd
@app.route('/sell', methods=['POST'])
def create_sell_record():
    pass

# Read a buying record
@app.route('/buy/<record_id>', methods=['GET'])
def get_buy_record(record_id):
    pass

# Read a selling record
@app.route('/sell/<record_id>', methods=['GET'])
def get_sell_record(record_id):
    pass

# Update a buying record
@app.route('/buy', methods=['PUT'])
def update_buy_record():
    pass

# Update a selling record 
@app.route('/sell', methods=['PUT'])
def update_sell_record():
    pass

# Delete a buying record
@app.route('/buy/<record_id>', methods=['DELETE'])
def delete_buy_record():
    pass

# Update a selling record
@app.route('/sell/<record_id>', methods=['DELETE'])
def delete_sell_record():
    pass



if __name__ == "__main__":
    #app.run(ssl_context=('adhoc'))
    app.run()
