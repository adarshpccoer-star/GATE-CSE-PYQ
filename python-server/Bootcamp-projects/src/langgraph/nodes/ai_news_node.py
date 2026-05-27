from src.langgraph.tools.search_tools import get_tools
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from src.langgraph.state.state import State
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

class AINewsNode:
    def __init__(self, model):
        self.tavily = TavilyClient()
        self.llm = model  # Fixed: Removed trailing comma

    def fetch_news(self, state: dict) -> dict:
        # Standardize fallback logic if message content isn't daily/weekly/monthly
        user_msg = state['messages'][0].content if isinstance(state['messages'], list) else state['messages']
        frequency = user_msg.lower().strip()
        
        time_rang_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'yearly': 'y'}
        day_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'yearly': 365}

        # Fallback to daily if input doesn't match keys
        if frequency not in time_rang_map:
            frequency = 'daily'

        response = self.tavily.search(
            query="Top Artificial Intelligence and Technology News",
            topic="news",
            time_range=time_rang_map[frequency],
            include_answer="advanced",
            max_results=15,
            days=day_map[frequency],
        )

        state['news_data'] = response.get('results', [])
        state['frequency'] = frequency  # Store securely inside graph state
        return state
    
    def summarize_news(self, state: dict) -> dict:
        news_item = state.get('news_data', [])
        
        prompt_template = ChatPromptTemplate([
            ("system", """
                Summarize the AI news articles in markdown format. For each item include:
                - Date in YYYY-MM-DD format in IST timezone
                - Concise sentences summary from latest news 
                - Sort news by date wise (latest first)
                - Source URL as Link
                
                ### [Date]
                - [Summary](Url)
             """),
            ("user", "Articles:\n{articles}"),
        ])

        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nDate: {item.get('date', '')}\nLink: {item.get('link', '')}" 
            for item in news_item
        ])

        # Invoke the actual model instance
        formatted_prompt = prompt_template.format(articles=articles_str)
        response = self.llm.invoke(formatted_prompt)

        state['summary'] = response.content
        return state

    def save_result(self, state: dict) -> dict:
        frequency = state.get('frequency', 'daily')
        summary = state.get('summary', '')
        
        # Ensure target directory exists
        import os
        os.makedirs("./AINews", exist_ok=True)
        
        filename = f"./AINews/{frequency}_summary.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
            
        state['filename'] = filename
        return state