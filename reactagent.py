import ollama
from tavily import TavilyClient
import os

# -------- API KEY (Only Tavily needed) --------
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# -------- AGENT CLASS --------
class WebResearchAgent:
    def __init__(self, topic):
        self.topic = topic
        self.questions = []
        self.research_data = {}

    # -------- PLANNING PHASE (Local LLM Reasoning) --------
    def generate_research_questions(self):
        prompt = f"""
        Generate 5–6 clear, well-structured research questions
        covering different aspects of the topic:
        {self.topic}
        """

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"]

        self.questions = [
            q.strip("- ").strip()
            for q in text.split("\n")
            if q.strip()
        ]

        return self.questions

    # -------- ACTING PHASE (Web Search Tool) --------
    def search_web(self):
        for question in self.questions:
            results = tavily_client.search(
                query=question,
                max_results=3
            )

            self.research_data[question] = []
            for item in results.get("results", []):
                self.research_data[question].append({
                    "title": item.get("title", "No title"),
                    "content": item.get("content", "No content available")
                })

    # -------- REPORT GENERATION --------
    def generate_report(self):
        report = f"# Research Report on {self.topic}\n\n"
        report += "## Introduction\n"
        report += (
            f"This report explores **{self.topic}** using a ReAct-based web research agent. "
            "A local large language model is used for reasoning, and a web search tool "
            "is used for information gathering.\n\n"
        )

        for question, answers in self.research_data.items():
            report += f"## {question}\n"
            for ans in answers:
                report += f"**{ans['title']}**\n\n"
                report += f"{ans['content']}\n\n"

        report += "## Conclusion\n"
        report += (
            "The ReAct agent successfully demonstrated planning and acting by "
            "generating research questions, collecting web-based information, "
            "and producing a structured report.\n"
        )

        return report


# -------- MAIN EXECUTION --------
if __name__ == "__main__":
    topic = input("Enter research topic: ").strip()

    agent = WebResearchAgent(topic)
    agent.generate_research_questions()
    agent.search_web()
    final_report = agent.generate_report()

    print("\n" + "=" * 70)
    print(final_report)
