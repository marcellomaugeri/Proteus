## Technical Documentation

### Data Analysis Track
The aim of the Quant Analysis track of this project is to analyse the data from the Aave V3 protocol in the Polygon chain.
The Aave V3 protocol data is taken from BigQuery and can be accessed using the demeter-fetch library.
The volatility data from the Polygon chain is taken from CoinGecko.
Due to time constraints, all data and experiments refer to June 2024, but the same methodology can be applied to real-time data using appropriate APIs.
This is left as future work.

### Prerequisites
Before getting started, data must be fetched by using demeter-fetch.
For convenience, a copy of such a data is provided in the data folder, under the sample folder.
If you still want to acquire data by yourself, please follow the next paragraph.

#### Use demeter-fetch to get data from BigQuery
The version of demeter-fetch in PyPi has some bugs.
As a consequence, it is suggested to run it from source code.

```
# Clone the repository
git clone https://github.com/zelos-alpha/demeter-fetch
# Install requirements (Python >= 3.11)
pip install -r demeter-fetch/requirements.txt
```

Then you need to setup a Google Cloud project, and create a service user with BigQuery admin permissions and download the credentials in JSON format.
Rename the file bigquerykey.json and keep it in the same folder as config.aave.toml file.
```
# Finally, run demeter-fetch with the provided config file
python3 demeter-fetch/main.py -c config.aave.toml
```
The output will be in a sample folder.
Move the folder in the data folder and continue.
Now you can open the Jupyter notebook.

### 1 - Jupyter Notebook / Quant Track
This folder contains a Jupyter notebook that analyzes the data from the Aave V3 protocol.
The objective is to analyse trend, potential indicator for an effective lending strategy.
The document is already self-explanatory and detailed.

### 2 - Simple Backtest / Quant Track
To let all test off-chains, Demeter have been used as backtesting framework.
The file `2_simple_backtest.py` shows how to backtest a strategy in Aave V3.

### 3 - Proteus Agent / Agent Track
The file `3_demo_agent.py` shows Proteus Agent in action.
The agent simply uses the network to borrow and repay tokens.

### 4 - Proteus Optimizer / Agent Track
The file `4_demo_optimizer.py` shows Proteus Optimizer in action.
Prometeus Optimizer aims to solve the same problem as Morpho Optimizer.
In brief, it helps lenders and borrowers to match with each other, providing them the way to perform a P2P transaction at better rates.

### Future Work
At the moment Proteus Optimizer can only find a match, but the underlying Demeter, the backtesting framework, does not support P2P transactions.
In addition, it does not support the possibility to change the rates just for a transaction in a easy way.
In the next future, Demeter should be extended to perform more types of backtesting and not simply individual strategy evaluation.
The next step would be to test both agents in a test network and finally deploy them to generate revenue automatically.