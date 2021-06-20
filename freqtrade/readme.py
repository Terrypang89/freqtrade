
main.py ->
	get_parsed_arg()

commands/arguments.py ->
	get_parsed_arg ->
		_build_subcommands ->
			trade_cmd.set_defaults(func=start_trading)

commands/trade_commands.py ->
	start_trading ->
		worker = Worker(args)

worker.py ->
	_init ->
		self._config = Configuration(self._args, None).get_config()
		self.freqtrade = FreqtradeBot(self._config)

freqtradebot.py ->
	process ->
		self.strategy.analyze(self.active_pair_whitelist)

strategy/interface.py
	def analyze(self, pairs: List[str]) -> None: ->
		def analyze_pair(self, pair: str) -> None: ->
			def _analyze_ticker_internal(self, dataframe: DataFrame, metadata: dict) -> DataFrame: ->
				def analyze_ticker(self, dataframe: DataFrame, metadata: dict) -> DataFrame: ->
					def advise_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame: ->
						populate_indicators
					def advise_buy(self, dataframe: DataFrame, metadata: dict) -> DataFrame: ->
						populate_buy_trend
					def advise_sell(self, dataframe: DataFrame, metadata: dict) -> DataFrame: ->
						populate_sell_trend

strategy/interface.py ->
with self._sell_lock:
	def exit_positions(self, trades: List[Any]) -> int:
		def handle_stoploss_on_exchange(self, trade: Trade) -> bool:
			def create_stoploss_order(self, trade: Trade, stop_price: float) -> bool:
				def stoploss(self, pair: str, amount: float, stop_price: float, order_types: Dict) -> Dict:
					order = self._api.create_order(symbol=pair, type=ordertype, side='sell',
		                                           amount=amount, price=stop_price, params=params)
		def handle_trade(self, trade: Trade) -> bool:
			def _check_and_execute_sell(self, trade: Trade, sell_rate: float,
		                                buy: bool, sell: bool) -> bool:
				should_sell = self.strategy.should_sell(
		            trade, sell_rate, datetime.now(timezone.utc), buy, sell,
		            force_stoploss=self.edge.stoploss(trade.pair) if self.edge else 0
		        )
				def execute_sell(self, trade: Trade, limit: float, sell_reason: SellType) -> bool:
					def sell(self, pair: str, ordertype: str, amount: float,
             			rate: float, time_in_force: str = 'gtc') -> Dict:
						return self._api.create_order(pair, ordertype, side,
                                          amount, rate_for_order, params)

if self.get_free_open_trades():
	def enter_positions(self) -> int:
		def create_trade(self, pair: str) -> bool:
			def execute_buy(self, pair: str, stake_amount: float, price: Optional[float] = None,
		                    forcebuy: bool = False) -> bool:
				def buy(self, pair: str, ordertype: str, amount: float,
            			rate: float, time_in_force: str) -> Dict:
					def create_order(self, pair: str, ordertype: str, side: str, amount: float,
                     				rate: float, params: Dict = {}) -> Dict:
						return self._api.create_order(pair, ordertype, side,
                                          amount, rate_for_order, params)

---------------------------------------------------------------------------------

freqtradebot.py ->
	#010
	def process(self) -> None: ->

		# Check whether markets have to be reloaded and reload them when it's needed
        self.exchange.reload_markets()
		# 001 Update closed trades without close fees assigned.
        #Only acts when Orders are in the database, otherwise the last orderid is unknown.
        self.update_closed_trades_without_assigned_fees()

        # Query trades from persistence layer
		# 014 get_open_trades return amount of total opentrade, which has been bought
		# Trade.get_trades(Trade.is_open.is_(True)).all()
        trades = Trade.get_open_trades()

        self.active_pair_whitelist = self._refresh_active_whitelist(trades)

        # Refreshing candles
        self.dataprovider.refresh(self.pairlists.create_pair_list(self.active_pair_whitelist),
                                  self.strategy.informative_pairs())

		strategy_safe_wrapper(self.strategy.bot_loop_start, supress_error=True)()
		# 011 detected, refer to strategy/strategy_wrapper ->
		#		strategy_safe_wrapper(f, message: str = "", default_retval=None, supress_error=False):

		# 012 Analyze all pairs using analyze_pair(). and fill in indicater with buy sell rules set
		self.strategy.analyze(self.active_pair_whitelist)

		with self._sell_lock:
			# 013 Check and handle any timed out open orders or canceled trade
			self.check_handle_timedout()

		with self._sell_lock:
			# 014 get_open_trades return amount of total opentrade, which has been bought
			# Trade.get_trades(Trade.is_open.is_(True)).all()
			trades = Trade.get_open_trades()
			# 015 First process current opened trades (positions) for selling
			# Tries to execute sell orders for open trades (positions)
			self.exit_positions(trades)

		# 016 Then looking for buy opportunities for buying
		#Return the number of free open trades slots or 0 if
        #max number of open trades reached
		# max(0, self.config['max_open_trades'] - len(Trade.get_open_trades()) )
		if self.get_free_open_trades():
			# 017 enter_positions
			self.enter_positions()

		Trade.session.flush()

--------------------------------------------------------------------------------

	# 010
	def update_closed_trades_without_assigned_fees(self):

        #Update closed trades without close fees assigned.
        #Only acts when Orders are in the database, otherwise the last orderid is unknown.

        if self.config['dry_run']:
            # Updating open orders in dry-run does not make sense and will fail.
            return

		#011
        trades: List[Trade] = Trade.get_sold_trades_without_assigned_fees()
        for trade in trades:
			# 013211 Verify if this side (buy / sell) has already been updated
            if not trade.is_open and not trade.fee_updated('sell'):
                # Get sell fee
                order = trade.select_order('sell', False)
                if order:
                    logger.info(f"Updating sell-fee on trade {trade} for order {order.order_id}.")
					# 0132 Common update trade state methods
					self.update_trade_state(trade, order.order_id,
                                            stoploss_order=order.ft_order_side == 'stoploss')

        trades: List[Trade] = Trade.get_open_trades_without_assigned_fees()
        for trade in trades:
			# 013211 Verify if this side (buy / sell) has already been updated
            if trade.is_open and not trade.fee_updated('buy'):
                order = trade.select_order('buy', False)
                if order:
                    logger.info(f"Updating buy-fee on trade {trade} for order {order.order_id}.")
					# 0132 Common update trade state methods
					self.update_trade_state(trade, order.order_id)

--------------------------------------------------------------------------------

	# 011
	@staticmethod
    def get_sold_trades_without_assigned_fees():
        #"""
        #Returns all closed trades which don't have fees set correctly
        #"""
        return Trade.get_trades([Trade.fee_close_currency.is_(None),
                                 Trade.orders.any(),
                                 Trade.is_open.is_(False),
                                 ]).all()

--------------------------------------------------------------------------------

	#017
	# BUY / enter positions / open trades logic and methods
	def enter_positions(self) -> int:

		#Tries to execute buy orders for new trades (positions)

		trades_created = 0
		whitelist = copy.deepcopy(self.active_pair_whitelist)
		# if whitelist shows nothing
		if not whitelist:
			logger.info("Active pair whitelist is empty.")
			return trades_created
		# Remove pairs for currently opened trades from the whitelist
		# 014 get_open_trades return amount of total opentrade, which has been bought
		# Trade.get_trades(Trade.is_open.is_(True)).all()
		for trade in Trade.get_open_trades():
			if trade.pair in whitelist:
				whitelist.remove(trade.pair)
				logger.debug('Ignoring %s in pair whitelist', trade.pair)

		if not whitelist:
			logger.info("No currency pair in active pair whitelist, "
									"but checking to sell open trades.")
			return trades_created
		if PairLocks.is_global_lock():
			lock = PairLocks.get_pair_longest_lock('*')
			if lock:
				self.log_once(f"Global pairlock active until "
								f"{lock.lock_end_time.strftime(constants.DATETIME_PRINT_FORMAT)}. "
								"Not creating new trades.", logger.info)
			else:
				self.log_once("Global pairlock active. Not creating new trades.", logger.info)
			return trades_created
		# Create entity and execute trade for each pair from whitelist
		for pair in whitelist:
			try:
				# 071 Check the implemented trading strategy for buy signals.\
		        #If the pair triggers the buy signal a new trade record gets created
		        #and the buy-order opening the trade gets issued towards the exchange.

				trades_created += self.create_trade(pair)
			except DependencyException as exception:
				logger.warning('Unable to create trade for %s: %s', pair, exception)

		if not trades_created:
			logger.debug("Found no buy signals for whitelisted currencies. Trying again...")

		return trades_created

	--------------------------------------------------------------------------------

	#015
	def exit_positions(self, trades: List[Any]) -> int: ->

	    #Tries to execute sell orders for open trades (positions)

	    trades_closed = 0
	    #check in every trades
		#order_types: Dict = {
	    #    'buy': 'limit',
	    #    'sell': 'limit',
	    #    'stoploss': 'limit',
	    #    'stoploss_on_exchange': False,
	    #    'stoploss_on_exchange_interval': 60,
	    #}
	    for trade in trades:
	        try:
				# 0151 Check if trade is fulfilled in which case the stoploss
				#on exchange should be added immediately if stoploss on exchange
				#is enabled.
	            if (self.strategy.order_types.get('stoploss_on_exchange') and self.handle_stoploss_on_exchange(trade)):
	                trades_closed += 1
	                continue
	            # 0152 Check if we can sell our current pair
				#Sells the current pair if the threshold is reached and updates the trade record.
		        #:return: True if trade has been sold, False otherwise
	            if trade.open_order_id is None and trade.is_open and self.handle_trade(trade):
	                trades_closed += 1

	        except DependencyException as exception:
	            logger.warning('Unable to sell trade %s: %s', trade.pair, exception)

	    # Updating wallets if any trade occured
	    if trades_closed:
	        self.wallets.update()

	    return trades_closed

--------------------------------------------------------------------------------
	# 0151
	def handle_stoploss_on_exchange(self, trade: Trade) -> bool:

        #Check if trade is fulfilled in which case the stoploss
        #on exchange should be added immediately if stoploss on exchange
        #is enabled.

        logger.debug('Handling stoploss on exchange %s ...', trade)

        stoploss_order = None

        try:
            # 01511 First we check if there is already a stoploss on exchange
			# based on trade_id and demanded pair, get stoploss_order from api
            stoploss_order = self.exchange.fetch_stoploss_order(
                trade.stoploss_order_id, trade.pair) if trade.stoploss_order_id else None
        except InvalidOrderException as exception:
            logger.warning('Unable to fetch stoploss order: %s', exception)

        if stoploss_order:
			# 01512 Get all non-closed orders - useful when trying to batch-update orders
            trade.update_order(stoploss_order) # throught cctx update

        # We check if stoploss order is fulfilled
        if stoploss_order and stoploss_order['status'] in ('closed', 'triggered'):
            trade.sell_reason = SellType.STOPLOSS_ON_EXCHANGE.value

			# 0132 update the trade.stoploss_order_id that trade stoposs is met
            self.update_trade_state(trade, trade.stoploss_order_id, stoploss_order,
                                    stoploss_order=True)
            # Lock pair for one candle to prevent immediate rebuys
            self.strategy.lock_pair(trade.pair, datetime.now(timezone.utc),
                                    reason='Auto lock')

			# Sends rpc notification when a sell occured.
            self._notify_sell(trade, "stoploss")
            return True

        if trade.open_order_id or not trade.is_open:
            # Trade has an open Buy or Sell order, Stoploss-handling can't happen in this case
            # as the Amount on the exchange is tied up in another trade.
            # The trade can be closed already (sell-order fill confirmation came in this iteration)
            return False

        # If buy order is fulfilled but there is no stoploss, we add a stoploss on exchange
        if not stoploss_order:
			# 01513 Creates a stoploss order.
        	# depending on order_types.stoploss configuration, uses 'market' or limit order.
            stoploss = self.edge.stoploss(pair=trade.pair) if self.edge else self.strategy.stoploss
            stop_price = trade.open_rate * (1 + stoploss)
			# 01514 Abstracts creating stoploss orders from the logic.
        	#Handles errors and updates the trade database object.
            if self.create_stoploss_order(trade=trade, stop_price=stop_price):
                trade.stoploss_last_update = datetime.utcnow()
                return False

        # If stoploss order is canceled for some reason we add it
        if stoploss_order and stoploss_order['status'] in ('canceled', 'cancelled'):
			# 01514 Abstracts creating stoploss orders from the logic.
        	#Handles errors and updates the trade database object.
            if self.create_stoploss_order(trade=trade, stop_price=trade.stop_loss):
                return False
            else:
                trade.stoploss_order_id = None
                logger.warning('Stoploss order was cancelled, but unable to recreate one.')

        # Finally we check if stoploss on exchange should be moved up because of trailing.
        if stoploss_order and (self.config.get('trailing_stop', False)
                               or self.config.get('use_custom_stoploss', False)):
            # if trailing stoploss is enabled we check if stoploss value has changed
            # in which case we cancel stoploss order and put another one with new
            # value immediately
			# 01515 Check to see if stoploss on exchange should be updated
        	# in case of trailing stoploss on exchange
            self.handle_trailing_stoploss_on_exchange(trade, stoploss_order)

        return False

--------------------------------------------------------------------------------

# 01511
exchange/ftx.py ->
	@retrier(retries=API_FETCH_ORDER_RETRY_COUNT)
    def fetch_stoploss_order(self, order_id: str, pair: str) -> Dict:
        if self._config['dry_run']:
            try:
				# return open order based on order_id
                order = self._dry_run_open_orders[order_id]
                return order
            except KeyError as e:
                # Gracefully handle errors with dry-run orders.
                raise InvalidOrderException(
                    f'Tried to get an invalid dry-run-order (id: {order_id}). Message: {e}') from e
        try:
			# get all the orders by fetch_orders from api, with demanded pair
			# 15111
            orders = self._api.fetch_orders(pair, None, params={'type': 'stop'})

			#get the order from fetch_orders api based on order_id
            order = [order for order in orders if order['id'] == order_id]
			#if order only contain one, then return it
            if len(order) == 1:
                return order[0]
            else:
                raise InvalidOrderException(f"Could not get stoploss order for id {order_id}")

        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Tried to get an invalid order (id: {order_id}). Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not get order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	# 015111
	@retrier(retries=API_FETCH_ORDER_RETRY_COUNT)
	def fetch_order(self, order_id: str, pair: str) -> Dict:
        if self._config['dry_run']:
            try:
                order = self._dry_run_open_orders[order_id]
                return order
            except KeyError as e:
                # Gracefully handle errors with dry-run orders.
                raise InvalidOrderException(
                    f'Tried to get an invalid dry-run-order (id: {order_id}). Message: {e}') from e
        try:
            return self._api.fetch_order(order_id, pair)
        except ccxt.OrderNotFound as e:
            raise RetryableOrderError(
                f'Order not found (pair: {pair} id: {order_id}). Message: {e}') from e
        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Tried to get an invalid order (pair: {pair} id: {order_id}). Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not get order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

# 01512
persistence/models.py ->
	def update_order(self, order: Dict) -> None:
        Order.update_orders(self.orders, order)

	@staticmethod
    def update_orders(orders: List['Order'], order: Dict[str, Any]):
        #Get all non-closed orders - useful when trying to batch-update orders

        if not isinstance(order, dict):
            logger.warning(f"{order} is not a valid response object.")
            return

        filtered_orders = [o for o in orders if o.order_id == order.get('id')]
        if filtered_orders:
            oobj = filtered_orders[0]
			# 015121 Update Order from ccxt response
            oobj.update_from_ccxt_object(order)
        else:
            logger.warning(f"Did not find order for {order}.")

	# 015121
	def update_from_ccxt_object(self, order):
        """
        Update Order from ccxt response
        Only updates if fields are available from ccxt -
        """
        if self.order_id != str(order['id']):
            raise DependencyException("Order-id's don't match")

        self.status = order.get('status', self.status)
        self.symbol = order.get('symbol', self.symbol)
        self.order_type = order.get('type', self.order_type)
        self.side = order.get('side', self.side)
        self.price = order.get('price', self.price)
        self.amount = order.get('amount', self.amount)
        self.filled = order.get('filled', self.filled)
        self.remaining = order.get('remaining', self.remaining)
        self.cost = order.get('cost', self.cost)
        if 'timestamp' in order and order['timestamp'] is not None:
			# convert timestamp to order_date
            self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)

        self.ft_is_open = True
        if self.status in ('closed', 'canceled', 'cancelled'):
            self.ft_is_open = False
            if order.get('filled', 0) > 0:
                self.order_filled_date = arrow.utcnow().datetime
        self.order_update_date = arrow.utcnow().datetime

--------------------------------------------------------------------------------

	# 01513 #Creates a stoploss order.
	#depending on order_types.stoploss configuration, uses 'market' or limit order.
	#Limit orders are defined by having orderPrice set, otherwise a market order is used.

	@retrier(retries=0)
    def stoploss(self, pair: str, amount: float, stop_price: float, order_types: Dict) -> Dict:

        #Creates a stoploss order.
        #depending on order_types.stoploss configuration, uses 'market' or limit order.
        #Limit orders are defined by having orderPrice set, otherwise a market order is used.

        limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
        limit_rate = stop_price * limit_price_pct

        ordertype = "stop"
		# 015131 Returns the price rounded up to the precision the Exchange accepts.
        #Partial Reimplementation of ccxt internal method decimal_to_precision(),
        #which does not support rounding up
        stop_price = self.price_to_precision(pair, stop_price)

        if self._config['dry_run']:
			# 01524231
            dry_order = self.dry_run_order(
                pair, ordertype, "sell", amount, stop_price)
            return dry_order

        try:
            params = self._params.copy()
            if order_types.get('stoploss', 'market') == 'limit':
                # set orderPrice to place limit order, otherwise it's a market order
                params['orderPrice'] = limit_rate
			# 7123 Returns the amount to buy or sell to a precision the Exchange accepts
	        # Reimplementation of ccxt internal methods - ensuring we can test the result is correct
	        # based on our definitions.
            amount = self.amount_to_precision(pair, amount)
			# direct ask api create order
            order = self._api.create_order(symbol=pair, type=ordertype, side='sell',
                                           amount=amount, price=stop_price, params=params)
            logger.info('stoploss order added for %s. '
                        'stop price: %s.', pair, stop_price)
            return order
        except ccxt.InsufficientFunds as e:
            raise InsufficientFundsError(
                f'Insufficient funds to create {ordertype} sell order on market {pair}. '
                f'Tried to create stoploss with amount {amount} at stoploss {stop_price}. '
                f'Message: {e}') from e
        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Could not create {ordertype} sell order on market {pair}. '
                f'Tried to create stoploss with amount {amount} at stoploss {stop_price}. '
                f'Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not place sell order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	# 01514
	@staticmethod
    def parse_from_ccxt_object(order: Dict[str, Any], pair: str, side: str) -> 'Order':
        """
        Parse an order from a ccxt object and return a new order Object.
        """
        o = Order(order_id=str(order['id']), ft_order_side=side, ft_pair=pair)
		# 015121
        o.update_from_ccxt_object(order)
        return o

--------------------------------------------------------------------------------

	# 015131
	def price_to_precision(self, pair: str, price: float) -> float:

        #Returns the price rounded up to the precision the Exchange accepts.
        #Partial Reimplementation of ccxt internal method decimal_to_precision(),
        #which does not support rounding up
        #TODO: If ccxt supports ROUND_UP for decimal_to_precision(), we could remove this and
        #align with amount_to_precision().
        #Rounds up

        if self.markets[pair]['precision']['price']:
            # price = float(decimal_to_precision(price, rounding_mode=ROUND,
            #                                    precision=self.markets[pair]['precision']['price'],
            #                                    counting_mode=self.precisionMode,
            #                                    ))
            if self.precisionMode == TICK_SIZE:
                precision = self.markets[pair]['precision']['price']
                missing = price % precision
                if missing != 0:
                    price = price - missing + precision
            else:
                symbol_prec = self.markets[pair]['precision']['price']
                big_price = price * pow(10, symbol_prec)
                price = ceil(big_price) / pow(10, symbol_prec)
        return price

--------------------------------------------------------------------------------

	# 01514
	def create_stoploss_order(self, trade: Trade, stop_price: float) -> bool:

        #Abstracts creating stoploss orders from the logic.
        #Handles errors and updates the trade database object.
        #Force-sells the pair (using EmergencySell reason) in case of Problems creating the order.
        #:return: True if the order succeeded, and False in case of problems.

        try:
			# creates a stoploss order.
        	# The precise ordertype is determined by the order_types dict or exchange default.
        	# Since ccxt does not unify stoploss-limit orders yet, this needs to be implemented in each
        	# exchange's subclass.
			# 01513 #Creates a stoploss order.
			#depending on order_types.stoploss configuration, uses 'market' or limit order.
			#Limit orders are defined by having orderPrice set, otherwise a market order is used.
            stoploss_order = self.exchange.stoploss(pair=trade.pair, amount=trade.amount,
                                                    stop_price=stop_price,
                                                    order_types=self.strategy.order_types)

			# Parse an order from a ccxt object and return a new order Object.
        	# o = Order(order_id=str(order['id']), ft_order_side=side, ft_pair=pair)
			# o.update_from_ccxt_object(order)
        	# return o
			# 01514
            order_obj = Order.parse_from_ccxt_object(stoploss_order, trade.pair, 'stoploss')
            trade.orders.append(order_obj)
            trade.stoploss_order_id = str(stoploss_order['id'])
            return True
        except InsufficientFundsError as e:
            logger.warning(f"Unable to place stoploss order {e}.")
            # Try to figure out what went wrong
            self.handle_insufficient_funds(trade)

        except InvalidOrderException as e:
            trade.stoploss_order_id = None
            logger.error(f'Unable to place a stoploss order on exchange. {e}')
            logger.warning('Selling the trade forcefully')

            self.execute_sell(trade, trade.stop_loss, sell_reason=SellType.EMERGENCY_SELL)

        except ExchangeError:
            trade.stoploss_order_id = None
            logger.exception('Unable to place a stoploss order on exchange.')
        return False

--------------------------------------------------------------------------------

	# 01515
	def handle_trailing_stoploss_on_exchange(self, trade: Trade, order: dict) -> None:

        #Check to see if stoploss on exchange should be updated
        #in case of trailing stoploss on exchange
        #:param Trade: Corresponding Trade
        #:param order: Current on exchange stoploss order
        #:return: None

		# Verify stop_loss against stoploss-order value (limit or price)
        #Returns True if adjustment is necessary.
		# raise OperationalException(f"stoploss is not implemented for {self.name}.")
        if self.exchange.stoploss_adjust(trade.stop_loss, order):
            # we check if the update is neccesary
            update_beat = self.strategy.order_types.get('stoploss_on_exchange_interval', 60)
            if (datetime.utcnow() - trade.stoploss_last_update).total_seconds() >= update_beat:
                # cancelling the current stoploss on exchange first
                logger.info(f"Cancelling current stoploss on exchange for pair {trade.pair} "
                            f"(orderid:{order['id']}) in order to add another one ...")
                try:
					# 015151
                    co = self.exchange.cancel_stoploss_order(order['id'], trade.pair)
                    trade.update_order(co)
                except InvalidOrderException:
                    logger.exception(f"Could not cancel stoploss order {order['id']} "
                                     f"for pair {trade.pair}")

                # Create new stoploss order
                if not self.create_stoploss_order(trade=trade, stop_price=trade.stop_loss):
                    logger.warning(f"Could not create trailing stoploss order "
                                   f"for pair {trade.pair}.")

--------------------------------------------------------------------------------

	# 015151
	@retrier
    def cancel_stoploss_order(self, order_id: str, pair: str) -> Dict:
        if self._config['dry_run']:
            return {}
        try:
            return self._api.cancel_order(order_id, pair, params={'type': 'stop'})
        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Could not cancel order. Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not cancel order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	# 0152
	def handle_trade(self, trade: Trade) -> bool:

        #Sells the current pair if the threshold is reached and updates the trade record.
        #:return: True if trade has been sold, False otherwise

        if not trade.is_open:
            raise DependencyException(f'Attempt to handle closed trade: {trade}')

        logger.debug('Handling %s ...', trade)

        (buy, sell) = (False, False)

		# get ask strategy
        config_ask_strategy = self.config.get('ask_strategy', {})

        if (config_ask_strategy.get('use_sell_signal', True) or
                config_ask_strategy.get('ignore_roi_if_buy_signal', False)):
			# 01521 :param pair: pair to get the data for
        	# :param timeframe: timeframe to get data for
        	# :return: Tuple of (Analyzed Dataframe, lastrefreshed) for the requested pair / timeframe combination.
            #Returns empty dataframe and Epoch 0 (1970-01-01) if no dataframe was cached.
            analyzed_df, _ = self.dataprovider.get_analyzed_dataframe(trade.pair,
                                                                      self.strategy.timeframe)
			# 01522 Calculates current signal based based on the buy / sell columns of the dataframe.
        	# Used by Bot to get the signal to buy or sell
        	# :param pair: pair in format ANT/BTC
        	# :param timeframe: timeframe to use
        	# :param dataframe: Analyzed dataframe to get signal from.
        	# :return: (Buy, Sell) A bool-tuple indicating buy/sell sign
            (buy, sell) = self.strategy.get_signal(trade.pair, self.strategy.timeframe, analyzed_df)

        if config_ask_strategy.get('use_order_book', False):
            order_book_min = config_ask_strategy.get('order_book_min', 1)
            order_book_max = config_ask_strategy.get('order_book_max', 1)
            logger.debug(f'Using order book between {order_book_min} and {order_book_max} '
                         f'for selling {trade.pair}...')
			# 01523 Helper generator to query orderbook in loop (used for early sell-order placing)
            order_book = self._order_book_gen(trade.pair, f"{config_ask_strategy['price_side']}s",
                                              order_book_min=order_book_min,
                                              order_book_max=order_book_max)
            for i in range(order_book_min, order_book_max + 1):
                try:
                    sell_rate = next(order_book)
                except (IndexError, KeyError) as e:
                    logger.warning(
                        f"Sell Price at location {i} from orderbook could not be determined."
                    )
                    raise PricingError from e
                logger.debug(f"  order book {config_ask_strategy['price_side']} top {i}: "
                             f"{sell_rate:0.8f}")
                # Assign sell-rate to cache - otherwise sell-rate is never updated in the cache,
                # resulting in outdated RPC messages
                self._sell_rate_cache[trade.pair] = sell_rate
				# 015241 This function evaluates if one of the conditions required to trigger a sell
		        # has been reached, which can either be a stop-loss, ROI or sell-signal.
                if self._check_and_execute_sell(trade, sell_rate, buy, sell):
                    return True

        else:
            logger.debug('checking sell')
			# 01525 Get sell rate - either using ticker bid or first bid based on orderbook
        	#The orderbook portion is only used for rpc messaging, which would otherwise fail
        	#for BitMex (has no bid/ask in fetch_ticker)
        	#or remain static in any other case since it's not updating.
            sell_rate = self.get_sell_rate(trade.pair, True)
			# 015241 This function evaluates if one of the conditions required to trigger a sell
	        # has been reached, which can either be a stop-loss, ROI or sell-signal.
            if self._check_and_execute_sell(trade, sell_rate, buy, sell):
                return True

        logger.debug('Found no sell signal for %s.', trade)
        return False

--------------------------------------------------------------------------------

	# 01521
data/dataprovider.py ->
	def get_analyzed_dataframe(self, pair: str, timeframe: str) -> Tuple[DataFrame, datetime]:

        #:param pair: pair to get the data for
        #:param timeframe: timeframe to get data for
        #:return: Tuple of (Analyzed Dataframe, lastrefreshed) for the requested pair / timeframe
        #    combination.
        #    Returns empty dataframe and Epoch 0 (1970-01-01) if no dataframe was cached.

        if (pair, timeframe) in self.__cached_pairs:
            return self.__cached_pairs[(pair, timeframe)]
        else:

            return (DataFrame(), datetime.fromtimestamp(0, tz=timezone.utc))

--------------------------------------------------------------------------------

	# 01522
	def get_signal(self, pair: str, timeframe: str, dataframe: DataFrame) -> Tuple[bool, bool]:

        #Calculates current signal based based on the buy / sell columns of the dataframe.
        #Used by Bot to get the signal to buy or sell
        #:param pair: pair in format ANT/BTC
        #:param timeframe: timeframe to use
        #:param dataframe: Analyzed dataframe to get signal from.
        #:return: (Buy, Sell) A bool-tuple indicating buy/sell signal

        if not isinstance(dataframe, DataFrame) or dataframe.empty:
            logger.warning(f'Empty candle (OHLCV) data for pair {pair}')
            return False, False

        latest_date = dataframe['date'].max()
        latest = dataframe.loc[dataframe['date'] == latest_date].iloc[-1]
        # Explicitly convert to arrow object to ensure the below comparison does not fail
        latest_date = arrow.get(latest_date)

        # Check if dataframe is out of date
        timeframe_minutes = timeframe_to_minutes(timeframe)
        offset = self.config.get('exchange', {}).get('outdated_offset', 5)
        if latest_date < (arrow.utcnow().shift(minutes=-(timeframe_minutes * 2 + offset))):
            logger.warning(
                'Outdated history for pair %s. Last tick is %s minutes old',
                pair, int((arrow.utcnow() - latest_date).total_seconds() // 60)
            )
            return False, False
		# check buy and sell
        (buy, sell) = latest[SignalType.BUY.value] == 1, latest[SignalType.SELL.value] == 1
        logger.debug('trigger: %s (pair=%s) buy=%s sell=%s',
                     latest['date'], pair, str(buy), str(sell))
        timeframe_seconds = timeframe_to_seconds(timeframe)
		# 015221
        if self.ignore_expired_candle(latest_date=latest_date,
                                      current_time=datetime.now(timezone.utc),
                                      timeframe_seconds=timeframe_seconds,
                                      buy=buy):
            return False, sell
        return buy, sell

--------------------------------------------------------------------------------

	# 015221
	def ignore_expired_candle(self, latest_date: datetime, current_time: datetime,
                              timeframe_seconds: int, buy: bool):
        if self.ignore_buying_expired_candle_after and buy:
            time_delta = current_time - (latest_date + timedelta(seconds=timeframe_seconds))
            return time_delta.total_seconds() > self.ignore_buying_expired_candle_after
        else:
            return False

--------------------------------------------------------------------------------

	# 01523
	def _order_book_gen(self, pair: str, side: str, order_book_max: int = 1,
                        order_book_min: int = 1):

        #Helper generator to query orderbook in loop (used for early sell-order placing)

        order_book = self.exchange.fetch_l2_order_book(pair, order_book_max)
        for i in range(order_book_min, order_book_max + 1):
            yield order_book[side][i - 1][0]

--------------------------------------------------------------------------------

	# 01524
	def _check_and_execute_sell(self, trade: Trade, sell_rate: float,
                                buy: bool, sell: bool) -> bool:

        #Check and execute sell
        # 015241 This function evaluates if one of the conditions required to trigger a sell
        # has been reached, which can either be a stop-loss, ROI or sell-signal.
        should_sell = self.strategy.should_sell(
            trade, sell_rate, datetime.now(timezone.utc), buy, sell,
			# 01513 #Creates a stoploss order.
			#depending on order_types.stoploss configuration, uses 'market' or limit order.
			#Limit orders are defined by having orderPrice set, otherwise a market order is used.
            force_stoploss=self.edge.stoploss(trade.pair) if self.edge else 0
        )

        if should_sell.sell_flag:
            logger.info(f'Executing Sell for {trade.pair}. Reason: {should_sell.sell_type}')
			# 015242 Executes a limit sell for the given trade and limit
			self.execute_sell(trade, sell_rate, should_sell.sell_type)
            return True
        return False

--------------------------------------------------------------------------------

	# 015241
	def should_sell(self, trade: Trade, rate: float, date: datetime, buy: bool,
                    sell: bool, low: float = None, high: float = None,
                    force_stoploss: float = 0) -> SellCheckTuple:

        #This function evaluates if one of the conditions required to trigger a sell
        #has been reached, which can either be a stop-loss, ROI or sell-signal.
        #:param low: Only used during backtesting to simulate stoploss
        #:param high: Only used during backtesting, to simulate ROI
        #:param force_stoploss: Externally provided stoploss
        #:return: True if trade should be sold, False otherwise

        # Set current rate to low for backtesting sell
        current_rate = low or rate
		# 0152411 Calculates the profit as ratio (including fee).
        current_profit = trade.calc_profit_ratio(current_rate)
		# Adjust the max_rate and min_rate.
        # self.max_rate = max(current_price, self.max_rate or self.open_rate)
        # self.min_rate = min(current_price, self.min_rate or self.open_rate)
        trade.adjust_min_max_rates(high or current_rate)
		# 0152412 Based on current profit of the trade and configured (trailing) stoploss,
        # decides to sell or not
        stoplossflag = self.stop_loss_reached(current_rate=current_rate, trade=trade,
                                              current_time=date, current_profit=current_profit,
                                              force_stoploss=force_stoploss, high=high)

        # Set current rate to high for backtesting sell
        current_rate = high or rate
		# 0152411 Calculates the profit as ratio (including fee)
        current_profit = trade.calc_profit_ratio(current_rate)
        ask_strategy = self.config.get('ask_strategy', {})

        # if buy signal and ignore_roi is set, we don't need to evaluate min_roi.
		#def min_roi_reached_entry(self, trade_dur: int) -> Tuple[Optional[int], Optional[float]]:
		#	roi_list = list(filter(lambda x: x <= trade_dur, self.minimal_roi.keys()))
        #	if not roi_list:
        #    	return None, None
        #	roi_entry = max(roi_list)
        #	return roi_entry, self.minimal_roi[roi_entry]
        roi_reached = (not (buy and ask_strategy.get('ignore_roi_if_buy_signal', False))
                       and self.min_roi_reached(trade=trade, current_profit=current_profit,
                                                current_time=date))

        if (ask_strategy.get('sell_profit_only', False)
                and current_profit <= ask_strategy.get('sell_profit_offset', 0)):
            # sell_profit_only and profit doesn't reach the offset - ignore sell signal
            sell_signal = False
        else:
            sell_signal = sell and not buy and ask_strategy.get('use_sell_signal', True)
            # TODO: return here if sell-signal should be favored over ROI

        # Start evaluations
        # Sequence:
        # ROI (if not stoploss)
        # Sell-signal
        # Stoploss
        if roi_reached and stoplossflag.sell_type != SellType.STOP_LOSS:
            logger.debug(f"{trade.pair} - Required profit reached. sell_flag=True, "
                         f"sell_type=SellType.ROI")
			# 01524122 NamedTuple for Sell type + reason
            return SellCheckTuple(sell_flag=True, sell_type=SellType.ROI)

        if sell_signal:
            logger.debug(f"{trade.pair} - Sell signal received. sell_flag=True, "
                         f"sell_type=SellType.SELL_SIGNAL")
			# 01524122 NamedTuple for Sell type + reason
            return SellCheckTuple(sell_flag=True, sell_type=SellType.SELL_SIGNAL)

        if stoplossflag.sell_flag:

            logger.debug(f"{trade.pair} - Stoploss hit. sell_flag=True, "
                         f"sell_type={stoplossflag.sell_type}")
            return stoplossflag

        # This one is noisy, commented out...
        # logger.debug(f"{trade.pair} - No sell signal. sell_flag=False")\
		# 01524122 NamedTuple for Sell type + reason
        return SellCheckTuple(sell_flag=False, sell_type=SellType.NONE)

--------------------------------------------------------------------------------

	#0152411
	def calc_profit_ratio(self, rate: Optional[float] = None,
                          fee: Optional[float] = None) -> float:

        #Calculates the profit as ratio (including fee).
        #:param rate: rate to compare with (optional).
        #    If rate is not set self.close_rate will be used
        #:param fee: fee to use on the close rate (optional).
        #:return: profit ratio as float
		# 01524111 Calculate the close_rate including fee
        close_trade_value = self.calc_close_trade_value(
            rate=(rate or self.close_rate),
            fee=(fee or self.fee_close)
        )
        profit_ratio = (close_trade_value / self.open_trade_value) - 1
        return float(f"{profit_ratio:.8f}")

--------------------------------------------------------------------------------

	# 01524111
	def calc_close_trade_value(self, rate: Optional[float] = None,
                               fee: Optional[float] = None) -> float:

        #Calculate the close_rate including fee
        #:param fee: fee to use on the close rate (optional).
        #    If rate is not set self.fee will be used
        #:param rate: rate to compare with (optional).
        #    If rate is not set self.close_rate will be used
        #:return: Price in BTC of the open trade

        if rate is None and not self.close_rate:
            return 0.0

        sell_trade = Decimal(self.amount) * Decimal(rate or self.close_rate)  # type: ignore
        fees = sell_trade * Decimal(fee or self.fee_close)
        return float(sell_trade - fees)

--------------------------------------------------------------------------------

	# 0152412
	def stop_loss_reached(self, current_rate: float, trade: Trade,
                          current_time: datetime, current_profit: float,
                          force_stoploss: float, high: float = None) -> SellCheckTuple:

        #Based on current profit of the trade and configured (trailing) stoploss,
        #decides to sell or not
        #:param current_profit: current profit as ratio

        stop_loss_value = force_stoploss if force_stoploss else self.stoploss

        # Initiate stoploss with open_rate. Does nothing if stoploss is already set.
		# 01524121 This adjusts the stop loss to it's most recently observed setting
        trade.adjust_stop_loss(trade.open_rate, stop_loss_value, initial=True)

        if self.use_custom_stoploss:
			#Custom stoploss logic, returning the new distance relative to current_rate (as ratio).
        	#e.g. returning -0.05 would create a stoploss 5% below current_rate.
        	#The custom stoploss can never be below self.stoploss, which serves as a hard maximum loss.
        	#For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/
        	#When not implemented by a strategy, returns the initial stoploss value
        	#Only called when use_custom_stoploss is set to True.
            stop_loss_value = strategy_safe_wrapper(self.custom_stoploss, default_retval=None
                                                    )(pair=trade.pair, trade=trade,
                                                      current_time=current_time,
                                                      current_rate=current_rate,
                                                      current_profit=current_profit)
            # Sanity check - error cases will return None
            if stop_loss_value:
                # logger.info(f"{trade.pair} {stop_loss_value=} {current_profit=}")
				# 01524121 This adjusts the stop loss to it's most recently observed setting
                trade.adjust_stop_loss(current_rate, stop_loss_value)
            else:
                logger.warning("CustomStoploss function did not return valid stoploss")

        if self.trailing_stop:
            # trailing stoploss handling
            sl_offset = self.trailing_stop_positive_offset

            # Make sure current_profit is calculated using high for backtesting.
			# 0152411` Calculates the profit as ratio (including fee).
            high_profit = current_profit if not high else trade.calc_profit_ratio(high)

            # Don't update stoploss if trailing_only_offset_is_reached is true.
            if not (self.trailing_only_offset_is_reached and high_profit < sl_offset):
                # Specific handling for trailing_stop_positive
                if self.trailing_stop_positive is not None and high_profit > sl_offset:
                    stop_loss_value = self.trailing_stop_positive
                    logger.debug(f"{trade.pair} - Using positive stoploss: {stop_loss_value} "
                                 f"offset: {sl_offset:.4g} profit: {current_profit:.4f}%")
				# 01524121 This adjusts the stop loss to it's most recently observed setting
                trade.adjust_stop_loss(high or current_rate, stop_loss_value)

        # evaluate if the stoploss was hit if stoploss is not on exchange
        # in Dry-Run, this handles stoploss logic as well, as the logic will not be different to
        # regular stoploss handling.
        if ((trade.stop_loss >= current_rate) and
                (not self.order_types.get('stoploss_on_exchange') or self.config['dry_run'])):

            sell_type = SellType.STOP_LOSS

            # If initial stoploss is not the same as current one then it is trailing.
            if trade.initial_stop_loss != trade.stop_loss:
                sell_type = SellType.TRAILING_STOP_LOSS
                logger.debug(
                    f"{trade.pair} - HIT STOP: current price at {current_rate:.6f}, "
                    f"stoploss is {trade.stop_loss:.6f}, "
                    f"initial stoploss was at {trade.initial_stop_loss:.6f}, "
                    f"trade opened at {trade.open_rate:.6f}")
                logger.debug(f"{trade.pair} - Trailing stop saved "
                             f"{trade.stop_loss - trade.initial_stop_loss:.6f}")
			# 01524122 NamedTuple for Sell type + reason
            return SellCheckTuple(sell_flag=True, sell_type=sell_type)
		# 01524122 NamedTuple for Sell type + reason
        return SellCheckTuple(sell_flag=False, sell_type=SellType.NONE)

--------------------------------------------------------------------------------

	# 01524121
	def adjust_stop_loss(self, current_price: float, stoploss: float,
                         initial: bool = False) -> None:

        #This adjusts the stop loss to it's most recently observed setting
        #:param current_price: Current rate the asset is traded
        #:param stoploss: Stoploss as factor (sample -0.05 -> -5% below current price).
        #:param initial: Called to initiate stop_loss.
        #    Skips everything if self.stop_loss is already set.

        if initial and not (self.stop_loss is None or self.stop_loss == 0):
            # Don't modify if called with initial and nothing to do
            return

        new_loss = float(current_price * (1 - abs(stoploss)))

        # no stop loss assigned yet
        if not self.stop_loss:
            logger.debug(f"{self.pair} - Assigning new stoploss...")
			# 015241211 Assign new stop value
            self._set_new_stoploss(new_loss, stoploss)
            self.initial_stop_loss = new_loss
            self.initial_stop_loss_pct = -1 * abs(stoploss)

        # evaluate if the stop loss needs to be updated
        else:
            if new_loss > self.stop_loss:  # stop losses only walk up, never down!
                logger.debug(f"{self.pair} - Adjusting stoploss...")
				# 015241211 Assign new stop value
                self._set_new_stoploss(new_loss, stoploss)
            else:
                logger.debug(f"{self.pair} - Keeping current stoploss...")

        logger.debug(
            f"{self.pair} - Stoploss adjusted. current_price={current_price:.8f}, "
            f"open_rate={self.open_rate:.8f}, max_rate={self.max_rate:.8f}, "
            f"initial_stop_loss={self.initial_stop_loss:.8f}, "
            f"stop_loss={self.stop_loss:.8f}. "
            f"Trailing stoploss saved us: "
            f"{float(self.stop_loss) - float(self.initial_stop_loss):.8f}.")

--------------------------------------------------------------------------------

	# 015241211
	def _set_new_stoploss(self, new_loss: float, stoploss: float):
        #Assign new stop value
        self.stop_loss = new_loss
        self.stop_loss_pct = -1 * abs(stoploss)
        self.stoploss_last_update = datetime.utcnow()

--------------------------------------------------------------------------------

	# 01524122
	class SellCheckTuple(NamedTuple):

    #NamedTuple for Sell type + reason

    sell_flag: bool
    sell_type: SellType

--------------------------------------------------------------------------------

	# 015242
	def execute_sell(self, trade: Trade, limit: float, sell_reason: SellType) -> bool:

        #Executes a limit sell for the given trade and limit
        #:param trade: Trade instance
        #:param limit: limit rate for the sell order
        #:param sellreason: Reason the sell was triggered
        #:return: True if it succeeds (supported) False (not supported)

        sell_type = 'sell'
        if sell_reason in (SellType.STOP_LOSS, SellType.TRAILING_STOP_LOSS):
            sell_type = 'stoploss'

        # if stoploss is on exchange and we are on dry_run mode,
        # we consider the sell price stop price
        if self.config['dry_run'] and sell_type == 'stoploss' \
           and self.strategy.order_types['stoploss_on_exchange']:
            limit = trade.stop_loss

        # First cancelling stoploss on exchange ...
        if self.strategy.order_types.get('stoploss_on_exchange') and trade.stoploss_order_id:
            try:
				# 0152421
                self.exchange.cancel_stoploss_order(trade.stoploss_order_id, trade.pair)
            except InvalidOrderException:
                logger.exception(f"Could not cancel stoploss order {trade.stoploss_order_id}")

        order_type = self.strategy.order_types[sell_type]
        if sell_reason == SellType.EMERGENCY_SELL:
            # Emergency sells (default to market!)
            order_type = self.strategy.order_types.get("emergencysell", "market")
        if sell_reason == SellType.FORCE_SELL:
            # Force sells (default to the sell_type defined in the strategy,
            # but we allow this value to be changed)
            order_type = self.strategy.order_types.get("forcesell", order_type)

		# 0152422 Get sellable amount.
        #Should be trade.amount - but will fall back to the available amount if necessary.
        ##This should cover cases where get_real_amount() was not able to update the amount
        #for whatever reason.
        amount = self._safe_sell_amount(trade.pair, trade.amount)
        time_in_force = self.strategy.order_time_in_force['sell']

		# Called right before placing a regular sell order.
        #Timing for this function is critical, so avoid doing heavy computations or
        #network requests in this method.
        if not strategy_safe_wrapper(self.strategy.confirm_trade_exit, default_retval=True)(
                pair=trade.pair, trade=trade, order_type=order_type, amount=amount, rate=limit,
                time_in_force=time_in_force,
                sell_reason=sell_reason.value):
            logger.info(f"User requested abortion of selling {trade.pair}")
            return False

        try:
            # 0152423 Execute sell and update trade record
            order = self.exchange.sell(pair=trade.pair,
                                       ordertype=order_type,
                                       amount=amount, rate=limit,
                                       time_in_force=time_in_force
                                       )
        except InsufficientFundsError as e:
            logger.warning(f"Unable to place order {e}.")
            # Try to figure out what went wrong
			# 0152424 Determine if we ever opened a sell order for this trade.
        	#If not, try update buy fees - otherwise "refind" the open order we obviously lost.
            self.handle_insufficient_funds(trade)
            return False

        order_obj = Order.parse_from_ccxt_object(order, trade.pair, 'sell')
        trade.orders.append(order_obj)

        trade.open_order_id = order['id']
        trade.sell_order_status = ''
        trade.close_rate_requested = limit
        trade.sell_reason = sell_reason.value
        # In case of market sell orders the order can be closed immediately
        if order.get('status', 'unknown') == 'closed':
			# 0132 Common update trade state methods
            self.update_trade_state(trade, trade.open_order_id, order)
        Trade.session.flush()

        # Lock pair for one candle to prevent immediate rebuys
        self.strategy.lock_pair(trade.pair, datetime.now(timezone.utc),
                                reason='Auto lock')

        self._notify_sell(trade, order_type)

        return True

--------------------------------------------------------------------------------

	# 0152421
	@retrier
    def cancel_stoploss_order(self, order_id: str, pair: str) -> Dict:
        if self._config['dry_run']:
            return {}
        try:
			#
            return self._api.cancel_order(order_id, pair, params={'type': 'stop'})
        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Could not cancel order. Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not cancel order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	# 0152422
	def _safe_sell_amount(self, pair: str, amount: float) -> float:

        #Get sellable amount.
        #Should be trade.amount - but will fall back to the available amount if necessary.
        #This should cover cases where get_real_amount() was not able to update the amount
        #for whatever reason.
        #:param pair: Pair we're trying to sell
        #:param amount: amount we expect to be available
        #:return: amount to sell
        #:raise: DependencyException: if available balance is not within 2% of the available amount.

        # Update wallets to ensure amounts tied up in a stoploss is now free!
        self.wallets.update()
		#Return a pair's quote currency
        # return self.markets.get(pair, {}).get('base', '')
        trade_base_currency = self.exchange.get_pair_base_currency(pair)
        wallet_amount = self.wallets.get_free(trade_base_currency)
        logger.debug(f"{pair} - Wallet: {wallet_amount} - Trade-amount: {amount}")
        if wallet_amount >= amount:
            return amount
        elif wallet_amount > amount * 0.98:
            logger.info(f"{pair} - Falling back to wallet-amount {wallet_amount} -> {amount}.")
            return wallet_amount
        else:
            raise DependencyException(
                f"Not enough amount to sell. Trade-amount: {amount}, Wallet: {wallet_amount}")

--------------------------------------------------------------------------------

	# 0152423
	def sell(self, pair: str, ordertype: str, amount: float,
             rate: float, time_in_force: str = 'gtc') -> Dict:

        if self._config['dry_run']:
			# 01524231
            dry_order = self.dry_run_order(pair, ordertype, "sell", amount, rate)
            return dry_order

        params = self._params.copy()
        if time_in_force != 'gtc' and ordertype != 'market':
            params.update({'timeInForce': time_in_force})
		# 01524232
        return self.create_order(pair, ordertype, 'sell', amount, rate, params)

--------------------------------------------------------------------------------

	# 01524231
	def dry_run_order(self, pair: str, ordertype: str, side: str, amount: float,
                      rate: float, params: Dict = {}) -> Dict[str, Any]:
        order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
		# 7123 Returns the amount to buy or sell to a precision the Exchange accepts
        # Reimplementation of ccxt internal methods - ensuring we can test the result is correct
        # based on our definitions.
        _amount = self.amount_to_precision(pair, amount)
        dry_order = {
            'id': order_id,
            'symbol': pair,
            'price': rate,
            'average': rate,
            'amount': _amount,
            'cost': _amount * rate,
            'type': ordertype,
            'side': side,
            'remaining': _amount,
            'datetime': arrow.utcnow().isoformat(),
            'timestamp': int(arrow.utcnow().int_timestamp * 1000),
            'status': "closed" if ordertype == "market" else "open",
            'fee': None,
            'info': {}
        }
		# 015242311
        self._store_dry_order(dry_order, pair)
        # Copy order and close it - so the returned order is open unless it's a market order
        return dry_order

--------------------------------------------------------------------------------

	# 015242311
	def _store_dry_order(self, dry_order: Dict, pair: str) -> None:
        closed_order = dry_order.copy()
        if closed_order['type'] in ["market", "limit"]:
            closed_order.update({
                'status': 'closed',
                'filled': closed_order['amount'],
                'remaining': 0,
                'fee': {
                    'currency': self.get_pair_quote_currency(pair),
                    'cost': dry_order['cost'] * self.get_fee(pair),
                    'rate': self.get_fee(pair)
                }
            })
        if closed_order["type"] in ["stop_loss_limit", "stop-loss-limit"]:
            closed_order["info"].update({"stopPrice": closed_order["price"]})
        self._dry_run_open_orders[closed_order["id"]] = closed_order

--------------------------------------------------------------------------------

	# 01524232
	def create_order(self, pair: str, ordertype: str, side: str, amount: float,
                     rate: float, params: Dict = {}) -> Dict:
        try:
            # Set the precision for amount and price(rate) as accepted by the exchange
			# 7123 Returns the amount to buy or sell to a precision the Exchange accepts
	        # Reimplementation of ccxt internal methods - ensuring we can test the result is correct
	        # based on our definitions.
            amount = self.amount_to_precision(pair, amount)
            needs_price = (ordertype != 'market'
                           or self._api.options.get("createMarketBuyOrderRequiresPrice", False))

			rate_for_order = self.price_to_precision(pair, rate) if needs_price else None
			# create order and send to api for execution
            return self._api.create_order(pair, ordertype, side,
                                          amount, rate_for_order, params)

--------------------------------------------------------------------------------

	# 01524234
	def handle_insufficient_funds(self, trade: Trade):

        #Determine if we ever opened a sell order for this trade.
        #If not, try update buy fees - otherwise "refind" the open order we obviously lost.

        sell_order = trade.select_order('sell', None)
        if sell_order:
			# 015242341 Try refinding a lost trade.
	        #Only used when InsufficientFunds appears on sell orders (stoploss or sell).
	        #Tries to walk the stored orders and sell them off eventually.
            self.refind_lost_order(trade)
        else:
            self.reupdate_buy_order_fees(trade)

--------------------------------------------------------------------------------

	# 015242341
	def refind_lost_order(self, trade):

        #Try refinding a lost trade.
        #Only used when InsufficientFunds appears on sell orders (stoploss or sell).
        #Tries to walk the stored orders and sell them off eventually.

        logger.info(f"Trying to refind lost order for {trade}")
        for order in trade.orders:
            logger.info(f"Trying to refind {order}")
            fo = None
            if not order.ft_is_open:
                logger.debug(f"Order {order} is no longer open.")
                continue
            if order.ft_order_side == 'buy':
                # Skip buy side - this is handled by reupdate_buy_order_fees
                continue
            try:
				# 0152423411 Simple wrapper calling either fetch_order or fetch_stoploss_order depending on
        		# the stoploss_order parameter
                fo = self.exchange.fetch_order_or_stoploss_order(order.order_id, order.ft_pair,
                                                                 order.ft_order_side == 'stoploss')
                if order.ft_order_side == 'stoploss':
                    if fo and fo['status'] == 'open':
                        # Assume this as the open stoploss order
                        trade.stoploss_order_id = order.order_id
                elif order.ft_order_side == 'sell':
                    if fo and fo['status'] == 'open':
                        # Assume this as the open order
                        trade.open_order_id = order.order_id
                if fo:
                    logger.info(f"Found {order} for trade {trade}.jj")
					#0132 Checks trades with open orders and updates the amount if necessary
		        	# Handles closing both buy and sell orders, check if trade is canceled or order is closed
                    self.update_trade_state(trade, order.order_id, fo,
                                            stoploss_order=order.ft_order_side == 'stoploss')

            except ExchangeError:
                logger.warning(f"Error updating {order.order_id}.")

--------------------------------------------------------------------------------

	# 0152423411
	def fetch_order_or_stoploss_order(self, order_id: str, pair: str,
                                      stoploss_order: bool = False) -> Dict:

        #Simple wrapper calling either fetch_order or fetch_stoploss_order depending on
        #the stoploss_order parameter
        #:param stoploss_order: If true, uses fetch_stoploss_order, otherwise fetch_order.

        if stoploss_order:
            return self.fetch_stoploss_order(order_id, pair)
		# 015111
        return self.fetch_order(order_id, pair)

--------------------------------------------------------------------------------

	# 01525
	def get_sell_rate(self, pair: str, refresh: bool) -> float:

        #Get sell rate - either using ticker bid or first bid based on orderbook
        #The orderbook portion is only used for rpc messaging, which would otherwise fail
        #for BitMex (has no bid/ask in fetch_ticker)
        #or remain static in any other case since it's not updating.
        #:param pair: Pair to get rate for
        #:param refresh: allow cached data
        #:return: Bid rate

        if not refresh:
            rate = self._sell_rate_cache.get(pair)
            # Check if cache has been invalidated
            if rate:
                logger.debug(f"Using cached sell rate for {pair}.")
                return rate

        ask_strategy = self.config.get('ask_strategy', {})
        if ask_strategy.get('use_order_book', False):
            # This code is only used for notifications, selling uses the generator directly
            logger.info(
                f"Getting price from order book {ask_strategy['price_side'].capitalize()} side."
            )
            try:
                rate = next(self._order_book_gen(pair, f"{ask_strategy['price_side']}s"))
            except (IndexError, KeyError) as e:
                logger.warning("Sell Price at location from orderbook could not be determined.")
                raise PricingError from e
        else:
			# 015251
            ticker = self.exchange.fetch_ticker(pair)
            ticker_rate = ticker[ask_strategy['price_side']]
            if ticker['last'] and ticker_rate < ticker['last']:
                balance = ask_strategy.get('bid_last_balance', 0.0)
                ticker_rate = ticker_rate - balance * (ticker_rate - ticker['last'])
            rate = ticker_rate

        if rate is None:
            raise PricingError(f"Sell-Rate for {pair} was empty.")
        self._sell_rate_cache[pair] = rate
        return rate

--------------------------------------------------------------------------------

	# 015251
	@retrier
    def fetch_ticker(self, pair: str) -> dict:
        try:
            if (pair not in self.markets or
                    self.markets[pair].get('active', False) is False):
                raise ExchangeError(f"Pair {pair} not available")
            data = self._api.fetch_ticker(pair)
            return data
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not load ticker due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	#016
	def get_free_open_trades(self) -> int:

      #Return the number of free open trades slots or 0 if
      #max number of open trades reached
	  # 014 get_open_trades return amount of total opentrade, which has been bought
	  # Trade.get_trades(Trade.is_open.is_(True)).all()
      open_trades = len(Trade.get_open_trades())
      return max(0, self.config['max_open_trades'] - open_trades)

--------------------------------------------------------------------------------

	#013
	def check_handle_timedout(self) -> None:

	    #Check if any orders are timed out and cancel if neccessary
	    #:param timeoutvalue: Number of minutes until order is considered timed out
	    #:return: None

	    for trade in Trade.get_open_order_trades():
	        try:
	            if not trade.open_order_id:
	                continue
				# 015111 get new trade.open_order_id
	            order = self.exchange.fetch_order(trade.open_order_id, trade.pair)
	        except (ExchangeError):
	            logger.info('Cannot query order for %s due to %s', trade, traceback.format_exc())
	            continue
			#0132 Checks trades with open orders and updates the amount if necessary
        	# Handles closing both buy and sell orders, check if trade is canceled or order is closed
	        fully_cancelled = self.update_trade_state(trade, trade.open_order_id, order)

			#check if trade is buy, open trade, fully_cancelled
	        if (order['side'] == 'buy' and (order['status'] == 'open' or fully_cancelled) and (
                fully_cancelled
                or self._check_timed_out('buy', order)
				# Check buy timeout function callback.
        		#This method can be used to override the buy-timeout.
        		#It is called whenever a limit buy order has been created,
        		#and is not yet fully filled.
                or strategy_safe_wrapper(self.strategy.check_buy_timeout,
                                         default_retval=False)(pair=trade.pair,
                                                               trade=trade,
                                                               order=order))):
						   #then handle the cancel buy
	            		   self.handle_cancel_buy(trade, order, constants.CANCEL_REASON['TIMEOUT'])
			#check if trade is sell, open trade, fully_cancelled
	        elif (order['side'] == 'sell' and (order['status'] == 'open' or fully_cancelled) and (
	              fully_cancelled
	              or self._check_timed_out('sell', order)
	              or strategy_safe_wrapper(self.strategy.check_sell_timeout,
	                                       default_retval=False)(pair=trade.pair,
	                                                             trade=trade,
	                                                             order=order))):
							#then handle the cancel sell
	            			 self.handle_cancel_sell(trade, order, constants.CANCEL_REASON['TIMEOUT'])

--------------------------------------------------------------------------------

	# 0132 Common update trade state methods
    def update_trade_state(self, trade: Trade, order_id: str, action_order: Dict[str, Any] = None,
                           stoploss_order: bool = False) -> bool:

        #Checks trades with open orders and updates the amount if necessary
        #Handles closing both buy and sell orders.
        #:param trade: Trade object of the trade we're analyzing
        #:param order_id: Order-id of the order we're analyzing
        #:param action_order: Already aquired order object
        #:return: True if order has been cancelled without being filled partially, False otherwise

        if not order_id:
            logger.warning(f'Orderid for trade {trade} is empty.')
            return False

        # Update trade with order values
        logger.info('Found open order for %s', trade)
        try:
			# Simple wrapper calling either
			# or fetch_stoploss_order depending on
        	# the stoploss_order parameter
			# 0152423411 Simple wrapper calling either fetch_order or fetch_stoploss_order depending on
			# the stoploss_order parameter
            order = action_order or self.exchange.fetch_order_or_stoploss_order(order_id,
                                                                                trade.pair,
                                                                                stoploss_order)
        except InvalidOrderException as exception:
            logger.warning('Unable to fetch order %s: %s', order_id, exception)
            return False
		# 01512 Get all non-closed orders - useful when trying to batch-update orders
        trade.update_order(order)

        # Try update amount (binance-fix)
        try:
			# 01321 Detect and update trade fee.
        	#Calls trade.update_fee() uppon correct detection.
        	#Returns modified amount if the fee was taken from the destination currency.
        	#Necessary for exchanges which charge fees in base currency (e.g. binance)
            new_amount = self.get_real_amount(trade, order)
            if not isclose(safe_value_fallback(order, 'filled', 'amount'), new_amount,
                           abs_tol=constants.MATH_CLOSE_PREC):
                order['amount'] = new_amount
                order.pop('filled', None)
                trade.recalc_open_trade_value()
        except DependencyException as exception:
            logger.warning("Could not update trade amount: %s", exception)

        if self.exchange.check_order_canceled_empty(order):
            # Trade has been cancelled on exchange
            # Handling of this will happen in check_handle_timeout.
            return True
        trade.update(order)

        # Updating wallets when order is closed
        if not trade.is_open:
            self.protections.stop_per_pair(trade.pair)
            self.protections.global_stop()
            self.wallets.update()
        return False

--------------------------------------------------------------------------------

	#071
	def create_trade(self, pair: str) -> bool:
        #Check the implemented trading strategy for buy signals.\
        #If the pair triggers the buy signal a new trade record gets created
        #and the buy-order opening the trade gets issued towards the exchange.

        #:return: True if a trade has been created.

        logger.debug(f"create_trade for pair {pair}")
		# 01521
        analyzed_df, _ = self.dataprovider.get_analyzed_dataframe(pair, self.strategy.timeframe)
        nowtime = analyzed_df.iloc[-1]['date'] if len(analyzed_df) > 0 else None
        if self.strategy.is_pair_locked(pair, nowtime):
            lock = PairLocks.get_pair_longest_lock(pair, nowtime)
            if lock:
                self.log_once(f"Pair {pair} is still locked until "
                              f"{lock.lock_end_time.strftime(constants.DATETIME_PRINT_FORMAT)}.",
                              logger.info)
            else:
                self.log_once(f"Pair {pair} is still locked.", logger.info)
            return False

        # get_free_open_trades is checked before create_trade is called
        # but it is still used here to prevent opening too many trades within one iteration
        if not self.get_free_open_trades():
            logger.debug(f"Can't open a new trade for {pair}: max number of trades is reached.")
            return False

        # running get_signal on historical data fetched
        (buy, sell) = self.strategy.get_signal(pair, self.strategy.timeframe, analyzed_df)

        if buy and not sell:
            stake_amount = self.wallets.get_trade_stake_amount(pair, self.get_free_open_trades(),
                                                               self.edge)
            if not stake_amount:
                logger.debug(f"Stake amount is 0, ignoring possible trade for {pair}.")
                return False

            logger.info(f"Buy signal found: about create a new trade with stake_amount: "
                        f"{stake_amount} ...")

            bid_check_dom = self.config.get('bid_strategy', {}).get('check_depth_of_market', {})
            if ((bid_check_dom.get('enabled', False)) and
                    (bid_check_dom.get('bids_to_ask_delta', 0) > 0)):
				# 711
                if self._check_depth_of_market_buy(pair, bid_check_dom):
                    logger.info(f'Executing Buy for {pair}.')
					# 712
                    return self.execute_buy(pair, stake_amount)
                else:
                    return False

            logger.info(f'Executing Buy for {pair}')
            return self.execute_buy(pair, stake_amount)
        else:
            return False

--------------------------------------------------------------------------------
	# 711
	def _check_depth_of_market_buy(self, pair: str, conf: Dict) -> bool:
        #Checks depth of market before executing a buy
        conf_bids_to_ask_delta = conf.get('bids_to_ask_delta', 0)
        logger.info(f"Checking depth of market for {pair} ...")
		# 7111 Get L2 order book from exchange.
        #Can be limited to a certain amount (if supported).
        #Returns a dict in the format
        order_book = self.exchange.fetch_l2_order_book(pair, 1000)
		# 7112 TODO: This should get a dedicated test
    	# Gets order book list, returns dataframe with below format per suggested by creslin
    	# -------------------------------------------------------------------
     	# b_sum       b_size       bids       asks       a_size       a_sum
    	# -------------------------------------------------------------------
        order_book_data_frame = order_book_to_dataframe(order_book['bids'], order_book['asks'])
        order_book_bids = order_book_data_frame['b_size'].sum()
        order_book_asks = order_book_data_frame['a_size'].sum()
        bids_ask_delta = order_book_bids / order_book_asks
        logger.info(
            f"Bids: {order_book_bids}, Asks: {order_book_asks}, Delta: {bids_ask_delta}, "
            f"Bid Price: {order_book['bids'][0][0]}, Ask Price: {order_book['asks'][0][0]}, "
            f"Immediate Bid Quantity: {order_book['bids'][0][1]}, "
            f"Immediate Ask Quantity: {order_book['asks'][0][1]}."
        )
        if bids_ask_delta >= conf_bids_to_ask_delta:
            logger.info(f"Bids to asks delta for {pair} DOES satisfy condition.")
            return True
        else:
            logger.info(f"Bids to asks delta for {pair} does not satisfy condition.")
            return False

--------------------------------------------------------------------------------

	# 7111
	@retrier
    def fetch_l2_order_book(self, pair: str, limit: int = 100) -> dict:

        # Get L2 order book from exchange.
        # Can be limited to a certain amount (if supported).
        # Returns a dict in the format
        # {'asks': [price, volume], 'bids': [price, volume]}

		# 71111
        limit1 = self.get_next_limit_in_list(limit, self._ft_has['l2_limit_range'])
        try:
			# 7111 Get L2 order book from exchange.
	        #Can be limited to a certain amount (if supported).
	        #Returns a dict in the format
            return self._api.fetch_l2_order_book(pair, limit1)
        except ccxt.NotSupported as e:
            raise OperationalException(
                f'Exchange {self._api.name} does not support fetching order book.'
                f'Message: {e}') from e
        except ccxt.DDoSProtection as e:
            raise DDosProtection(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not get order book due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

--------------------------------------------------------------------------------

	# 71111
	@staticmethod
    def get_next_limit_in_list(limit: int, limit_range: Optional[List[int]]):

        #Get next greater value in the list.
        #Used by fetch_l2_order_book if the api only supports a limited range

        if not limit_range:
            return limit
        return min([x for x in limit_range if limit <= x] + [max(limit_range)])

--------------------------------------------------------------------------------

	# 7112
	def order_book_to_dataframe(bids: list, asks: list) -> DataFrame:

	    #TODO: This should get a dedicated test
	    #Gets order book list, returns dataframe with below format per suggested by creslin
	    #-------------------------------------------------------------------
	    # b_sum       b_size       bids       asks       a_size       a_sum
	    #-------------------------------------------------------------------

	    cols = ['bids', 'b_size']

	    bids_frame = DataFrame(bids, columns=cols)
	    # add cumulative sum column
	    bids_frame['b_sum'] = bids_frame['b_size'].cumsum()
	    cols2 = ['asks', 'a_size']
	    asks_frame = DataFrame(asks, columns=cols2)
	    # add cumulative sum column
	    asks_frame['a_sum'] = asks_frame['a_size'].cumsum()

	    frame = pd.concat([bids_frame['b_sum'], bids_frame['b_size'], bids_frame['bids'],
	                       asks_frame['asks'], asks_frame['a_size'], asks_frame['a_sum']], axis=1,
	                      keys=['b_sum', 'b_size', 'bids', 'asks', 'a_size', 'a_sum'])
	    # logger.info('order book %s', frame )
	    return frame

--------------------------------------------------------------------------------

	# 712
	def execute_buy(self, pair: str, stake_amount: float, price: Optional[float] = None,
                    forcebuy: bool = False) -> bool:
        #Executes a limit buy for the given pair
        #:param pair: pair for which we want to create a LIMIT_BUY
        #:return: True if a buy order is created, false if it fails.
        time_in_force = self.strategy.order_time_in_force['buy']

        if price:
            buy_limit_requested = price
        else:
            # 7121 Calculate price
			# Calculates bid target between current ask price and last price
            buy_limit_requested = self.get_buy_rate(pair, True)

        if not buy_limit_requested:
            raise PricingError('Could not determine buy price.')
		# 7122
        min_stake_amount = self.exchange.get_min_pair_stake_amount(pair, buy_limit_requested,
                                                                   self.strategy.stoploss)
        if min_stake_amount is not None and min_stake_amount > stake_amount:
            logger.warning(
                f"Can't open a new trade for {pair}: stake amount "
                f"is too small ({stake_amount} < {min_stake_amount})"
            )
            return False

        amount = stake_amount / buy_limit_requested
        order_type = self.strategy.order_types['buy']
        if forcebuy:
            # Forcebuy can define a different ordertype
            order_type = self.strategy.order_types.get('forcebuy', order_type)

		# Called right before placing a buy order.
        #Timing for this function is critical, so avoid doing heavy computations or
        #network requests in this method.
        if not strategy_safe_wrapper(self.strategy.confirm_trade_entry, default_retval=True)(
                pair=pair, order_type=order_type, amount=amount, rate=buy_limit_requested,
                time_in_force=time_in_force):
            logger.info(f"User requested abortion of buying {pair}")
            return False
		# 7123 Returns the amount to buy or sell to a precision the Exchange accepts
        # Reimplementation of ccxt internal methods - ensuring we can test the result is correct
        # based on our definitions.
        amount = self.exchange.amount_to_precision(pair, amount)
		# 7124 buy using create_order
        order = self.exchange.buy(pair=pair, ordertype=order_type,
                                  amount=amount, rate=buy_limit_requested,
                                  time_in_force=time_in_force)
        order_obj = Order.parse_from_ccxt_object(order, pair, 'buy')
        order_id = order['id']
        order_status = order.get('status', None)

        # we assume the order is executed at the price requested
        buy_limit_filled_price = buy_limit_requested
        amount_requested = amount

        if order_status == 'expired' or order_status == 'rejected':
            order_tif = self.strategy.order_time_in_force['buy']

            # return false if the order is not filled
            if float(order['filled']) == 0:
                logger.warning('Buy %s order with time in force %s for %s is %s by %s.'
                               ' zero amount is fulfilled.',
                               order_tif, order_type, pair, order_status, self.exchange.name)
                return False
            else:
                # the order is partially fulfilled
                # in case of IOC orders we can check immediately
                # if the order is fulfilled fully or partially
                logger.warning('Buy %s order with time in force %s for %s is %s by %s.'
                               ' %s amount fulfilled out of %s (%s remaining which is canceled).',
                               order_tif, order_type, pair, order_status, self.exchange.name,
                               order['filled'], order['amount'], order['remaining']
                               )
                stake_amount = order['cost']
                amount = safe_value_fallback(order, 'filled', 'amount')
                buy_limit_filled_price = safe_value_fallback(order, 'average', 'price')

        # in case of FOK the order may be filled immediately and fully
        elif order_status == 'closed':
            stake_amount = order['cost']
            amount = safe_value_fallback(order, 'filled', 'amount')
            buy_limit_filled_price = safe_value_fallback(order, 'average', 'price')

        # Fee is applied twice because we make a LIMIT_BUY and LIMIT_SELL
        fee = self.exchange.get_fee(symbol=pair, taker_or_maker='maker')
        trade = Trade(
            pair=pair,
            stake_amount=stake_amount,
            amount=amount,
            amount_requested=amount_requested,
            fee_open=fee,
            fee_close=fee,
            open_rate=buy_limit_filled_price,
            open_rate_requested=buy_limit_requested,
            open_date=datetime.utcnow(),
            exchange=self.exchange.id,
            open_order_id=order_id,
            strategy=self.strategy.get_strategy_name(),
            timeframe=timeframe_to_minutes(self.config['timeframe'])
        )
        trade.orders.append(order_obj)

        # Update fees if order is closed
        if order_status == 'closed':
			# 0132 Common update trade state methods
            self.update_trade_state(trade, order_id, order)

        Trade.session.add(trade)
        Trade.session.flush()

        # Updating wallets
        self.wallets.update()

        self._notify_buy(trade, order_type)

        return True

--------------------------------------------------------------------------------

	# 01321
	def get_real_amount(self, trade: Trade, order: Dict) -> float:

        #Detect and update trade fee.
        #Calls trade.update_fee() uppon correct detection.
        #Returns modified amount if the fee was taken from the destination currency.
        #Necessary for exchanges which charge fees in base currency (e.g. binance)
        #:return: identical (or new) amount for the trade

        # Init variables
        order_amount = safe_value_fallback(order, 'filled', 'amount')
        # Only run for closed orders
		# 013211 Verify if this side (buy / sell) has already been updated
        if trade.fee_updated(order.get('side', '')) or order['status'] == 'open':
            return order_amount
		#Return a pair's quote currency
        # return self.markets.get(pair, {}).get('base', '')
        trade_base_currency = self.exchange.get_pair_base_currency(trade.pair)
        # use fee from order-dict if possible
        if self.exchange.order_has_fee(order):
            fee_cost, fee_currency, fee_rate = self.exchange.extract_cost_curr_rate(order)
            logger.info(f"Fee for Trade {trade} [{order.get('side')}]: "
                        f"{fee_cost:.8g} {fee_currency} - rate: {fee_rate}")
            if fee_rate is None or fee_rate < 0.02:
                # Reject all fees that report as > 2%.
                # These are most likely caused by a parsing bug in ccxt
                # due to multiple trades (https://github.com/ccxt/ccxt/issues/8025)
                trade.update_fee(fee_cost, fee_currency, fee_rate, order.get('side', ''))
                if trade_base_currency == fee_currency:
                    # Apply fee to amount
                    return self.apply_fee_conditional(trade, trade_base_currency,
                                                      amount=order_amount, fee_abs=fee_cost)
                return order_amount
        return self.fee_detection_from_trades(trade, order, order_amount)


--------------------------------------------------------------------------------

	# 013211
	def fee_updated(self, side: str) -> bool:

        #Verify if this side (buy / sell) has already been updated

        if side == 'buy':
            return self.fee_open_currency is not None
        elif side == 'sell':
            return self.fee_close_currency is not None
        else:
            return False

--------------------------------------------------------------------------------

	# 7121
	def get_buy_rate(self, pair: str, refresh: bool) -> float:

        #Calculates bid target between current ask price and last price
        #:param pair: Pair to get rate for
        #:param refresh: allow cached data
        #:return: float: Price

        if not refresh:
            rate = self._buy_rate_cache.get(pair)
            # Check if cache has been invalidated
            if rate:
                logger.debug(f"Using cached buy rate for {pair}.")
                return rate

        bid_strategy = self.config.get('bid_strategy', {})
        if 'use_order_book' in bid_strategy and bid_strategy.get('use_order_book', False):
            logger.info(
                f"Getting price from order book {bid_strategy['price_side'].capitalize()} side."
            )
            order_book_top = bid_strategy.get('order_book_top', 1)
            order_book = self.exchange.fetch_l2_order_book(pair, order_book_top)
            logger.debug('order_book %s', order_book)
            # top 1 = index 0
            try:
                rate_from_l2 = order_book[f"{bid_strategy['price_side']}s"][order_book_top - 1][0]
            except (IndexError, KeyError) as e:
                logger.warning(
                    "Buy Price from orderbook could not be determined."
                    f"Orderbook: {order_book}"
                 )
                raise PricingError from e
            logger.info(f'...top {order_book_top} order book buy rate {rate_from_l2:.8f}')
            used_rate = rate_from_l2
        else:
            logger.info(f"Using Last {bid_strategy['price_side'].capitalize()} / Last Price")
            ticker = self.exchange.fetch_ticker(pair)
            ticker_rate = ticker[bid_strategy['price_side']]
            if ticker['last'] and ticker_rate > ticker['last']:
                balance = bid_strategy['ask_last_balance']
                ticker_rate = ticker_rate + balance * (ticker['last'] - ticker_rate)
            used_rate = ticker_rate

        self._buy_rate_cache[pair] = used_rate

        return used_rate

--------------------------------------------------------------------------------

	# 7122
	def get_min_pair_stake_amount(self, pair: str, price: float,
                                  stoploss: float) -> Optional[float]:
        try:
            market = self.markets[pair]
        except KeyError:
            raise ValueError(f"Can't get market information for symbol {pair}")

        if 'limits' not in market:
            return None

        min_stake_amounts = []
        limits = market['limits']
        if ('cost' in limits and 'min' in limits['cost']
                and limits['cost']['min'] is not None):
            min_stake_amounts.append(limits['cost']['min'])

        if ('amount' in limits and 'min' in limits['amount']
                and limits['amount']['min'] is not None):
            min_stake_amounts.append(limits['amount']['min'] * price)

        if not min_stake_amounts:
            return None

        # reserve some percent defined in config (5% default) + stoploss
        amount_reserve_percent = 1.0 + self._config.get('amount_reserve_percent',
                                                        DEFAULT_AMOUNT_RESERVE_PERCENT)
        amount_reserve_percent += abs(stoploss)
        # it should not be more than 50%
        amount_reserve_percent = max(min(amount_reserve_percent, 1.5), 1)

        # The value returned should satisfy both limits: for amount (base currency) and
        # for cost (quote, stake currency), so max() is used here.
        # See also #2575 at github.
        return max(min_stake_amounts) * amount_reserve_percent

--------------------------------------------------------------------------------

	# 7123
	def amount_to_precision(self, pair: str, amount: float) -> float:

        #Returns the amount to buy or sell to a precision the Exchange accepts
        #Reimplementation of ccxt internal methods - ensuring we can test the result is correct
        #based on our definitions.

        if self.markets[pair]['precision']['amount']:
            amount = float(decimal_to_precision(amount, rounding_mode=TRUNCATE,
                                                precision=self.markets[pair]['precision']['amount'],
                                                counting_mode=self.precisionMode,
                                                ))

        return amount

--------------------------------------------------------------------------------

	# 7124
	def buy(self, pair: str, ordertype: str, amount: float,
            rate: float, time_in_force: str) -> Dict:

        if self._config['dry_run']:
			# 01524231
            dry_order = self.dry_run_order(pair, ordertype, "buy", amount, rate)
            return dry_order

        params = self._params.copy()
        if time_in_force != 'gtc' and ordertype != 'market':
            params.update({'timeInForce': time_in_force})
		# 01524232
        return self.create_order(pair, ordertype, 'buy', amount, rate, params)

--------------------------------------------------------------------------------

# 014
persistence/models.py ->
	@staticmethod
    def get_open_trades() -> List[Any]:

        #Query trades from persistence layer
		# 0141 #Helper function to query Trades using filters.
        return Trade.get_trades(Trade.is_open.is_(True)).all()

--------------------------------------------------------------------------------

	@staticmethod
    def get_open_order_trades():

        #Returns all open trades
		# 0141 #Helper function to query Trades using filters.
        return Trade.get_trades(Trade.open_order_id.isnot(None)).all()

-------------------------------------------------------------------------------

	# 0141
	@staticmethod
    def get_trades(trade_filter=None) -> Query:

        #Helper function to query Trades using filters.
        #:param trade_filter: Optional filter to apply to trades
        #                     Can be either a Filter object, or a List of filters
        #                     e.g. `(trade_filter=[Trade.id == trade_id, Trade.is_open.is_(True),])`
        #                     e.g. `(trade_filter=Trade.id == trade_id)`
        #:return: unsorted query object

        if trade_filter is not None:
            if not isinstance(trade_filter, list):
                trade_filter = [trade_filter]
            return Trade.query.filter(*trade_filter)
        else:
            return Trade.query

-------------------------------------------------------------------------------

strategy/interface.py ->
	# 012
	def analyze(self, pairs: List[str]) -> None:

        #Analyze all pairs using analyze_pair().
        #:param pairs: List of pairs to analyze

        for pair in pairs:
            self.analyze_pair(pair)
	# 0121
	def analyze_pair(self, pair: str) -> None:

        #Fetch data for this pair from dataprovider and analyze.
        #Stores the dataframe into the dataprovider.
        #The analyzed dataframe is then accessible via `dp.get_analyzed_dataframe()`.
        #:param pair: Pair to analyze.

        if not self.dp:
            raise OperationalException("DataProvider not found.")
        dataframe = self.dp.ohlcv(pair, self.timeframe)
        if not isinstance(dataframe, DataFrame) or dataframe.empty:
            logger.warning('Empty candle (OHLCV) data for pair %s', pair)
            return

        try:
			# keep some data for dataframes
			# def preserve_df(dataframe: DataFrame) -> Tuple[int, float, datetime]:
        	# 	return len(dataframe), dataframe["close"].iloc[-1], dataframe["date"].iloc[-1]
            df_len, df_close, df_date = self.preserve_df(dataframe)

            dataframe = strategy_safe_wrapper(
				# 0122 Parses the given candle (OHLCV) data and returns a populated DataFrame
		        #add several TA indicators and buy signal to it
                self._analyze_ticker_internal, message=""
            )(dataframe, {'pair': pair})

			# 0123 Ensure dataframe (length, last candle) was not modified, and has all elements we need.
            self.assert_df(dataframe, df_len, df_close, df_date)
        except StrategyError as error:
            logger.warning(f"Unable to analyze candle (OHLCV) data for pair {pair}: {error}")
            return

        if dataframe.empty:
            logger.warning('Empty dataframe for pair %s', pair)
            return

-------------------------------------------------------------------------------
	#0122
	def _analyze_ticker_internal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #Parses the given candle (OHLCV) data and returns a populated DataFrame
        #add several TA indicators and buy signal to it
        #WARNING: Used internally only, may skip analysis if `process_only_new_candles` is set.
        #:param dataframe: Dataframe containing data from exchange
        #:param metadata: Metadata dictionary with additional data (e.g. 'pair')
        #:return: DataFrame of candle (OHLCV) data with indicator data and signals added

        pair = str(metadata.get('pair'))

        # Test if seen this pair and last candle before.
        # always run if process_only_new_candles is set to false
        if (not self.process_only_new_candles or
                self._last_candle_seen_per_pair.get(pair, None) != dataframe.iloc[-1]['date']):
            # 01221 Defs that only make change on new candle data.
			#Parses the given candle (OHLCV) data and returns a populated DataFrame
		    #add several TA indicators and buy signal to it
            dataframe = self.analyze_ticker(dataframe, metadata)
            self._last_candle_seen_per_pair[pair] = dataframe.iloc[-1]['date']
            if self.dp:
				# 012212 Store cached Dataframe.
        		# Using private method as this should never be used by a user
        		# (but the class is exposed via `self.dp` to the strategy)
                self.dp._set_cached_df(pair, self.timeframe, dataframe)
        else:
            logger.debug("Skipping TA Analysis for already analyzed candle")
            dataframe['buy'] = 0
            dataframe['sell'] = 0

        # Other Defs in strategy that want to be called every loop here
        # twitter_sell = self.watch_twitter_feed(dataframe, metadata)
        logger.debug("Loop Analysis Launched")

        return dataframe

--------------------------------------------------------------------------------
	# 01221
	def analyze_ticker(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #Parses the given candle (OHLCV) data and returns a populated DataFrame
        #add several TA indicators and buy signal to it
        #:param dataframe: Dataframe containing data from exchange
        #:param metadata: Metadata dictionary with additional data (e.g. 'pair')
        #:return: DataFrame of candle (OHLCV) data with indicator data and signals added

        logger.debug("TA Analysis Launched")
		# 0124 Adds several different TA indicators to the given DataFrame
        #Performance Note: For the best performance be frugal on the number of indicators
        #you are using. Let uncomment only the indicator you are using in your strategies
        #or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        dataframe = self.advise_indicators(dataframe, metadata)
		# 0125 Based on TA indicators, populates the buy signal for the given dataframe
		# dataframe.loc[
        #    (
        #        (qtpylib.crossed_above(dataframe['rsi'], 30)) & (dataframe['tema'] <= dataframe['bb_middleband'])
        #    ), 'buy'] = 1
        dataframe = self.advise_buy(dataframe, metadata)
		# 0126 Based on TA indicators, populates the sell signal for the given dataframe
		# dataframe.loc[ (
        #        (qtpylib.crossed_above(dataframe['rsi'], 70)) &  (dataframe['tema'] > dataframe['bb_middleband']) &  # Guard: tema above BB middle
        #    ), 'sell'] = 1
        dataframe = self.advise_sell(dataframe, metadata)
        return dataframe

-------------------------------------------------------------------------------

	# 012212
	def _set_cached_df(self, pair: str, timeframe: str, dataframe: DataFrame) -> None:

        #Store cached Dataframe.
        #Using private method as this should never be used by a user
        #(but the class is exposed via `self.dp` to the strategy)
        #:param pair: pair to get the data for
        #:param timeframe: Timeframe to get data for
        #:param dataframe: analyzed dataframe
		def __init__(self, config: dict, exchange: Exchange, pairlists=None) -> None:
			self.__cached_pairs: Dict[PairWithTimeframe, Tuple[DataFrame, datetime]] = {}

        self.__cached_pairs[(pair, timeframe)] = (dataframe, datetime.now(timezone.utc))

-------------------------------------------------------------------------------

	# 0123
	def assert_df(self, dataframe: DataFrame, df_len: int, df_close: float, df_date: datetime):

        #Ensure dataframe (length, last candle) was not modified, and has all elements we need.

        message = ""
        if df_len != len(dataframe):
            message = "length"
        elif df_close != dataframe["close"].iloc[-1]:
            message = "last close price"
        elif df_date != dataframe["date"].iloc[-1]:
            message = "last date"
        if message:
            if self.disable_dataframe_checks:
                logger.warning(f"Dataframe returned from strategy has mismatching {message}.")
            else:
                raise StrategyError(f"Dataframe returned from strategy has mismatching {message}.")

-------------------------------------------------------------------------------

	# 0124
	def advise_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #Populate indicators that will be used in the Buy and Sell strategy
        #This method should not be overridden.
        #:param dataframe: Dataframe with data from the exchange
        #:param metadata: Additional information, like the currently traded pair
        #:return: a Dataframe with all mandatory indicators for the strategies

        logger.debug(f"Populating indicators for pair {metadata.get('pair')}.")
        if self._populate_fun_len == 2:
            warnings.warn("deprecated - check out the Sample strategy to see "
                          "the current function headers!", DeprecationWarning)
            return self.populate_indicators(dataframe)  # type: ignore
        else:
            return self.populate_indicators(dataframe, metadata)

--------------------------------------------------------------------------------
	#0125
	def advise_buy(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #Based on TA indicators, populates the buy signal for the given dataframe
        #This method should not be overridden.
        #:param dataframe: DataFrame
        #:param pair: Additional information, like the currently traded pair
        #:return: DataFrame with buy column

        logger.debug(f"Populating buy signals for pair {metadata.get('pair')}.")

        if self._buy_fun_len == 2:
            warnings.warn("deprecated - check out the Sample strategy to see "
                          "the current function headers!", DeprecationWarning)
            return self.populate_buy_trend(dataframe)  # type: ignore
        else:
            return self.populate_buy_trend(dataframe, metadata)

--------------------------------------------------------------------------------
	#0126
    def advise_sell(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #Based on TA indicators, populates the sell signal for the given dataframe
        #This method should not be overridden.
        #:param dataframe: DataFrame
        #:param pair: Additional information, like the currently traded pair
        #:return: DataFrame with sell column

        logger.debug(f"Populating sell signals for pair {metadata.get('pair')}.")
        if self._sell_fun_len == 2:
            warnings.warn("deprecated - check out the Sample strategy to see "
                          "the current function headers!", DeprecationWarning)
            return self.populate_sell_trend(dataframe)  # type: ignore
        else:
            return self.populate_sell_trend(dataframe, metadata)
