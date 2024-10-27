# Proteus - LLM-Powered Lending Agent on Aave

![Proteus Logo](proteus_logo.jpg)

### Abstract
Decentralized finance offers a wide range of opportunities for investors and traders. However, navigating the complex world of DeFi protocols can be challenging, especially for those unfamiliar with the technical intricacies. This project aims to develop a lending agent powered by large language models (LLMs) to automate and optimize lending strategies on the Aave V3 protocol. 
Proteus, the agent proposed, can work in two modes:
* Standalone: it analyze the market trends, understanding when it is better to supply, borrow, withdraw or repay tokens.
* Multi-Agent: it collaborates with other Proteus clients to minimize the share between supply/borrow APY, with the aim to maximize capital efficiency, by dealing better rates.

### Technologies involved
* **LangChain:** Framework used to build up the core of the Proteus agent
* **OpenAI API:** Provides access to powerful LLMs like GPT-4o.
* **Demeter:** A Python library for building and backtesting trading strategies.
* **Demeter_Fetch:** A Python library for fetching data from Aave V3 protocol.
* **BigQuery:** A cloud-based data warehouse containing the data from the Aave V3 protocol.
* **Aave V3 Protocol:** The DeFi protocol used for lending and borrowing.
* **Python:** The programming language used for developing the agent.
* **Pandas:** A Python library for data manipulation and analysis.

### Project Goals
* **Automate Lending Strategies:** The agent is able to execute lending strategies based on market conditions.
* **Optimize Lending Returns:** The agent leverages LLMs to analyze market data, identify profitable opportunities, and adjust strategies accordingly.

### Getting Started
Please click (this link)[./src/README.md] to getting started. It will guide you through all the phases of the project.

### Project Status
This project works off-chain, using Demeter library for backtesting. Future work will involve risk analysis and on-chain deployment.

### Project Structure
The project is structured as follows:
* **src:** Contains the source code for the lending agent.
* **data:** Contains market data used for training and backtesting.
* **docs:** Contains documentation for the project.

### Disclaimer
This project was built during the Encode London 2024 Hackaton to participate in the RNDM.io tracks. It is not intended to be used in production as it was developed in two days without sleeping.