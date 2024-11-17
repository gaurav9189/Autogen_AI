import autogen
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class AgentSystem:
    def __init__(self):
        # Configure agents with specific roles
        self.config = {
            "temperature": 0.7,
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY")
        }

        # Research Agent
        self.researcher = autogen.AssistantAgent(
            name="researcher",
            system_message="You are a research expert. Analyze requirements, research best practices, and ask clarifying questions when needed.",
            llm_config=self.config
        )

        # Solution Designer
        self.designer = autogen.AssistantAgent(
            name="designer",
            system_message="You are a solution architect. Create detailed technical designs based on research findings.",
            llm_config=self.config
        )

        # Code Generator
        self.coder = autogen.AssistantAgent(
            name="coder",
            system_message="You are a coding expert. Generate implementation code based on technical designs.",
            llm_config=self.config
        )

        # User Proxy Agent
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "workspace"}
        )

    def start_workflow(self, initial_prompt: str):
        """Start the workflow with an initial prompt"""
        # Initialize the group chat
        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher, self.designer, self.coder],
            messages=[],
            max_round=50
        )
        
        manager = autogen.GroupChatManager(groupchat=groupchat)

        # Start the chat with the initial prompt
        self.user_proxy.initiate_chat(
            manager,
            message=f"""
            Project Request: {initial_prompt}
            
            Please follow this workflow:
            1. Researcher: Analyze requirements and research best practices
            2. Designer: Create technical design based on research
            3. Coder: Generate implementation code
            
            Each agent should wait for the previous agent to complete their task.
            """
        )
