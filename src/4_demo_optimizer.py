from asyncio import sleep
import os
from langchain_openai import ChatOpenAI
from datetime import date, datetime
from typing import Union
from demeter import TokenInfo, Actuator, Strategy, RowData, MarketInfo, MarketTypeEnum, ChainType, AtTimeTrigger
from demeter.aave import AaveBalance, AaveV3Market, AaveTokenStatus, SupplyKey, BorrowKey
import pandas as pd
from langchain_core.messages import SystemMessage
from proteus_agent import ProteusAgent
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Optional
import random
from threading import Thread
import sys

# setting up credentioals
os.environ["OPENAI_MODEL_NAME"]='gpt-4o-mini'  
os.environ["OPENAI_API_KEY"] = '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'

global market
usdc = TokenInfo(name="usdc", decimal=18, address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
weth = TokenInfo(name="weth", decimal=18, address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619")
token_list = [ usdc, weth ]

DEBUG = True
NUMBER_OF_AGENTS = 5

initial_prompt_optimizer = """You act as a matchmaker, facilitating peer-to-peer lending and borrowing in the Aave V3 Protocol. You will simulate a Morpho Optimizer by keeping a PriorityQueue for both lenders and borrowers.
You will receive messages from the agents, and you will decide whether to match them."""

class Operation(BaseModel):
    token: TokenInfo = Field(description="Token to operate on")
    amount: float = Field(description="Amount to operate on. It is 0 for withdraw and repay")
    
@tool(args_schema = Operation)
def match(token: TokenInfo, amount: float):
    """Matches a lender and a borrower.

    Args:
        token: The token to match.
        amount: The amount to match.

    Returns:
        A string indicating the result of the match.
    """    
    #Check if there are lenders and borrowers for the token
    print("Optimizer called!")
    print("Optimizer called!")
    print(type(token))
    suppliers = market.get_supply(token)
    borrowers = market.get_borrow(token)
    if suppliers is not None:
        print("Supplies: {}".format(suppliers))
    if borrowers is not None:
        print("Borrows: {}".format(borrowers))
    
    #Find a match
    while not suppliers.empty() and not borrowers.empty():
        lender = suppliers.get()
        borrower = borrowers.get()
        
        #Check if the lender has enough funds
        if lender[0] >= amount:
            #Check if the borrower can afford the amount
            if borrower[0] <= amount:
                #Match the lender and borrower
                print("\033[31mMatched lender {} with borrower {} for {} {} tokens\033[34m".format(lender[1]['address'], borrower[1]['address'], amount, token.name))
                return "Match successful."
            else:
                #Put the borrower back in the queue
                borrowers.put(borrower)
        else:
            #Put the lender back in the queue
            suppliers.put(lender)
    
    #No match found
    return "No match found."


optimizer_model = ChatOpenAI(model="gpt-4o-mini")
agent = ProteusAgent(optimizer_model, [match], initial_prompt_optimizer)

@tool(args_schema = Operation)
def supply(token: TokenInfo, amount: float) -> Optional[SupplyKey]:
    """Supplies a specified amount of a given token to the Aave market.

    Args:
        token: The token to supply.
        amount: The amount of the token to supply.

    Returns:
        The SupplyKey for the supply operation if successful, otherwise None.
    """
    try:
        supply_key = market.supply(token, amount)
        #Call the optimizer
        agent.call_llm({'messages': [SystemMessage(content="Done supply of {} in {}".format(amount, token))]})
        if DEBUG:
            print("\033[31mSupplied {} {} tokens\033[34m".format(amount, token.name))
        return supply_key
    except Exception as e:
        print(e)
    return None

@tool(args_schema = Operation)
def borrow(token: TokenInfo, amount: float) -> Optional[BorrowKey]:
    """Borrows a specified amount of a given token from the Aave market.

    Args:
        token: The token to borrow.
        amount: The amount of the token to borrow.

    Returns:
        The BorrowKey for the borrow operation if successful, otherwise None.
    """
    try:
        borrow_key = market.borrow(token, amount)
        agent.call_llm({'messages': [SystemMessage(content="Done borrow of {} in {}".format(amount, token))]})
        if DEBUG:
            print("\033[31mBorrowed {} {} tokens\033[34m".format(amount, token.name))
        return borrow_key
    except Exception as e:
        print(e)
    return None

@tool(args_schema = Operation)
def withdraw(token: TokenInfo, amount: float) -> bool:
    """Withdraws previously supplied tokens. 
    
    Args:
        token: The token is a SupplyKey (TokenInfo) obtained during the supply operation.
        amount: must be 0
        
    Returns:
        True if the withdrawal is successful, otherwise False.
    """
    try:
        market.withdraw(token)
        if DEBUG:
            print("\033[31mWithdrew {} {} tokens\033[34m".format(amount, token.name))
        return True
    except Exception as e:
        print(e)
        return False

@tool(args_schema = Operation)
def repay(token: TokenInfo, amount: float) -> bool:
    """Repays a previous borrow operation.
    
    Args:
        token: The token is BorrowKey (TokenInfo) obtained during the borrow operation.
        amount: must be 0
        
    Returns:
        True if the repayment is successful, otherwise False.
    """
    try:
        market.repay(token)
        if DEBUG:
            print("\033[31mRepaid {} {} tokens\033[34m".format(amount, token.name))
        return True
    except Exception as e:
        print(e)
    return False   

initial_prompt_agent = """You are a lending agent working in the Aave lending protocol.
        In every message I will provide you your current balance and market status.
        In addition, I will provide you some stats about the last 30 minutes.
        Your goal is to decide wheter supply, borrow, withdraw tokens or repay.
        You will be in charge of your strategy, try to maximize your profit.
        You have a lot of money, so feel free to do frequent transactions"""
    
class MySimpleStrategy(Strategy):
    def initialize(self):        
        self.model = ChatOpenAI(model="gpt-4o-mini")
        self.agent = ProteusAgent(self.model, [supply, borrow, withdraw, repay], initial_prompt_agent)
        self.counter = 0
        pass

    def on_bar(self, row_data: RowData):
        self.counter += 1
        #Get market status
        market_status: Union[pd.Series, AaveTokenStatus] = row_data.market_status[market_key]
        if self.counter%3000 == 0:
            #Get current balance
            usdc_balance = self.broker.get_token_balance(usdc)
            weth_balance = self.broker.get_token_balance(weth)
            
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

def threaded_agent(id):
    actuator = Actuator()
    broker = actuator.broker
    broker.add_market(market)
    broker.set_balance(usdc, random.randint(100, 5000*(i+1)))
    broker.set_balance(weth, random.randint(100, 1000-i))
    actuator.strategy = MySimpleStrategy()
    actuator.set_price(prices_df)
    actuator.run()
    
if __name__ == "__main__":
    print("""\033[34m
          
 ,---.  ,---.    .---.  _______ ,---.  .-. .-.   .---. 
 | .-.\ | .-.\  / .-. )|__   __|| .-'  | | | |  ( .-._)
 | |-' )| `-'/  | | |(_) )| |   | `-.  | | | | (_) \   
 | |--' |   (   | | | | (_) |   | .-'  | | | | _  \ \  
 | |    | |\ \  \ `-' /   | |   |  `--.| `-')|( `-'  ) 
 /(     |_| \)\  )---'    `-'   /( __.'`---(_) `----'  
(__)        (__)(_)            (__)                    


 .---.  ,---.  _______ ,-.        ,-. _____  ,---.  ,---.    
/ .-. ) | .-.\|__   __||(||\    /||(|/___  / | .-'  | .-.\   
| | |(_)| |-' ) )| |   (_)|(\  / |(_)   / /) | `-.  | `-'/   
| | | | | |--' (_) |   | |(_)\/  || |  / /(_)| .-'  |   (    
\ `-' / | |      | |   | || \  / || | / /___ |  `--.| |\ \   
 )---'  /(       `-'   `-'| |\/| |`-'(_____/ /( __.'|_| \)\  
(_)    (__)               '-'  '-'          (__)        (__) 

""")
    
    market_key = MarketInfo("aave", MarketTypeEnum.aave_v3)
    market = AaveV3Market(market_key, "../data/riskparameters.csv", token_list)
    market.data_path = "../data/sample"

    market.load_data(
        chain=ChainType.polygon,
        token_info_list=market.tokens,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 30),
    )
    prices_df = pd.read_csv("../data/WETH_USDC_Prices.csv", index_col=0, parse_dates=True)

    threads = []
    for i in range(NUMBER_OF_AGENTS):
        thread = Thread(target = threaded_agent, args = (i,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()    