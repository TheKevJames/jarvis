def get_plugins(slack):
    from jarvis.plugins.cash_pool import CashPool
    from jarvis.plugins.download import Download
    from jarvis.plugins.location import Location
    from jarvis.plugins.ship_it import ShipIt
    from jarvis.plugins.status import Status

    return [
        CashPool(slack),
        Download(slack),
        Location(slack),
        ShipIt(slack),
        Status(slack),
    ]
