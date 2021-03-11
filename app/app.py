from flask import Flask, jsonify, json, request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Float
from pycoingecko import CoinGeckoAPI

engine = create_engine('sqlite:///app.db', echo=True)
app = Flask(__name__)

def get_buying_table():
    conn = engine.connect()
    meta = MetaData()

    buying_history = Table(
        'buying_history', meta,
        Column('id', Integer, primary_key=True),
        Column('coingecko_id', String),
        Column('symbol', String),
        Column('amount', Float),
        Column('price_usd', Float)
    )

    meta.create_all(engine, checkfirst=True)
    return conn, buying_history

def get_selling_table():
    conn = engine.connect()
    meta = MetaData()

    selling_history = Table(
        'selling_history', meta,
        Column('id', Integer, primary_key=True),
        Column('coingecko_id', String),
        Column('symbol', String),
        Column('amount', Float),
        Column('price_usd', Float)
    )

    meta.create_all(engine, checkfirst=True)
    return conn, selling_history

def init_database():
    get_buying_table()
    get_selling_table()

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

    conn, buying_history = get_buying_table()
    ins = sqlalchemy.insert(buying_history).values(
        coingecko_id=request.json['coin_id'],
        symbol=symbol,
        amount=request.json['amount'],
        price_usd=request.json['price_usd']
        )
    result = conn.execute(ins)

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
    init_database()
    app.run()
