from dotenv import load_dotenv
from agents.summary_generator import SummaryGeneratorAgent

if __name__ == "__main__":
    load_dotenv()  
    
    summary_generator_agent = SummaryGeneratorAgent()
    summary_generator_agent.run()