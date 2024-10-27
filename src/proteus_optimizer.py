# useful imports
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from queue import PriorityQueue
"""
class Lender(TypedDict):
    address: str
    amount: float

class Borrower(TypedDict):
    address: str
    amount: float
"""

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    lenders: PriorityQueue
    borrowers: PriorityQueue
    
class ProteusOptimizer:
    def __init__(self, model):
        graph = StateGraph(AgentState)
        
        graph.add_node("llm", self.call_llm)
        graph.add_node("execute_function", self.execute_function)
        graph.add_conditional_edges("llm", self.exists_function_calling, {True: "function", False: END})   
        graph.add_edge("execute_function", "llm")
        
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
        llm_response = self.model.invoke(messages)
        
        # Add the LLM response to the message history
        state['messages'].append(llm_response) 

        # Check if the LLM wants to call a tool
        if llm_response.tool_calls:
            # Execute the tool calls
            state = self.execute_function(state)
            # Add the tool responses to the message history
            messages.extend(state['messages'])

        # Update the state with the LLM response or tool responses
        return {'messages': messages}
    
    # Execute one of the tools provided to the agent
    def execute_function(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls

        results = []
        for t in tool_calls:
        # checking whether tool name is correct
            if not t['name'] in self.tools:
                # returning error to the agent 
                result = "Error: There's no such tool, please, try again" 
            else:
                result = self.tools[t['name']](t['args'])
        
        results.append(
            ToolMessage(
            tool_call_id=t['id'], 
            name=t['name'], 
            content=str(result)
            )
        )
        return {'messages': results}
    
    #It checks if there is a tool call in the trace, otherwise it won't take that path in the graph
    def exists_function_calling(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0