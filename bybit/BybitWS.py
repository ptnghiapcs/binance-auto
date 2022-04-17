import time
import hmac
import json
import logging
import threading
import requests
import websocket

from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor

class WebSocket:
    """
    Connector for Bybit's WebSocket API.
    """

    def __init__(self, endpoint, api_key=None, api_secret=None,
                 subscriptions=None, logging_level=logging.INFO,
                 max_data_length=200, ping_interval=30, ping_timeout=10,
                 restart_on_error=True, purge_on_fetch=True,
                 trim_data=True):
        """
        Initializes the websocket session.
        :param endpoint: Required parameter. The endpoint of the remote
            websocket.
        :param api_key: Your API key. Required for authenticated endpoints.
            Defaults to None.
        :param api_secret: Your API secret key. Required for authenticated
            endpoints. Defaults to None.
        :param subscriptions: A list of desired topics to subscribe to. See API
            documentation for more information. Defaults to an empty list, which
            will raise an error.
        :param logging_level: The logging level of the built-in logger. Defaults
            to logging.INFO. Options are CRITICAL (50), ERROR (40),
            WARNING (30), INFO (20), DEBUG (10), or NOTSET (0).
        :param max_data_length: The maximum number of rows for the stored
            dataset. A smaller number will prevent performance or memory issues.
        :param ping_interval: The number of seconds between each automated ping.
        :param ping_timeout: The number of seconds to wait for 'pong' before an
            Exception is raised.
        :param restart_on_error: Whether or not the connection should restart on
            error.
        :param purge_on_fetch: Whether or not stored data should be purged each
            fetch. For example, if the user subscribes to the 'trade' topic, and
            fetches, should the data show all trade history up to the maximum
            length or only get the data since the last fetch?
        :param trim_data: Decide whether the returning data should be
            trimmed to only provide the data value.
        :returns: WebSocket session.
        """

        if not subscriptions:
            raise Exception('Subscription list cannot be empty!')

        # Require symbol on 'trade' topic.
        if 'trade' in subscriptions:
            raise Exception('\'trade\' requires a ticker, e.g. '
                            '\'trade.BTCUSD\'.')

        # Require currency on 'insurance' topic.
        if 'insurance' in subscriptions:
            raise Exception('\'insurance\' requires a currency, e.g. '
                            '\'insurance.BTC\'.')

        # Require timeframe and ticker on 'klineV2' topic.
        if 'klineV2' in subscriptions:
            raise Exception('\'klineV2\' requires a timeframe and ticker, e.g.'
                            ' \'klineV2.5.BTCUSD\'.')

        # set websocket name for logging purposes
        self.wsName = 'Authenticated' if api_key else 'Non-Authenticated'

        # Setup logger.
        self.logger = logging.getLogger(__name__)

        if len(logging.root.handlers) == 0:
            # no handler on root logger set -> we add handler just for this logger to not mess with custom logic from outside
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                   datefmt='%Y-%m-%d %H:%M:%S'
                                                   )
                                 )
            handler.setLevel(logging_level)
            self.logger.addHandler(handler)

        self.logger.debug(f'Initializing {self.wsName} WebSocket.')

        # Ensure authentication for private topics.
        if any(i in subscriptions for i in [
            'position',
            'execution',
            'order',
            'stop_order',
            'wallet'
        ]) and api_key is None:
            raise PermissionError('You must be authorized to use '
                                  'private topics!')

        # Set endpoint.
        self.endpoint = endpoint

        # Set API keys.
        self.api_key = api_key
        self.api_secret = api_secret

        # Set topic subscriptions for WebSocket.
        self.subscriptions = subscriptions
        self.max_length = max_data_length

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Other optional data handling settings.
        self.handle_error = restart_on_error
        self.purge = purge_on_fetch
        self.trim = trim_data

        # Set initial state, initialize dictionary and connnect.
        self._reset()
        self._connect(self.endpoint)

    def fetch(self, topic):
        """
        Fetches data from the subscribed topic.
        :param topic: Required parameter. The subscribed topic to poll.
        :returns: Filtered data as dict.
        """

        # If topic isn't a string.
        if not isinstance(topic, str):
            self.logger.error('Topic argument must be a string.')
            return

        # If the topic given isn't in the initial subscribed list.
        if topic not in self.subscriptions:
            self.logger.error(f'You aren\'t subscribed to the {topic} topic.')
            return

        # Pop all trade or execution data on each poll.
        # dont pop order or stop_order data as we will lose valuable state
        if topic.startswith((
                'trade',
                'execution'
        )) and not topic.startswith('orderBook'):
            data = self.data[topic].copy()
            if self.purge:
                self.data[topic] = []
            return data
        else:
            try:
                return self.data[topic]
            except KeyError:
                return []

    def ping(self):
        """
        Pings the remote server to test the connection. The status of the
        connection can be monitored using ws.ping().
        """

        self.ws.send(json.dumps({'op': 'ping'}))

    def exit(self):
        """
        Closes the websocket connection.
        """

        self.ws.close()
        while self.ws.sock:
            continue
        self.exited = True

    def _auth(self):
        """
        Authorize websocket connection.
        """

        # Generate expires.
        expires = int((time.time() + 1) * 1000)

        # Generate signature.
        _val = f'GET/realtime{expires}'
        signature = str(hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(_val, 'utf-8'), digestmod='sha256'
        ).hexdigest())

        # Authenticate with API.
        self.ws.send(
            json.dumps({
                'op': 'auth',
                'args': [self.api_key, expires, signature]
            })
        )

    def _connect(self, url):
        """
        Open websocket in a thread.
        """

        self.ws = websocket.WebSocketApp(
            url=url,
            on_message=lambda ws, msg: self._on_message(msg),
            on_close=self._on_close(),
            on_open=self._on_open(),
            on_error=lambda ws, err: self._on_error(err)
        )

        # Setup the thread running WebSocketApp.
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_timeout
        ))

        # Configure as daemon; start.
        self.wst.daemon = True
        self.wst.start()

        # Attempt to connect for X seconds.
        retries = 10
        while retries > 0 and (not self.ws.sock or not self.ws.sock.connected):
            retries -= 1
            time.sleep(1)

        # If connection was not successful, raise error.
        if retries <= 0:
            self.exit()
            raise websocket.WebSocketTimeoutException('Connection failed.')

        # If given an api_key, authenticate.
        if self.api_key and self.api_secret:
            self._auth()

        # Check if subscriptions is a list.
        if isinstance(self.subscriptions, str):
            self.subscriptions = [self.subscriptions]

        # Subscribe to the requested topics.
        self.ws.send(
            json.dumps({
                'op': 'subscribe',
                'args': self.subscriptions
            })
        )

        # Initialize the topics.
        for topic in self.subscriptions:
            if topic not in self.data:
                self.data[topic] = {}

    @staticmethod
    def _find_index(source, target, key):
        """
        Find the index in source list of the targeted ID.
        """
        return next(i for i, j in enumerate(source) if j[key] == target[key])

    def _on_message(self, message):
        """
        Parse incoming messages. Similar structure to the
        official WS connector.
        """

        # Load dict of message.
        msg_json = json.loads(message)

        # If 'success' exists
        if 'success' in msg_json:
            if msg_json['success']:

                # If 'request' exists.
                if 'request' in msg_json:

                    # If we get succesful auth, notify user.
                    if msg_json['request']['op'] == 'auth':
                        self.logger.debug('Authorization successful.')
                        self.auth = True

                    # If we get successful subscription, notify user.
                    if msg_json['request']['op'] == 'subscribe':
                        sub = msg_json['request']['args']
                        self.logger.debug(f'Subscription to {sub} successful.')
            else:
                response = msg_json['ret_msg']
                if 'unknown topic' in response:
                    self.logger.error('Couldn\'t subscribe to topic.'
                                      f' Error: {response}.')

                # If we get unsuccesful auth, notify user.
                elif msg_json['request']['op'] == 'auth':
                    self.logger.debug('Authorization failed. Please check your '
                                     'API keys and restart.')

        elif 'topic' in msg_json:

            topic = msg_json['topic']

            # If incoming 'orderbookL2' data.
            if 'orderBook' in topic:

                # Make updates according to delta response.
                if 'delta' in msg_json['type']:

                    # Delete.
                    for entry in msg_json['data']['delete']:
                        index = self._find_index(self.data[topic], entry, 'id')
                        self.data[topic].pop(index)

                    # Update.
                    for entry in msg_json['data']['update']:
                        index = self._find_index(self.data[topic], entry, 'id')
                        self.data[topic][index] = entry

                    # Insert.
                    for entry in msg_json['data']['insert']:
                        self.data[topic].append(entry)

                # Record the initial snapshot.
                elif 'snapshot' in msg_json['type']:
                    if 'order_book' in msg_json['data']:
                        self.data[topic] = msg_json['data']['order_book'] if self.trim else msg_json
                    else:
                        self.data[topic] = msg_json['data'] if self.trim else msg_json
                    #self.data[topic] = msg_json['data']

            # For incoming 'order' and 'stop_order' data.
            elif any(i in topic for i in ['order', 'stop_order']):

                # record incoming data  
                for i in msg_json['data']:
                    try:
                        # update existing entries
                        # temporary workaround for field anomaly in stop_order data
                        ord_id = topic + '_id' if i['symbol'].endswith('USDT') else 'order_id'
                        index = self._find_index(self.data[topic], i, ord_id)
                        self.data[topic][index] = i
                    except StopIteration:
                        # Keep appending or create new list if not already created.
                        try:
                            self.data[topic].append(i)
                        except AttributeError:
                            self.data[topic] = msg_json['data']

            # For incoming 'trade' and 'execution' data.
            elif any(i in topic for i in ['trade', 'execution']):

                # Keep appending or create new list if not already created.
                try:
                    for i in msg_json['data']:
                        self.data[topic].append(i)
                except AttributeError:
                    self.data[topic] = msg_json['data']

                # If list is too long, pop the first entry.
                if len(self.data[topic]) > self.max_length:
                    self.data[topic].pop(0)

            # If incoming 'insurance', 'klineV2', or 'wallet' data.
            elif any(i in topic for i in ['insurance', 'klineV2', 'wallet',
                                          'candle']):

                # Record incoming data.
                self.data[topic] = msg_json['data'][0] if self.trim else msg_json

            # If incoming 'instrument_info' data.
            elif 'instrument_info' in topic:

                # Make updates according to delta response.
                if 'delta' in msg_json['type']:
                    for i in msg_json['data']['update'][0]:
                        self.data[topic][i] = msg_json['data']['update'][0][i]

                # Record the initial snapshot.
                elif 'snapshot' in msg_json['type']:
                    self.data[topic] = msg_json['data'] if self.trim else msg_json

            # If incoming 'position' data.
            elif 'position' in topic:

                # Record incoming position data.
                for p in msg_json['data']:

                    # linear (USDT) positions have Buy|Sell side and
                    # updates contain all USDT positions.
                    # For linear tickers...
                    if p['symbol'].endswith('USDT'):
                        try:
                            self.data[topic][p['symbol']][p['side']] = p
                        # if side key hasn't been created yet...
                        except KeyError:
                            self.data[topic][p['symbol']] = {p['side']: p}

                    # For non-linear tickers...
                    else:
                        self.data[topic][p['symbol']] = p

    def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """

        if not self.exited:
            self.logger.error(f'WebSocket {self.wsName} encountered error: {error}.')
            self.exit()

        # Reconnect.
        if self.handle_error:
            self._reset()
            self._connect(self.endpoint)

    def _on_open(self):
        """
        Log WS open.
        """
        self.logger.debug(f'WebSocket {self.wsName} opened.')

    def _on_close(self):
        """
        Log WS close.
        """
        self.logger.debug(f'WebSocket {self.wsName} closed.')

    def _reset(self):
        """
        Set state booleans and initialize dictionary.
        """
        self.exited = False
        self.auth = False
        self.data = {}