
freqtradebot.py ->
    def process(self) -> None: ->

		# Check whether markets have to be reloaded and reload them when it's needed
        self.exchange.reload_markets()
		# 001 Update closed trades without close fees assigned.
        #Only acts when Orders are in the database, otherwise the last orderid is unknown.
        self.update_closed_trades_without_assigned_fees() ->
        {{}
            #Update closed trades without close fees assigned.
            #Only acts when Orders are in the database, otherwise the last orderid is unknown.

            if self.config['dry_run']:
                # Updating open orders in dry-run does not make sense and will fail.
                return

            trades: List[Trade] = Trade.get_sold_trades_without_assigned_fees() ->
            {{}
                @staticmethod
                def get_sold_trades_without_assigned_fees():
                    #Returns all closed trades which don't have fees set correctly
                    return Trade.get_trades([Trade.fee_close_currency.is_(None),
                                             Trade.orders.any(),
                                             Trade.is_open.is_(False),
                                             ]).all()
            }
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
        }

        # Query trades from persistence layer
        trades = Trade.get_open_trades() ->
        {{}
            {{}
                #Query trades from persistence layer
                return Trade.get_trades(Trade.is_open.is_(True)).all() ->
                {{}
                    if trade_filter is not None:
                        if not isinstance(trade_filter, list):
                            trade_filter = [trade_filter]
                        return Trade.query.filter(*trade_filter)
                    else:
                        return Trade.query
                }
            }
        }

        self.active_pair_whitelist = self._refresh_active_whitelist(trades)

        # Refreshing candles
        self.dataprovider.refresh(self.pairlists.create_pair_list(self.active_pair_whitelist),
                                  self.strategy.informative_pairs())

		strategy_safe_wrapper(self.strategy.bot_loop_start, supress_error=True)()

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

---------------------------------------------------------------------------------------------------------------

sample_strategy.py ->
    class SampleStrategy(IStrategy):
        INTERFACE_VERSION = 2
        minimal_roi = {
            "70": 0.0, #sell when trade is non-loosing (in effect after 70 minutes)
            "60": 0.01, #sell when 1% profit was reached in effect after 60 minutes
            "30": 0.02, #sell when 2% profit was reached in effect after
            "0": 0.04 #sell whether 4% profit was reached
        }
        stoploss = -0.10 #stopkiss of -10%
        trailing_stop = False
        timeframe = '5m'
        process_only_new_candles = False
        use_sell_signal = True
        sell_profit_only = False
        ignore_roi_if_buy_signal = False
        startup_candle_count: int = 30
        order_types = {
            'buy': 'limit',
            'sell': 'limit',
            'stoploss': 'market',
            'stoploss_on_exchange': False
        }
        order_time_in_force = {
            'buy': 'gtc',
            'sell': 'gtc'
        }

freqtradebot.py ->
    def process(self) -> None: ->

        self.exchange.reload_markets()

        self.update_closed_trades_without_assigned_fees() ->
        {{}
            if self.config['dry_run']:
                return

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
                                                stoploss_order=order.ft_order_side == 'stoploss') ->
                        {{}
                            if not order_id:
                                return False
                            order = action_order or self.exchange.fetch_order_or_stoploss_order(order_id, trade.pair, stoploss_order) ->
                            {{}
                                if stoploss_order:
                                    return self.fetch_stoploss_order(order_id, pair) ->
                                    {{}
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
                                    }
                                return self.fetch_order(order_id, pair) ->
                                {{}
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
                                }
                            }
                            trade.update_order(order) ->
                            {{}
                                Order.update_orders(self.orders, order) ->
                                {{}
                                    if not isinstance(order, dict):
                                        logger.warning(f"{order} is not a valid response object.")
                                        return
                                    filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                    if filtered_orders:
                                        oobj = filtered_orders[0]
                                        oobj.update_from_ccxt_object(order) ->
                                        {{}
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
                                                self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                            self.ft_is_open = True
                                            if self.status in ('closed', 'canceled', 'cancelled'):
                                                self.ft_is_open = False
                                                if order.get('filled', 0) > 0:
                                                    self.order_filled_date = arrow.utcnow().datetime
                                            self.order_update_date = arrow.utcnow().datetime
                                        }
                                    else:
                                        logger.warning(f"Did not find order for {order}.")
                                }
                            }
                            new_amount = self.get_real_amount(trade, order)
                            if not isclose(safe_value_fallback(order, 'filled', 'amount'), new_amount,abs_tol=constants.MATH_CLOSE_PREC):
                                order['amount'] = new_amount
                                order.pop('filled', None)
                                trade.recalc_open_trade_value()

                            if self.exchange.check_order_canceled_empty(order):
                                return True
                            trade.update(order)
                            if not trade.is_open:
                                self.protections.stop_per_pair(trade.pair)
                                self.protections.global_stop()
                                self.wallets.update()
                            return False
                        }

            trades: List[Trade] = Trade.get_open_trades_without_assigned_fees()
            for trade in trades:
    			# 013211 Verify if this side (buy / sell) has already been updated
                if trade.is_open and not trade.fee_updated('buy'):
                    order = trade.select_order('buy', False)
                    if order:
                        logger.info(f"Updating buy-fee on trade {trade} for order {order.order_id}.")
    					# 0132 Common update trade state methods
    					self.update_trade_state(trade, order.order_id) ->
                        {{}
                            if not order_id:
                                return False
                            order = action_order or self.exchange.fetch_order_or_stoploss_order(order_id, trade.pair, stoploss_order) ->
                            {{}
                                if stoploss_order:
                                    return self.fetch_stoploss_order(order_id, pair) ->
                                    {{}
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
                                    }
                                return self.fetch_order(order_id, pair) ->
                                {{}
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
                                }

                            }
                            trade.update_order(order) ->
                            {{}
                                Order.update_orders(self.orders, order) ->
                                {{}
                                    if not isinstance(order, dict):
                                        logger.warning(f"{order} is not a valid response object.")
                                        return
                                    filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                    if filtered_orders:
                                        oobj = filtered_orders[0]
                                        oobj.update_from_ccxt_object(order) ->
                                        {{}
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
                                                self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                            self.ft_is_open = True
                                            if self.status in ('closed', 'canceled', 'cancelled'):
                                                self.ft_is_open = False
                                                if order.get('filled', 0) > 0:
                                                    self.order_filled_date = arrow.utcnow().datetime
                                            self.order_update_date = arrow.utcnow().datetime
                                        }
                                    else:
                                        logger.warning(f"Did not find order for {order}.")
                                }
                            }
                            new_amount = self.get_real_amount(trade, order)
                            if not isclose(safe_value_fallback(order, 'filled', 'amount'), new_amount,abs_tol=constants.MATH_CLOSE_PREC):
                                order['amount'] = new_amount
                                order.pop('filled', None)
                                trade.recalc_open_trade_value()

                            if self.exchange.check_order_canceled_empty(order):
                                return True
                            trade.update(order)
                            if not trade.is_open:
                                self.protections.stop_per_pair(trade.pair)
                                self.protections.global_stop()
                                self.wallets.update()
                            return False
                        }
        }

        trades = Trade.get_open_trades()

        self.active_pair_whitelist = self._refresh_active_whitelist(trades)

        # Refreshing candles
        self.dataprovider.refresh(self.pairlists.create_pair_list(self.active_pair_whitelist),
                                  self.strategy.informative_pairs())

		strategy_safe_wrapper(self.strategy.bot_loop_start, supress_error=True)()

	    self.strategy.analyze(self.active_pair_whitelist)
            for pair in pairs:
                self.analyze_pair(pair) ->
                {{}
                    if not self.dp:
                        raise OperationalException("DataProvider not found.")
                    dataframe = self.dp.ohlcv(pair, self.timeframe)
                    if not isinstance(dataframe, DataFrame) or dataframe.empty:
                        logger.warning('Empty candle (OHLCV) data for pair %s', pair)
                        return
                    try:
                        df_len, df_close, df_date = self.preserve_df(dataframe)
                        dataframe = strategy_safe_wrapper(self._analyze_ticker_internal, message="")(dataframe, {'pair': pair}) ->
                        {{}
                            pair = str(metadata.get('pair'))
                            if (not self.process_only_new_candles or self._last_candle_seen_per_pair.get(pair, None) != dataframe.iloc[-1]['date']):
                                dataframe = self.analyze_ticker(dataframe, metadata) ->
                                    dataframe = self.advise_indicators(dataframe, metadata)
                                    dataframe = self.advise_buy(dataframe, metadata)
                                    dataframe = self.advise_sell(dataframe, metadata)
                                    return dataframe
                                self._last_candle_seen_per_pair[pair] = dataframe.iloc[-1]['date']
                            return dataframe
                        }
                        self.assert_df(dataframe, df_len, df_close, df_date)
                    except StrategyError as error:
                        logger.warning(f"Unable to analyze candle (OHLCV) data for pair {pair}: {error}")
                        return

                    if dataframe.empty:
                        logger.warning('Empty dataframe for pair %s', pair)
                        return
                }

        with self._sell_lock:
            trades = Trade.get_open_trades()
            self.exit_positions(trades) ->
            {{}
                trades_closed = 0
                for trade in trades:
                    try:
                        if (self.strategy.order_types.get('stoploss_on_exchange') and self.handle_stoploss_on_exchange(trade)): ->
    	                    trades_closed += 1
    	                    continue
                        if trade.open_order_id is None and trade.is_open and self.handle_trade(trade): ->
    	                    trades_closed += 1
                    except DependencyException as exception:
	                    logger.warning('Unable to sell trade %s: %s', trade.pair, exception)
                if trades_closed:
	                self.wallets.update()
                return trades_closed
            }
                    def handle_stoploss_on_exchange(self, trade: Trade) -> bool:
                        logger.debug('Handling stoploss on exchange %s ...', trade)

                        stoploss_order = None
                        try:
                            stoploss_order = self.exchange.fetch_stoploss_order(trade.stoploss_order_id, trade.pair) if trade.stoploss_order_id else None ->
                            {{}
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
                            }
                        except InvalidOrderException as exception:
                            logger.warning('Unable to fetch stoploss order: %s', exception)
                        if stoploss_order:
                            trade.update_order(stoploss_order) ->
                            {{}
                                Order.update_orders(self.orders, order) ->
                                {{}
                                    if not isinstance(order, dict):
                                        logger.warning(f"{order} is not a valid response object.")
                                        return
                                    filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                    if filtered_orders:
                                        oobj = filtered_orders[0]
                                        oobj.update_from_ccxt_object(order) ->
                                        {{}
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
                                                self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                            self.ft_is_open = True
                                            if self.status in ('closed', 'canceled', 'cancelled'):
                                                self.ft_is_open = False
                                                if order.get('filled', 0) > 0:
                                                    self.order_filled_date = arrow.utcnow().datetime
                                            self.order_update_date = arrow.utcnow().datetime
                                        }
                                    else:
                                        logger.warning(f"Did not find order for {order}.")
                                }
                            }
                        # We check if stoploss order is fulfilled
                        if stoploss_order and stoploss_order['status'] in ('closed', 'triggered'):
                            trade.sell_reason = SellType.STOPLOSS_ON_EXCHANGE.value
                            self.update_trade_state(trade, trade.stoploss_order_id, stoploss_order, stoploss_order=True) ->
                            {{}
                                if not order_id:
                                    logger.warning(f'Orderid for trade {trade} is empty.')
                                    return False
                                logger.info('Found open order for %s', trade)
                                try:
                                    order = action_order or self.exchange.fetch_order_or_stoploss_order(order_id, trade.pair, stoploss_order) ->
                                    {{}
                                        if stoploss_order:
                                            return self.fetch_stoploss_order(order_id, pair) ->
                                            {{}
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
                                            }
                                        return self.fetch_order(order_id, pair) ->
                                        {{}
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
                                        }

                                    }
                                except InvalidOrderException as exception:
                                    logger.warning('Unable to fetch order %s: %s', order_id, exception)
                                    return False
                                trade.update_order(order) ->
                                {{}
                                    Order.update_orders(self.orders, order) ->
                                    {{}
                                        if not isinstance(order, dict):
                                            logger.warning(f"{order} is not a valid response object.")
                                            return
                                        filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                        if filtered_orders:
                                            oobj = filtered_orders[0]
                                            oobj.update_from_ccxt_object(order) ->
                                            {{}
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
                                                    self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                                self.ft_is_open = True
                                                if self.status in ('closed', 'canceled', 'cancelled'):
                                                    self.ft_is_open = False
                                                    if order.get('filled', 0) > 0:
                                                        self.order_filled_date = arrow.utcnow().datetime
                                                self.order_update_date = arrow.utcnow().datetime
                                            }
                                        else:
                                            logger.warning(f"Did not find order for {order}.")
                                    }
                                }
                                # Try update amount (binance-fix)
                                try:
                                    new_amount = self.get_real_amount(trade, order)
                                    if not isclose(safe_value_fallback(order, 'filled', 'amount'), new_amount,abs_tol=constants.MATH_CLOSE_PREC):
                                        order['amount'] = new_amount
                                        order.pop('filled', None)
                                        trade.recalc_open_trade_value()
                                except DependencyException as exception:
                                    logger.warning("Could not update trade amount: %s", exception)

                                if self.exchange.check_order_canceled_empty(order):
                                    return True
                                trade.update(order)
                                if not trade.is_open:
                                    self.protections.stop_per_pair(trade.pair)
                                    self.protections.global_stop()
                                    self.wallets.update()
                                return False
                            }
                            self.strategy.lock_pair(trade.pair, datetime.now(timezone.utc), reason='Auto lock')
                            self._notify_sell(trade, "stoploss")
                            return True

                        if trade.open_order_id or not trade.is_open:
                            # Trade has an open Buy or Sell order, Stoploss-handling can't happen in this case
                            # as the Amount on the exchange is tied up in another trade.
                            # The trade can be closed already (sell-order fill confirmation came in this iteration)
                            return False

                        if not stoploss_order:
                            stoploss = self.edge.stoploss(pair=trade.pair) if self.edge else self.strategy.stoploss ->
                            {{}
                                limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
                                limit_rate = stop_price * limit_price_pct
                                ordertype = "stop"
                                stop_price = self.price_to_precision(pair, stop_price)

                                if self._config['dry_run']:
                                    dry_order = self.dry_run_order(pair, ordertype, "sell", amount, stop_price) ->
                                    {{}
                                        order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                        self._store_dry_order(dry_order, pair) ->
                                        {{}
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
                                        }
                                        return dry_order
                                    }
                                    return dry_order

                                params = self._params.copy()
                                if order_types.get('stoploss', 'market') == 'limit':
                                    params['orderPrice'] = limit_rate
                                amount = self.amount_to_precision(pair, amount)
                                order = self._api.create_order(symbol=pair, type=ordertype, side='sell',
                                                               amount=amount, price=stop_price, params=params) ->
                                {{}
                                    try:
                                        amount = self.amount_to_precision(pair, amount)
                                        needs_price = (ordertype != 'market'
                                                       or self._api.options.get("createMarketBuyOrderRequiresPrice", False))

                            			rate_for_order = self.price_to_precision(pair, rate) if needs_price else None
                            			# create order and send to api for execution
                                        return self._api.create_order(pair, ordertype, side,
                                                                      amount, rate_for_order, params)
                                }
                                return order
                            }
                            stop_price = trade.open_rate * (1 + stoploss)
                            if self.create_stoploss_order(trade=trade, stop_price=stop_price): ->
                                {{}
                                    stoploss_order = self.exchange.stoploss(pair=trade.pair, amount=trade.amount,
                                                    stop_price=stop_price,
                                                    order_types=self.strategy.order_types) ->
                                    {{}
                                        limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
                                        limit_rate = stop_price * limit_price_pct
                                        ordertype = "stop"
                                        stop_price = self.price_to_precision(pair, stop_price)

                                        if self._config['dry_run']:
                                            dry_order = self.dry_run_order(pair, ordertype, "sell", amount, stop_price) ->
                                            {{}
                                                order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                                self._store_dry_order(dry_order, pair) ->
                                                {{}
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
                                                }
                                                return dry_order
                                            }
                                            return dry_order
                                        try:
                                            params = self._params.copy()
                                            if order_types.get('stoploss', 'market') == 'limit':
                                                params['orderPrice'] = limit_rate
                                            amount = self.amount_to_precision(pair, amount)
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
                                    }
                                    order_obj = Order.parse_from_ccxt_object(stoploss_order, trade.pair, 'stoploss')
                                    trade.orders.append(order_obj)
                                    trade.stoploss_order_id = str(stoploss_order['id'])
                                    return True
                                }
                                trade.stoploss_last_update = datetime.utcnow()
                                return False

                        if stoploss_order and stoploss_order['status'] in ('canceled', 'cancelled'):
                            if self.create_stoploss_order(trade=trade, stop_price=trade.stop_loss): ->
                            {{}
                                stoploss_order = self.exchange.stoploss(pair=trade.pair, amount=trade.amount,
                                                stop_price=stop_price,
                                                order_types=self.strategy.order_types) ->
                                {{}
                                    limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
                                    limit_rate = stop_price * limit_price_pct
                                    ordertype = "stop"
                                    stop_price = self.price_to_precision(pair, stop_price)

                                    if self._config['dry_run']:
                                        dry_order = self.dry_run_order(pair, ordertype, "sell", amount, stop_price) ->
                                        {{}
                                            order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                            self._store_dry_order(dry_order, pair) ->
                                            {{}
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
                                            }
                                            return dry_order
                                        }
                                        return dry_order
                                    try:
                                        params = self._params.copy()
                                        if order_types.get('stoploss', 'market') == 'limit':
                                            params['orderPrice'] = limit_rate
                                        amount = self.amount_to_precision(pair, amount)
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
                                }
                                order_obj = Order.parse_from_ccxt_object(stoploss_order, trade.pair, 'stoploss')
                                trade.orders.append(order_obj)
                                trade.stoploss_order_id = str(stoploss_order['id'])
                                return True
                            }
                                return False
                            else:
                                trade.stoploss_order_id = None
                                logger.warning('Stoploss order was cancelled, but unable to recreate one.')

                        if stoploss_order and (self.config.get('trailing_stop', False)
                               or self.config.get('use_custom_stoploss', False)):
                            self.handle_trailing_stoploss_on_exchange(trade, stoploss_order) ->
                            {{}
                                if self.exchange.stoploss_adjust(trade.stop_loss, order):
                                    update_beat = self.strategy.order_types.get('stoploss_on_exchange_interval', 60)
                                    if (datetime.utcnow() - trade.stoploss_last_update).total_seconds() >= update_beat:
                                        logger.info(f"Cancelling current stoploss on exchange for pair {trade.pair} "
                                                    f"(orderid:{order['id']}) in order to add another one ...")
                                        try:
                                            co = self.exchange.cancel_stoploss_order(order['id'], trade.pair) ->
                                            {{}
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
                                            }
                                            trade.update_order(co)
                                            {{}
                                                Order.update_orders(self.orders, order) ->
                                                {{}
                                                    if not isinstance(order, dict):
                                                        logger.warning(f"{order} is not a valid response object.")
                                                        return
                                                    filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                                    if filtered_orders:
                                                        oobj = filtered_orders[0]
                                                        oobj.update_from_ccxt_object(order) ->
                                                        {{}
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
                                                                self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                                            self.ft_is_open = True
                                                            if self.status in ('closed', 'canceled', 'cancelled'):
                                                                self.ft_is_open = False
                                                                if order.get('filled', 0) > 0:
                                                                    self.order_filled_date = arrow.utcnow().datetime
                                                            self.order_update_date = arrow.utcnow().datetime
                                                        }
                                                    else:
                                                        logger.warning(f"Did not find order for {order}.")
                                                }
                                            }
                                        except InvalidOrderException:
                                            logger.exception(f"Could not cancel stoploss order {order['id']} "
                                                             f"for pair {trade.pair}")
                                    if not self.create_stoploss_order(trade=trade, stop_price=trade.stop_loss): ->
                                    {{}
                                        try:
                                            stoploss_order = self.exchange.stoploss(pair=trade.pair, amount=trade.amount,
                                                            stop_price=stop_price,
                                                            order_types=self.strategy.order_types) ->
                                            {{}
                                                limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
                                                limit_rate = stop_price * limit_price_pct
                                                ordertype = "stop"
                                                stop_price = self.price_to_precision(pair, stop_price)

                                                if self._config['dry_run']:
                                                    dry_order = self.dry_run_order(pair, ordertype, "sell", amount, stop_price) ->
                                                    {{}
                                                        order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                                        self._store_dry_order(dry_order, pair) ->
                                                        {{}
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
                                                        }
                                                        return dry_order
                                                    }
                                                    return dry_order
                                                try:
                                                    params = self._params.copy()
                                                    if order_types.get('stoploss', 'market') == 'limit':
                                                        params['orderPrice'] = limit_rate
                                                    amount = self.amount_to_precision(pair, amount)
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
                                            }
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
                                    }
                                        logger.warning(f"Could not create trailing stoploss order "
                                                       f"for pair {trade.pair}.")
                            }
                        return False

                    def handle_trade(self, trade: Trade) -> bool:
                        (buy, sell) = (False, False)
                        config_ask_strategy = self.config.get('ask_strategy', {})

                        if (config_ask_strategy.get('use_sell_signal', True) or config_ask_strategy.get('ignore_roi_if_buy_signal', False)):
                            analyzed_df, _ = self.dataprovider.get_analyzed_dataframe(trade.pair, self.strategy.timeframe) ->
                            {{}
                                if (pair, timeframe) in self.__cached_pairs:
                                    return self.__cached_pairs[(pair, timeframe)]
                                else:
                                    return (DataFrame(), datetime.fromtimestamp(0, tz=timezone.utc))
                            }
                            (buy, sell) = self.strategy.get_signal(trade.pair, self.strategy.timeframe, analyzed_df) ->
                            {{}
                                if not isinstance(dataframe, DataFrame) or dataframe.empty:
                                    logger.warning(f'Empty candle (OHLCV) data for pair {pair}')
                                    return False, False
                                latest_date = dataframe['date'].max()
                                latest = dataframe.loc[dataframe['date'] == latest_date].iloc[-1]
                                latest_date = arrow.get(latest_date)
                                # ccxt.Exchange.parse_timeframe(timeframe) // 60
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
                                # ccxt.Exchange.parse_timeframe(timeframe)
                                timeframe_seconds = timeframe_to_seconds(timeframe)
                                if self.ignore_expired_candle(latest_date=latest_date,
                                                              current_time=datetime.now(timezone.utc),
                                                              timeframe_seconds=timeframe_seconds,
                                                              buy=buy): ->
                                {{}
                                    if self.ignore_buying_expired_candle_after and buy:
                                        time_delta = current_time - (latest_date + timedelta(seconds=timeframe_seconds))
                                        return time_delta.total_seconds() > self.ignore_buying_expired_candle_after
                                    else:
                                        return False
                                }
                                    return False, sell
                                return buy, sell
                            }

                        if config_ask_strategy.get('use_order_book', False):
                            order_book_min = config_ask_strategy.get('order_book_min', 1)
                            order_book_max = config_ask_strategy.get('order_book_max', 1)
                            logger.debug(f'Using order book between {order_book_min} and {order_book_max} '
                                         f'for selling {trade.pair}...')
                            order_book = self._order_book_gen(trade.pair, f"{config_ask_strategy['price_side']}s",
                                                              order_book_min=order_book_min,
                                                              order_book_max=order_book_max)
                            {{}
                                order_book = self.exchange.fetch_l2_order_book(pair, order_book_max)
                                for i in range(order_book_min, order_book_max + 1):
                                    yield order_book[side][i - 1][0]
                            }
                            for i in range(order_book_min, order_book_max + 1):
                                sell_rate = next(order_book)
                                self._sell_rate_cache[trade.pair] = sell_rate
                                if self._check_and_execute_sell(trade, sell_rate, buy, sell): ->
                                {{}
                                    should_sell = self.strategy.should_sell(
                                        trade, sell_rate, datetime.now(timezone.utc), buy, sell,
                                        force_stoploss=self.edge.stoploss(trade.pair) if self.edge else 0 ->
                                        {{}
                                            limit_price_pct = order_types.get('stoploss_on_exchange_limit_ratio', 0.99)
                                            limit_rate = stop_price * limit_price_pct
                                            ordertype = "stop"
                                            stop_price = self.price_to_precision(pair, stop_price)

                                            if self._config['dry_run']:
                                                dry_order = self.dry_run_order(pair, ordertype, "sell", amount, stop_price) ->
                                                {{}
                                                    order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                                    self._store_dry_order(dry_order, pair) ->
                                                    {{}
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
                                                    }
                                                    return dry_order
                                                }
                                                return dry_order

                                            params = self._params.copy()
                                            if order_types.get('stoploss', 'market') == 'limit':
                                                params['orderPrice'] = limit_rate
                                            amount = self.amount_to_precision(pair, amount)
                                            order = self._api.create_order(symbol=pair, type=ordertype, side='sell',
                                                                           amount=amount, price=stop_price, params=params)
                                            return order
                                        }
                                    )
                                    if should_sell.sell_flag:
                                        logger.info(f'Executing Sell for {trade.pair}. Reason: {should_sell.sell_type}')
                            			# 015242 Executes a limit sell for the given trade and limit
                            			self.execute_sell(trade, sell_rate, should_sell.sell_type) ->
                                        {{}
                                            sell_type = 'sell'
                                            if sell_reason in (SellType.STOP_LOSS, SellType.TRAILING_STOP_LOSS):
                                                sell_type = 'stoploss'

                                            if self.config['dry_run'] and sell_type == 'stoploss' \
                                               and self.strategy.order_types['stoploss_on_exchange']:
                                                limit = trade.stop_loss

                                            if self.strategy.order_types.get('stoploss_on_exchange') and trade.stoploss_order_id:
                                                try:
                                                    self.exchange.cancel_stoploss_order(trade.stoploss_order_id, trade.pair) ->
                                                    {{}
                                                        if self._config['dry_run']:
                                                            return {}
                                                        try:
                                                            return self._api.cancel_order(order_id, pair, params={'type': 'stop'})
                                                    }
                                                except InvalidOrderException:
                                                    logger.exception(f"Could not cancel stoploss order {trade.stoploss_order_id}")

                                            order_type = self.strategy.order_types[sell_type]
                                            if sell_reason == SellType.EMERGENCY_SELL:
                                                order_type = self.strategy.order_types.get("emergencysell", "market")
                                            if sell_reason == SellType.FORCE_SELL:
                                                order_type = self.strategy.order_types.get("forcesell", order_type)

                                            amount = self._safe_sell_amount(trade.pair, trade.amount) ->
                                            {{}
                                                self.wallets.update()
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
                                            }

                                            time_in_force = self.strategy.order_time_in_force['sell']

                                            if not strategy_safe_wrapper(self.strategy.confirm_trade_exit, default_retval=True)(
                                                    pair=trade.pair, trade=trade, order_type=order_type, amount=amount, rate=limit,
                                                    time_in_force=time_in_force,
                                                    sell_reason=sell_reason.value):
                                                logger.info(f"User requested abortion of selling {trade.pair}")
                                                return False

                                            try:
                                                order = self.exchange.sell(pair=trade.pair,
                                                                           ordertype=order_type,
                                                                           amount=amount, rate=limit,
                                                                           time_in_force=time_in_force
                                                                           ) ->
                                                {{}
                                                    if self._config['dry_run']:
                                                        dry_order = self.dry_run_order(pair, ordertype, "sell", amount, rate) ->
                                                        {{}
                                                            order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                                            self._store_dry_order(dry_order, pair) ->
                                                            {{}
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
                                                            }
                                                            return dry_order
                                                        }
                                                        return dry_order

                                                    params = self._params.copy()
                                                    if time_in_force != 'gtc' and ordertype != 'market':
                                                        params.update({'timeInForce': time_in_force})
                                                    return self.create_order(pair, ordertype, 'sell', amount, rate, params) ->
                                                    {{}
                                                        try:
                                                            amount = self.amount_to_precision(pair, amount)
                                                            needs_price = (ordertype != 'market'
                                                                           or self._api.options.get("createMarketBuyOrderRequiresPrice", False))

                                                			rate_for_order = self.price_to_precision(pair, rate) if needs_price else None
                                                            return self._api.create_order(pair, ordertype, side,
                                                                                          amount, rate_for_order, params)
                                                    }
                                                }
                                            except InsufficientFundsError as e:
                                                logger.warning(f"Unable to place order {e}.")
                                                self.handle_insufficient_funds(trade)
                                                return False

                                            order_obj = Order.parse_from_ccxt_object(order, trade.pair, 'sell')
                                            trade.orders.append(order_obj)

                                            trade.open_order_id = order['id']
                                            trade.sell_order_status = ''
                                            trade.close_rate_requested = limit
                                            trade.sell_reason = sell_reason.value
                                            if order.get('status', 'unknown') == 'closed':
                                                self.update_trade_state(trade, trade.open_order_id, order) ->
                                                {{}
                                                    if not order_id:
                                                        logger.warning(f'Orderid for trade {trade} is empty.')
                                                        return False
                                                    logger.info('Found open order for %s', trade)
                                                    try:
                                                        order = action_order or self.exchange.fetch_order_or_stoploss_order(order_id, trade.pair, stoploss_order) ->
                                                        {{}
                                                            if stoploss_order:
                                                                return self.fetch_stoploss_order(order_id, pair) ->
                                                                {{}
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
                                                                }
                                                            return self.fetch_order(order_id, pair) ->
                                                            {{}
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
                                                            }

                                                        }
                                                    except InvalidOrderException as exception:
                                                        logger.warning('Unable to fetch order %s: %s', order_id, exception)
                                                        return False
                                                    trade.update_order(order) ->
                                                    {{}
                                                        Order.update_orders(self.orders, order) ->
                                                        {{}
                                                            if not isinstance(order, dict):
                                                                logger.warning(f"{order} is not a valid response object.")
                                                                return
                                                            filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                                            if filtered_orders:
                                                                oobj = filtered_orders[0]
                                                                oobj.update_from_ccxt_object(order) ->
                                                                {{}
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
                                                                        self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                                                    self.ft_is_open = True
                                                                    if self.status in ('closed', 'canceled', 'cancelled'):
                                                                        self.ft_is_open = False
                                                                        if order.get('filled', 0) > 0:
                                                                            self.order_filled_date = arrow.utcnow().datetime
                                                                    self.order_update_date = arrow.utcnow().datetime
                                                                }
                                                            else:
                                                                logger.warning(f"Did not find order for {order}.")
                                                        }
                                                    }
                                                    try:
                                                        new_amount = self.get_real_amount(trade, order)
                                                        if not isclose(safe_value_fallback(order, 'filled', 'amount'), new_amount,abs_tol=constants.MATH_CLOSE_PREC):
                                                            order['amount'] = new_amount
                                                            order.pop('filled', None)
                                                            trade.recalc_open_trade_value()

                                                    except DependencyException as exception:
                                                        logger.warning("Could not update trade amount: %s", exception)
                                                    if self.exchange.check_order_canceled_empty(order):
                                                        return True
                                                    trade.update(order)
                                                    if not trade.is_open:
                                                        self.protections.stop_per_pair(trade.pair)
                                                        self.protections.global_stop()
                                                        self.wallets.update()
                                                    return False
                                                }
                                            Trade.session.flush()
                                            self.strategy.lock_pair(trade.pair, datetime.now(timezone.utc),
                                                                    reason='Auto lock')

                                            self._notify_sell(trade, order_type)

                                            return True
                                        }
                                        return True
                                    return False
                                }
                                    return True
                        else:
                            sell_rate = self.get_sell_rate(trade.pair, True)
                            if self._check_and_execute_sell(trade, sell_rate, buy, sell):
                                return True

                        logger.debug('Found no sell signal for %s.', trade)
                        return False

        if self.get_free_open_trades(): ->
            {{}
                #Return the number of free open trades slots or 0 if
                #max number of open trades reached
                open_trades = len(Trade.get_open_trades()) ->
                {{}
                    #Query trades from persistence layer
                    return Trade.get_trades(Trade.is_open.is_(True)).all() ->
                    {{}
                        if trade_filter is not None:
                            if not isinstance(trade_filter, list):
                                trade_filter = [trade_filter]
                            return Trade.query.filter(*trade_filter)
                        else:
                            return Trade.query
                    }
                }
                return max(0, self.config['max_open_trades'] - open_trades)
            }
        	def enter_positions() ->
            {
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
        		for trade in Trade.get_open_trades(): ->
                {{}
                    #Query trades from persistence layer
                    return Trade.get_trades(Trade.is_open.is_(True)).all() ->
                    {{}
                        if trade_filter is not None:
                            if not isinstance(trade_filter, list):
                                trade_filter = [trade_filter]
                            return Trade.query.filter(*trade_filter)
                        else:
                            return Trade.query
                    }
                }
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

        				trades_created += self.create_trade(pair) ->
                        {
                            #Check the implemented trading strategy for buy signals.\
                            #If the pair triggers the buy signal a new trade record gets created
                            #and the buy-order opening the trade gets issued towards the exchange.

                            #:return: True if a trade has been created.

                            logger.debug(f"create_trade for pair {pair}")

                            analyzed_df, _ = self.dataprovider.get_analyzed_dataframe(pair, self.strategy.timeframe)
                            {{}
                                #:param pair: pair to get the data for
                                #:param timeframe: timeframe to get data for
                                #:return: Tuple of (Analyzed Dataframe, lastrefreshed) for the requested pair / timeframe
                                #    combination.
                                #    Returns empty dataframe and Epoch 0 (1970-01-01) if no dataframe was cached.

                                if (pair, timeframe) in self.__cached_pairs:
                                    return self.__cached_pairs[(pair, timeframe)]
                                else:
                                    return (DataFrame(), datetime.fromtimestamp(0, tz=timezone.utc))
                            }
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
                            if not self.get_free_open_trades(): ->
                            {{}
                                #Return the number of free open trades slots or 0 if
                                  #max number of open trades reached
                            	  # 014 get_open_trades return amount of total opentrade, which has been bought
                            	  # Trade.get_trades(Trade.is_open.is_(True)).all()
                                  open_trades = len(Trade.get_open_trades()) ->
                                  {{}
                                      #Query trades from persistence layer
                                      return Trade.get_trades(Trade.is_open.is_(True)).all() ->
                                      {{}
                                          if trade_filter is not None:
                                              if not isinstance(trade_filter, list):
                                                  trade_filter = [trade_filter]
                                              return Trade.query.filter(*trade_filter)
                                          else:
                                              return Trade.query
                                      }
                                  }
                                  return max(0, self.config['max_open_trades'] - open_trades)
                            }
                                logger.debug(f"Can't open a new trade for {pair}: max number of trades is reached.")
                                return False

                            # running get_signal on historical data fetched
                            (buy, sell) = self.strategy.get_signal(pair, self.strategy.timeframe, analyzed_df) ->
                            {{}
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

                                if self.ignore_expired_candle(latest_date=latest_date,
                                                              current_time=datetime.now(timezone.utc),
                                                              timeframe_seconds=timeframe_seconds,
                                                              buy=buy): ->
                                {{}
                                    if self.ignore_buying_expired_candle_after and buy:
                                        time_delta = current_time - (latest_date + timedelta(seconds=timeframe_seconds))
                                        return time_delta.total_seconds() > self.ignore_buying_expired_candle_after
                                    else:
                                        return False
                                }
                                    return False, sell
                                return buy, sell
                            }

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
                                    if self._check_depth_of_market_buy(pair, bid_check_dom): ->
                                    {{}
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
                                    }
                                        logger.info(f'Executing Buy for {pair}.')
                    					# 712
                                        return self.execute_buy(pair, stake_amount) ->
                                        {{}
                                            #Executes a limit buy for the given pair
                                            #:param pair: pair for which we want to create a LIMIT_BUY
                                            #:return: True if a buy order is created, false if it fails.
                                            time_in_force = self.strategy.order_time_in_force['buy']

                                            if price:
                                                buy_limit_requested = price
                                            else:
                                                # 7121 Calculate price
                                    			# Calculates bid target between current ask price and last price
                                                # get the price based on order_book
                                                buy_limit_requested = self.get_buy_rate(pair, True) ->
                                                {{}
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
                                                }

                                            if not buy_limit_requested:
                                                raise PricingError('Could not determine buy price.')
                                    		# 7122 //get the min stake amount
                                            min_stake_amount = self.exchange.get_min_pair_stake_amount(pair, buy_limit_requested,
                                                                                                       self.strategy.stoploss) ->
                                            {{}
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
                                            }
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
                                            amount = self.exchange.amount_to_precision(pair, amount) ->
                                            {{}
                                                #Returns the amount to buy or sell to a precision the Exchange accepts
                                                #Reimplementation of ccxt internal methods - ensuring we can test the result is correct
                                                #based on our definitions.

                                                if self.markets[pair]['precision']['amount']:
                                                    amount = float(decimal_to_precision(amount, rounding_mode=TRUNCATE,
                                                                                        precision=self.markets[pair]['precision']['amount'],
                                                                                        counting_mode=self.precisionMode,
                                                                                        ))

                                                return amount
                                            }
                                    		# 7124 buy using create_order
                                            order = self.exchange.buy(pair=pair, ordertype=order_type,
                                                                      amount=amount, rate=buy_limit_requested,
                                                                      time_in_force=time_in_force) ->
                                            {{}
                                                if self._config['dry_run']:
                                        			# 01524231
                                                    dry_order = self.dry_run_order(pair, ordertype, "buy", amount, rate) ->
                                                    {{}
                                                        order_id = f'dry_run_{side}_{datetime.now().timestamp()}'
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
                                                        self._store_dry_order(dry_order, pair) ->
                                                        {{}
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
                                                        }
                                                        return dry_order
                                                    }

                                                    return dry_order

                                                params = self._params.copy()
                                                if time_in_force != 'gtc' and ordertype != 'market':
                                                    params.update({'timeInForce': time_in_force})
                                        		# 01524232
                                                return self.create_order(pair, ordertype, 'buy', amount, rate, params) ->
                                                {{}
                                                    try:
                                                        amount = self.amount_to_precision(pair, amount)
                                                        needs_price = (ordertype != 'market'
                                                                       or self._api.options.get("createMarketBuyOrderRequiresPrice", False))

                                                        rate_for_order = self.price_to_precision(pair, rate) if needs_price else None
                                                        return self._api.create_order(pair, ordertype, side,
                                                                                      amount, rate_for_order, params)
                                                }
                                            }
                                            order_obj = Order.parse_from_ccxt_object(order, pair, 'buy') ->
                                            {{}
                                                o = Order(order_id=str(order['id']), ft_order_side=side, ft_pair=pair)
                                        		# 015121
                                                o.update_from_ccxt_object(order) ->
                                                {{}
                                                    #Update Order from ccxt response
                                                    #Only updates if fields are available from ccxt -

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
                                                }
                                                return o
                                            }
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
                                                {{}
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
                                                                                                                            stoploss_order) ->
                                                        {{}
                                                            if stoploss_order:
                                                                return self.fetch_stoploss_order(order_id, pair) ->
                                                                {{}
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
                                                                }
                                                            return self.fetch_order(order_id, pair) ->
                                                            {{}
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
                                                            }
                                                        }
                                                    except InvalidOrderException as exception:
                                                        logger.warning('Unable to fetch order %s: %s', order_id, exception)
                                                        return False
                                            		# 01512 Get all non-closed orders - useful when trying to batch-update orders
                                                    trade.update_order(order) ->
                                                    {{}
                                                        Order.update_orders(self.orders, order) ->
                                                        {{}
                                                            if not isinstance(order, dict):
                                                                logger.warning(f"{order} is not a valid response object.")
                                                                return
                                                            filtered_orders = [o for o in orders if o.order_id == order.get('id')]
                                                            if filtered_orders:
                                                                oobj = filtered_orders[0]
                                                                oobj.update_from_ccxt_object(order) ->
                                                                {{}
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
                                                                        self.order_date = datetime.fromtimestamp(order['timestamp'] / 1000, tz=timezone.utc)
                                                                    self.ft_is_open = True
                                                                    if self.status in ('closed', 'canceled', 'cancelled'):
                                                                        self.ft_is_open = False
                                                                        if order.get('filled', 0) > 0:
                                                                            self.order_filled_date = arrow.utcnow().datetime
                                                                    self.order_update_date = arrow.utcnow().datetime
                                                                }
                                                            else:
                                                                logger.warning(f"Did not find order for {order}.")
                                                        }
                                                    }

                                                    # Try update amount (binance-fix)
                                                    try:
                                            			# 01321 Detect and update trade fee.
                                                    	#Calls trade.update_fee() uppon correct detection.
                                                    	#Returns modified amount if the fee was taken from the destination currency.
                                                    	#Necessary for exchanges which charge fees in base currency (e.g. binance)
                                                        new_amount = self.get_real_amount(trade, order) ->
                                                        {{}
                                                            #Detect and update trade fee.
                                                            #Calls trade.update_fee() uppon correct detection.
                                                            #Returns modified amount if the fee was taken from the destination currency.
                                                            #Necessary for exchanges which charge fees in base currency (e.g. binance)
                                                            #:return: identical (or new) amount for the trade

                                                            # Init variables
                                                            order_amount = safe_value_fallback(order, 'filled', 'amount')
                                                            # Only run for closed orders
                                                    		# 013211 Verify if this side (buy / sell) has already been updated
                                                            if trade.fee_updated(order.get('side', '')) or order['status'] == 'open': ->
                                                            {{}
                                                                #Verify if this side (buy / sell) has already been updated
                                                                if side == 'buy':
                                                                    return self.fee_open_currency is not None
                                                                elif side == 'sell':
                                                                    return self.fee_close_currency is not None
                                                                else:
                                                                    return False
                                                            }
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
                                                        }
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
                                                }
                                            Trade.session.add(trade)
                                            Trade.session.flush()

                                            # Updating wallets
                                            self.wallets.update()

                                            self._notify_buy(trade, order_type)

                                            return True
                                        }
                                    else:
                                        return False

                                logger.info(f'Executing Buy for {pair}')
                                return self.execute_buy(pair, stake_amount)
                            else:
                                return False
                        }
        			except DependencyException as exception:
        				logger.warning('Unable to create trade for %s: %s', pair, exception)

        		if not trades_created:
        			logger.debug("Found no buy signals for whitelisted currencies. Trying again...")

        		return trades_created
            }
