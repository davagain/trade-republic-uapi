"""Restrict the wrapper; this does not narrow permissions of the broker session."""
READ_ROUTES=frozenset({'/api/portfolio','/api/accounts','/api/transactions','/api/orders',
    '/api/search-instruments','/api/instrument','/api/instrument-history',
    '/api/accounts-history','/api/schedule-exchange','/api/tr-instrument',
    '/api/order-price','/api/order-fees','/api/price-alarms','/api/accounts-activity'})

def allowed(path,allow_writes=False):
    return allow_writes or path in READ_ROUTES
