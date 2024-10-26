# useful imports
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from typing import Optional
from demeter.aave import SupplyKey, BorrowKey
from demeter import TokenInfo



class Operation(BaseModel):
    token: TokenInfo
    amount: float = Field(description="Amount to operate on. It is 0 for withdraw and repay")
    

# defining agent state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    
#let's define a LangGraph agent with 4 tools, a central node that can use any tool
class LendingAgent:
    def __init__(self, model, prompt, market):
        self.market = market
        
        graph = StateGraph(AgentState)
        
        graph.add_node("llm", self.call_llm)
        graph.add_node("execute_function", self.execute_function)
        graph.add_edge("execute_function", "llm")
        
        self.tools = [
            self.supply,
            self.borrow,
            self.withdraw,
            self.repay
        ]
        
        self.system_prompt = prompt
        
        self.model = model.bind_tools(self.tools)
        
    def call_llm(self, state: AgentState) -> AgentState:
        """Calls the LLM to get a response.

        Args:
            state: The current state of the agent.

        Returns:
            The updated state of the agent.
        """
        messages = state['messages']
        # adding system prompt if it's defined
        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages
        
        # calling LLM
        message = self.model.invoke(messages)

        return {'messages': [message]}
    
    def execute_function(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls

        results = []
        for tool in tool_calls:
        # checking whether tool name is correct
            if not tool['name'] in self.tools:
                # returning error to the agent 
                result = "Error: There's no such tool, please, try again" 
            else:
                # getting result from the tool
                result = self.tools[tool['name']].invoke(tool['args'])
        
        results.append(
            ToolMessage(
            tool_call_id=tool['id'], 
            name=tool['name'], 
            content=str(result)
            )
        )
        return {'messages': results}
    
    @tool(args_schema = Operation)
    def supply(self, token: TokenInfo, amount: float) -> Optional[SupplyKey]:
        """Supplies a specified amount of a given token to the Aave market.

        Args:
            token: The token to supply.
            amount: The amount of the token to supply.

        Returns:
            The SupplyKey for the supply operation if successful, otherwise None.
        """
        exit()
        try:
            supply_key = self.market.supply(token, amount)
            return supply_key
        except Exception as e:
            print(e)
        return None

    @tool(args_schema = Operation)
    def borrow(self, token: TokenInfo, amount: float) -> Optional[BorrowKey]:
        """Borrows a specified amount of a given token from the Aave market.

        Args:
            token: The token to borrow.
            amount: The amount of the token to borrow.

        Returns:
            The BorrowKey for the borrow operation if successful, otherwise None.
        """
        try:
            borrow_key = self.market.borrow(token, amount)
            return borrow_key
        except Exception as e:
            print(e)
        return None

    @tool(args_schema = Operation)
    def withdraw(self, token: TokenInfo, amount: float) -> bool:
        """Withdraws previously supplied tokens. 
        
        Args:
            token: The token is a SupplyKey (TokenInfo) obtained during the supply operation.
            
        Returns:
            True if the withdrawal is successful, otherwise False.
        """
        try:
            self.market.withdraw(token)  # Use the supply_key here
            return True
        except Exception as e:
            print(e)
        return False

    @tool(args_schema = Operation)
    def repay(self, token: TokenInfo, amount: float) -> bool:
        """Repays a previous borrow operation.
        
        Args:
            token: The token is BorrowKey (TokenInfo) obtained during the borrow operation.
            
        Returns:
            True if the repayment is successful, otherwise False.
        """
        try:
            self.market.repay(token)  # Use the borrow_key here
            return True
        except Exception as e:
            print(e)
        return False