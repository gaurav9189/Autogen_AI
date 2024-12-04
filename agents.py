import autogen
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class AgentSystem:
    def __init__(self):
        # Create workspace directory if it doesn't exist
        os.makedirs("workspace", exist_ok=True)

        # Configure settings for OpenAI
        self.openai_config = {
            "temperature": 0.7,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "config_list": [{"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}]
        }

        # Configure settings for Anthropic
        self.anthropic_config = {
            "temperature": 0.7,
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "config_list": [{
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "api_type": "anthropic"
            }]
        }

        # Research Agent with gpt-4o-mini
        self.researcher = autogen.AssistantAgent(
            name="researcher",
            system_message="You are a research expert. Analyze requirements, research best practices, and ask clarifying questions when needed.",
            # Using standard GPT-4
            llm_config={**self.openai_config, "model": "gpt-4o-mini"}
        )

        # Solution Designer with gpt-4o
        self.designer = autogen.AssistantAgent(
            name="designer",
            system_message="You are a solution architect. Create detailed technical designs based on research findings.",
            # Using standard GPT-4
            llm_config={**self.openai_config, "model": "gpt-4o"}
        )

        # User Proxy Agent
        code_execution_config = {
            "work_dir": "workspace",
            "use_docker": False,
            "last_n_messages": 3,
            "timeout": 100
        }

        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=code_execution_config
        )

        # Enhanced Coder Agent with anthropic-sonnet-3.5
        self.coder = autogen.AssistantAgent(
            name="coder",
            system_message="""You are a coding expert who can write both general Python code and Snowflake-specific code.
            CRITICAL INSTRUCTION: You MUST ALWAYS respond with code implementation.
            - NEVER just acknowledge or approve designs
            - NEVER just provide suggestions without code
            - ALWAYS start your response with "Here's the code implementation:"
            - ALWAYS include code blocks
            
            For Snowflake operations:
            1. Always use environment variables (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE) for other details get the details from prompt as they are not defined in shell and use python code to connect to Snowflake
            2. ALWAYS include these elements in your code:
               - Explicit print statements for all query results
               - Print statements before and after each operation
               - Print the actual SQL queries being executed
               - Print the number of rows returned
            3. Use this structure for Snowflake queries:
               - Connect to Snowflake
               - Print "Executing query: <query>"
               - Execute query
               - Fetch results
               - Print "Results:"
               - Print actual results (use proper formatting)
               - Print "Number of rows returned: <count>"
            4. Include proper error handling with try/except blocks
            5. Always close connections properly
            
            IMPORTANT: When providing code:
            1. Always start with "Here's the code implementation:"
            2. Always wrap code blocks with triple backticks and specify the language:
            ```python
            # your code here
            ```
            3. After the code block, always say "Please execute this code."
            4. Wait for confirmation before proceeding.
            
            Example response format:
            Here's the code implementation:
            ```python
            print("Connecting to Snowflake...")
            # connection code here
            print("Executing query: SHOW DATABASES")
            cursor.execute("SHOW DATABASES")
            results = cursor.fetchall()
            print("Results:")
            for row in results:
                print(row)
            print(f"Number of rows returned: {len(results)}")
            ```
            Please execute this code.

            REMEMBER: 
            - NEVER just acknowledge or approve designs
            - NEVER just make suggestions without providing code
            - ALWAYS start with "Here's the code implementation:"
            - ALWAYS wrap code in triple backticks with language specification
            - ALWAYS include proper error handling
            - ALWAYS end with "Please execute this code."
            
            Example of REQUIRED response format:
            Here's the code implementation:
            ```python
            import os
            print("Current working directory:", os.getcwd())
            # ... rest of the code
            ```
            Please execute this code.
            """,
            llm_config=self.anthropic_config  # Using Claude-3.5
        )

    def start_workflow(self, initial_prompt: str):
        """Start the agent workflow with enhanced debugging"""
        print("\n🚀 Starting workflow...")
        print("\n📌 Debug: Creating group chat with agents:")
        print("User Proxy")
        # f"- User Proxy (executor) in workspace: {self.user_proxy._code_execution_config['work_dir']}")
        print(f"- Researcher: Analysis & Requirements")
        print(f"- Designer: Technical Architecture")
        print(f"- Coder: Implementation")

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
        print("\nWorkflow Process:")
        print("1. User Proxy sends prompt to Group Chat Manager")
        print("2. Researcher analyzes and responds")
        print("3. Designer creates technical spec")
        print("4. Coder writes implementation")
        print("5. User Proxy executes any code in workspace directory")
        # Capture the output from the UserProxyAgent
        output = self.user_proxy.initiate_chat(
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
        return output
