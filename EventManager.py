###################
# Time Management #
###################

class EventManager(object):
    '''
    Manager for periodic events.

    parameters

    period: integer            
        number of business days between events
        default: 1

    max_daily_hits: integer
        upper limit on the number of times per day the event is triggered.
        (trading controls could work for this too)
        default: 1

    trade_timing_func: function (returns a boolean)
        decision function for timimng an intraday entry point
    '''

    def __init__(self, 
                 period=1,
                 max_daily_hits=1,
                 frequency = '1m',
                 trade_timing_func=None):
        
        self.period = period
        self.max_daily_hits = max_daily_hits
        self.remaining_hits = max_daily_hits
        self._trade_timing_func = trade_timing_func
        self.next_event_date = None
        self.market_open = None
        self.market_close = None
        self.frequency = frequency
    
    @property
    def todays_index(self):
        dt = calendar.canonicalize_datetime(get_datetime())
        return calendar.trading_days.searchsorted(dt)
    
    def open_and_close(self, dt):
        return calendar.open_and_closes.T[dt]
        
    def format_datetime(self, dt):
        # if in minute mode, dt is datetime.datetime
        # if in daily mode, dt is datetime.date
        tmp = { 
            '1m': lambda x: x, 
            '1d': lambda x: x.date() if x is not None else x,
        }[self.frequency](dt)
        return tmp
        
    def signal(self, *args, **kwargs):
        '''
        Entry point for the rule_func
        All arguments are passed to rule_func
        '''
        now = get_datetime()
        dt = calendar.canonicalize_datetime(get_datetime())
        if self.next_event_date is None:
            self.next_event_date = dt
            times = self.open_and_close(dt)
            self.market_open = times['market_open'] 
            self.market_close = times['market_close'] 
        if self.format_datetime(now) < self.format_datetime(self.market_open):
            return False
        #print self.format_datetime(now) >= self.format_datetime(self.market_close)
        if (self.frequency == '1m'):
            # decide if it is the entry time for today's trading
            decision = self._trade_timing_func(*args, **kwargs)
            if decision:
                self.remaining_hits -= 1
                self.set_next_event_date()
        elif (self.frequency == '1d'):
            decision = self.format_datetime(now) >= \
                self.format_datetime(self.market_close)
            if decision:
                self.set_next_event_date()
        return decision
    
    def set_next_event_date(self):
        self.remaining_hits = self.max_daily_hits
        tdays = calendar.trading_days
        idx = self.todays_index + self.period
        self.next_event_date = tdays[idx]
        times = self.open_and_close(self.next_event_date)
        self.market_open = times['market_open']
        self.market_close = times['market_close']
        
    

def entry_func(dt):
    '''
    rule_func passed to EventManager for 
    an intraday entry decision.
    '''
    dt = dt.astimezone(timezone('US/Eastern'))
    return dt.hour == 11 and dt.minute <= 30 
    
# Global instance of the EventManager
trade_manager = EventManager(period=21, frequency = '1d', 
                             trade_timing_func=entry_func)