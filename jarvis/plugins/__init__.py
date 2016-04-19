def get_plugins(slack):
    from .cash_pool import CashPool
    from .download import Download
    from .location import Location
    from .ship_it import ShipIt
    from .status import Status

    return [
        CashPool(slack),
        Download(slack),
        Location(slack),
        ShipIt(slack),
        Status(slack),
    ]
