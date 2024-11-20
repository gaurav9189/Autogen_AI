import autogen
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class AgentSystem:
    def __init__(self):
        # Create workspace directory if it doesn't exist
        os.makedirs("workspace", exist_ok=True)

        # Configure agents with specific roles
        self.config = {
            "temperature": 0.7,
            "model": "gpt-3.5-turbo",
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

        # User Proxy Agent with code execution config
        code_execution_config = {
            "work_dir": "workspace",
            "use_docker": False,
            "last_n_messages": 3,
            "timeout": 60,
        }

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=code_execution_config
        )

        # Enhanced Coder Agent
        self.coder = autogen.AssistantAgent(
            name="coder",
            system_message="""You are a coding expert who can write both general Python code and Snowflake-specific code.
            For Snowflake operations, always use environment variables (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, etc.) from the shell.
            Write clear, executable code blocks with proper error handling and debugging messages.
            Always print status messages to help track execution progress.""",
            llm_config=self.config
        )

    def start_workflow(self, initial_prompt: str):
        """Start the agent workflow with enhanced debugging"""
        print("\n🚀 Starting workflow...")

        # Initialize the group chat with all agents
        agents = [self.user_proxy, self.researcher, self.designer, self.coder]

        groupchat = autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=50
        )

        manager = autogen.GroupChatManager(groupchat=groupchat)

        # Start the chat with the initial prompt
        print("\n📋 Initiating chat with workflow steps...")
        self.user_proxy.initiate_chat(
            manager,
            message=f"""
            Project Request: {initial_prompt}
            
            Please follow this workflow:
            1. Researcher: Analyze requirements and research best practices
            2. Designer: Create technical design based on research
            3. Coder: Generate and execute implementation code
               - For Snowflake operations, use environment variables
               - Include status messages and error handling
               - Test the code execution
            
            Each agent should wait for the previous agent to complete their task.
            Print clear status messages during execution.
            """
        )
        print("\n✅ Workflow completed!")
