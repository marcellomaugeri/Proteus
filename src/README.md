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
Rename the file bigquerykey.json

```
# Finally, run demeter-fetch with the provided config file
python3 demeter-fetch/main.py -c config.aave.toml
```
The output will be in a sample folder.
Move the folder in the data folder and continue.
Now you can open the Jupyter notebook.

### 1 - Jupyter Notebook
This folder contains a Jupyter notebook that analyzes the data from the Aave V3 protocol.
The objective is to analyse trend, potential indicator for an effective lending strategy.
The document is already self-explanatory and detailed.

### 2 - Simple Backtest
To let all test off-chains, Demeter have been used as backtesting framework.
The file `2_simple_backtest.py` shows how to use the network in Aave V3.
Before going further with the agent, I suggest a brief reading to understand the setup.
If the scripts executes until the end, you would look some general data about the network, more details about how to interprete them will be provided in the next step.

### 3 - Standalone Agent
The file `3_standalone_agent.py` shows how to use the network in Aave V3.
The agent is a simple agent that uses the network to borrow and repay tokens.
The agent is not optimized, but it is a good starting point for developing more complex agents.
The agent is trained using a reinforcement learning algorithm.

####
