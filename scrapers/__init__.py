from . import airdropalert
from . import coingecko
from . import coinmarketcap
from . import cryptorank
from . import icodrops
from . import icoholder
from . import etherscan


generator_functions = {
    'Airdropalert': airdropalert.start,
    'Coingecko': coingecko.start,
    'Coinmarketcap': coinmarketcap.start,
    'Cryptorank': cryptorank.start,
    'Etherscan': etherscan.start,
    'Icodrops': icodrops.start,
    'Icoholder': icoholder.start
}
