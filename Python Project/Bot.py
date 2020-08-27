from datetime import datetime, timedelta
import requests
import json


class Bot:

    def __init__(self):
        """Bot Initialization"""
        # dictionary initialization for data saving
        self.data = {}
        # integer for the number of credit used.
        self.credit_count = 0
        # url definition for requests
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        # header definition for requests
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': ''
        }

    def load_key(self, file_name):
        """Load the personal key for CoinMarketCap API from a text file"""
        # return variables initialization
        key = None
        error = 0
        try:
            # try to open the file and read the key from it. Then close it
            with open(file_name, 'r') as file:
                key = file.read()
        except:
            # if an exception accours, catch it and save its class
            error = 1
        # header update for requests
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': key
        }
        return error

    def get_key(self):
        """Load the personal key for CoinMarketCap API from a text file"""
        # return variables initialization
        data = None
        error = 0
        try:
            # try to open the file and read the key from it. Then close it
            with open('key.txt', 'r') as file:
                data = file.read()
        except Exception as e:
            # if an exception accours, catch it and save its class
            error = 1
            data = e.__class__
        return error, data

    def reset_data(self):
        """Reset data stored in the class instance"""
        self.data = {}
        self.credit_count = 0

    def save_data(self):
        """Save collected data to a json file"""
        # if there are data to save
        if self.data:
            # than, file name definition and error variable initialization
            file_name = str(datetime.now().date()) + '.json'
            error = 0
            try:
                # try to open the file and write data in it. Then close it
                with open(file_name, 'w') as file:
                    json.dump(self.data, file)
            except Exception as e:
                # if an exception accours, catch it and save its class
                error = 1
                file_name = e.__class__
        else:
            # else return error flag and message
            file_name = 'Nessun dato da salvare'
            error = 1
        return error, file_name

    def load_data(self):
        """Load last data from a json file"""
        # get yesterday's file name
        file_name = str((datetime.now() - timedelta(days=1)).date()) + '.json'
        # variable initialization
        data = None
        error = 0
        try:
            # try to open the file and read the data from it. Then close it
            with open(file_name, 'r') as file:
                data = json.load(file)
        except Exception as e:
            # if an exception accours, catch it and save its class
            error = 1
            data = e.__class__
        return error, data

    def make_request(self, params):
        """API request with errors and exceptions handling"""
        # variable initialization
        error = None
        data = None
        try:
            # try to do a request to the server
            req = requests.get(url=self.url, params=params,
                               headers=self.headers).json()
        except Exception as e:
            # if an exception accours, catch it and save its class
            error = 1
            data = e.__class__
        else:
            # otherwise, get the number of credits used for the request
            self.credit_count += req['status']['credit_count']
            # get the error code
            error = req['status']['error_code']
            # if there is an error
            if error:
                # then save also its message
                data = req['status']['error_message']
            else:
                # else save the data
                data = req['data']
        return error, data

    def top_volume(self):
        """First answer: find the cypto with highest volume"""
        # parameter definition for the request
        params = {
            'start': '1',
            'limit': '1',
            'sort_dir': 'desc',
            'sort': 'volume_24h',
            'convert': 'USD'
        }
        # request with error handling
        error, data = self.make_request(params)
        # if there is not an error
        if not error:
            # fetch name, symbol and volume of the crypto
            data = {
                'name': data[0]['name'],
                'symbol': data[0]['symbol'],
                'volume': data[0]['quote']['USD']['volume_24h']
            }
            # and save it in the instance
            self.data[1] = data
        return error, data

    def headtail_perc_change(self):
        """Second answer: find the best and worst crypto by last 24h percent change"""
        # variable initialization and parameter definition for the request
        data = {}
        params = {
            'start': '1',
            'limit': '100',
            'sort': 'percent_change_24h',
            'convert': 'USD'
        }
        # for cryptos in the head and tail of the list by percent change
        for field, sort_dir in zip(['head', 'tail'], ['desc', 'asc']):
            # define the proper sort direction
            params['sort_dir'] = sort_dir
            # request with error handling
            error, temp = self.make_request(params)
            # if there is an error
            if error:
                # return error flag and its description
                return error, temp
            # else define the data structure
            data[field] = []
            # for the first 10 items in the list
            for item in temp[:10]:
                # fetch name, symbol and percent change, then append the tuple
                name = item['name']
                symbol = item['symbol']
                change = item['quote']['USD']['percent_change_24h']
                data[field].append((name, symbol, change))
        # save the dictionary in the instance
        self.data[2] = data
        return error, data

    def topN_cap_price(self, N=20):
        """Third answer: find the total unit price of the first 20 crypto by capitalization"""
        # parameters definition for the request
        params = {
            'start': '1',
            'limit': str(N),
            'sort_dir': 'desc',
            'sort': 'market_cap',
            'convert': 'USD'
        }
        # request with error handling
        error, data = self.make_request(params)
        # if there is not an error
        if not error:
            # variables initialization
            ids = []
            names = []
            total = 0
            # for the items in the list
            for item in data:
                # add its price to the total and append names and ids to relative lists
                total += item['quote']['USD']['price']
                names.append(item['name'])
                ids.append(item['id'])
            # save everything as a dictionary
            data = {
                'total': total,
                'names': names,
                'ids': ids
            }
            # and save it in the instance
            self.data[3] = data
        return error, data

    def topV_vol_price(self, V=76000000):
        """Forth answer: find the total unit price of all cryptos with 24h volume >= V"""
        # variables initialization
        total = 0
        error = 0
        start = 1
        limit = 100
        volume = V
        # while the volume of the crypto is above the threshold and there is not an error
        while((volume >= V) and (not error)):
            # parameters definition for the request
            params = {
                'start': str(start),
                'limit': str(limit),
                'sort_dir': 'desc',
                'sort': 'volume_24h',
                'convert': 'USD'
            }
            # request with error handling
            error, data = self.make_request(params)
            # if there is not an error
            if not error:
                # initialize variables and volume evaluation for the first crypto
                index = 0
                length = len(data)
                volume = data[index]['quote']['USD']['volume_24h']
                # while the volume of the crypto is above the threshold
                # and the index is lower than the total lenght of the data vector
                while((volume >= V) and (index < length)):
                    # add its price to the total and increase the index
                    total += data[index]['quote']['USD']['price']
                    index += 1
                    # evaluate the volume of the next crypto
                    volume = data[index % length]['quote']['USD']['volume_24h']
                    # NOTE: when index == lenght we obtain 0 from the modulo operator which is wrong
                    # however, we will not use this volume for the while condition on index
                # data preparation for return and saving in the instance
                data = total
                self.data[4] = data
                # if we have not found all the crypto with volume above the threshold,
                # change the starting point of the request and fetch more data
                start += limit
        return error, data

    def check_profit(self):
        """Fifth answer: check the profit that you would have if you buyed cryptos of the Third answer"""
        # load the data from yesterday
        error, old_data = self.load_data()
        # if there is an error
        if error:
            # then return the error and its message
            return error, old_data
        # else fetch the old total amount and the its of the cryptos used
        old_total = old_data["3"]['total']
        old_ids = [item for item in old_data["3"]['ids']]
        # variables initializations
        count = 0
        start = 1
        limit = 100
        new_total = 0
        # while we used less than 20 crypto for the evaluation and there is not an error
        while((count < 20) and (not error)):
            # parameters definition for the request
            params = {
                'start': str(start),
                'limit': str(limit),
                'sort_dir': 'desc',
                'sort': 'volume_24h',
                'convert': 'USD'
            }
            # request with error handling
            error, data = self.make_request(params)
            # if there is not an error
            if not error:
                # initialize the index
                index = 0
                # while we used less than 20 crypto for the evaluation
                # and the index is lower than the total lenght of the data vector
                while((count < 20) and (index < len(data))):
                    # get crypto id
                    new_id = data[index]['id']
                    # if there is that id in the ids used yesterday
                    if new_id in old_ids:
                        # add crypto's price to the total
                        new_total += data[index]['quote']['USD']['price']
                        # increase the counter
                        count += 1
                        # and, also, remove that id for efficiency
                        old_ids.remove(new_id)
                    # increase the index
                    index += 1
                # increase the request starting point for further requests (if needed)
                start += limit
                # data preparation for return and saving in the instance
                data = (new_total - old_total) / old_total * 100
                self.data[5] = data
        return error, data
