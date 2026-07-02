"""Interactive CLI chat loop for the Multi-Tool AI Agent for Bangladesh."""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

from agent.main_agent import build_agent_executor  # noqa: E402  (must load .env first)


def main():
    print("Multi-Tool AI Agent for Bangladesh (type 'exit' or 'quit' to stop)\n")
    executor = build_agent_executor()
    chat_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        result = executor.invoke({"input": user_input, "chat_history": chat_history})
        answer = result["output"]
        print(f"\nAgent: {answer}\n")

        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=answer))


if __name__ == "__main__":
    main()
