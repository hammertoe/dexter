# dexter
A tool for creating orders on the XRP Ledger DEX


## Installation

Create a virtual environment, install xrp-py, and run dexter:

```python
python3 -m venv venv
./venv/bin/activate
python dexter.py
```

This was created as part of the Ripple Innovate hackathon.

## Plan

To be clear, my vision of this is not to be a general trading bot. At least not for this hackathon, but to be a tool for easily adding liquidity on the testnet DEX for a specified currency pair. I'm thinking the 'phases' as such of evolution will go something like:

1. script to run manually, as a one-off, given the key to an account and a currency pair places offers on the book for that pair
2. ability to configure/plug in different strategies to above e.g. 'place 5 bids/asks at 20 basis points above and below the mid price'
3. UI for the above script
4. Enable script to run continuously as a market maker, cancelling existing orders and placing new ones
5. More logic for the above to allow additional strategies
6. ...
7. profit?!