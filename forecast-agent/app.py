from agents.forecast_agent import ForecastAgent


def main():

    agent = ForecastAgent()

    print("=" * 60)
    print("Supply Chain Intelligence Copilot")
    print("=" * 60)

    while True:

        user_query = input("\nYou : ")

        if user_query.lower() in ["exit", "quit"]:

            print("\nGoodbye!")

            break

        response = agent.run(user_query)

        print("\nAssistant:\n")

        print(response)


if __name__ == "__main__":

    main()