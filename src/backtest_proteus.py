import os
from langchain_openai import ChatOpenAI
from datetime import date, datetime
from typing import Union
from demeter import TokenInfo, Actuator, Strategy, RowData, MarketInfo, MarketTypeEnum, ChainType, AtTimeTrigger
from demeter.aave import AaveBalance, AaveV3Market, AaveTokenStatus
import pandas as pd
global market
from simple_agent import LendingAgent
from langchain_core.messages import SystemMessage

# setting up credentioals
os.environ["OPENAI_MODEL_NAME"]='gpt-4o-mini'  
os.environ["OPENAI_API_KEY"] = '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'

class MyFirstStrategy(Strategy):
    def initialize(self):
        supply_trigger = AtTimeTrigger(time=datetime(2024, 6, 10, 0, 1, 0), do=self.supply)
        withdraw_trigger = AtTimeTrigger(time=datetime(2024, 6, 14, 23, 58, 0), do=self.withdraw)
        #borrow_trigger = AtTimeTrigger(time=datetime(2024, 6, 20, 0, 2, 0), do=self.borrow)
        repay_trigger = AtTimeTrigger(time=datetime(2024, 6, 30, 23, 57, 0), do=self.repay)
        self.triggers.extend([supply_trigger, withdraw_trigger, repay_trigger])

    def supply(self, row_data: RowData):
        print(self.markets)
        supply_key = market.supply(weth, 10, True)

    def borrow(self, row_data: RowData):
        borrow_key = market.borrow(weth, 3)

    def repay(self, row_data: RowData):
        for key in market.borrow_keys:
            market.repay(key)

    def withdraw(self, row_data: RowData):
        for key in market.supply_keys:
            market.withdraw(key)

    def on_bar(self, row_data: RowData):
        balance: AaveBalance = market.get_market_balance()
        market_status: Union[pd.Series, AaveTokenStatus] = row_data.market_status[market_key]
        print(market_status)
        pass
    
class MySimpleStrategy(Strategy):
    def initialize(self):
        # initial prompt
        prompt = '''You are a lending agent working in the Aave lending protocol.
        In every message I will provide you your current balance for each currency.
        In addition, I will provide you some stats about the last 30 minutes.
        Your goal is to decide wheter supply, borrow, withdraw tokens or repay.
        You will be in charge of your strategy.
        '''
        #init the agent
        self.model = ChatOpenAI(model="gpt-4o-mini")
        self.agent = LendingAgent(self.model, prompt, market)
        self.counter = 0
        pass

    def on_bar(self, row_data: RowData):
        self.counter += 1
        #Get market status
        market_status: Union[pd.Series, AaveTokenStatus] = row_data.market_status[market_key]
        if self.counter%3000 == 0:
            #Get current balance
            usdc_balance = broker.get_token_balance(usdc)
            weth_balance = broker.get_token_balance(weth)
            
            #Get current borrow_keys
            borrow_keys = market.borrow_keys
            #Get current supply_keys
            supply_keys = market.supply_keys
            
            #Prepare the message for the LLM
            message = f"""
            Current balance:
            USDC: {usdc_balance}
            WETH: {weth_balance}
            
            Market status:
            {market_status}
            
            Borrow keys:
            {borrow_keys}
            
            Supply keys:
            {supply_keys}
            """
            # Invoke the agent with message
            self.agent.call_llm({'messages': [SystemMessage(content=message)]})
            
    
    
if __name__ == "__main__":
    usdc = TokenInfo(name="usdc", decimal=18, address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
    weth = TokenInfo(name="weth", decimal=18, address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619")
    token_list = [ usdc, weth ]
    #TokenInfo(name="usdt", decimal=18, address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F"),
    #TokenInfo(name="sushi", decimal=18, address="0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a"),
    market_key = MarketInfo("aave", MarketTypeEnum.aave_v3)
    market = AaveV3Market(market_key, "riskparameters.csv", token_list)
    market.data_path = "./sample"

    market.load_data(
        chain=ChainType.polygon,
        token_info_list=market.tokens,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 30),
    )

    actuator = Actuator()
    broker = actuator.broker
    broker.add_market(market)
    broker.set_balance(usdc, 20)
    broker.set_balance(weth, 100)
    actuator.strategy = MySimpleStrategy()
    prices_df = pd.read_csv("./prices.csv", index_col=0, parse_dates=True)

    actuator.set_price(prices_df)

    actuator.run()
    