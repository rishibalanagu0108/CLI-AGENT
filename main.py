import argparse
import sys

from agent import Agent


def run_once(query: str, verbose: bool):
    agent = Agent()
    try:
        answer = agent.run(query)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(answer)
    if verbose:
        print(
            f"\n[tokens: {agent.state.total_tokens} | iterations: {agent.state.iterations}]",
            file=sys.stderr,
        )


def repl(verbose: bool):
    print("CLI Agent  —  type 'exit' or press Ctrl-C to quit\n")
    while True:
        try:
            query = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)

        if query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if not query:
            continue

        agent = Agent()
        try:
            answer = agent.run(query)
        except RuntimeError as e:
            print(f"\nError: {e}\n", file=sys.stderr)
            continue
        print(f"\nAgent: {answer}\n")
        if verbose:
            print(
                f"[tokens: {agent.state.total_tokens} | iterations: {agent.state.iterations}]\n",
                file=sys.stderr,
            )


def main():
    parser = argparse.ArgumentParser(
        prog="cli-agent",
        description="A Think→Act→Observe agent powered by Azure OpenAI.",
    )
    parser.add_argument("query", nargs="?", help="Query to answer (omit for interactive mode)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print token + iteration stats")
    args = parser.parse_args()

    if args.query:
        run_once(args.query, args.verbose)
    else:
        repl(args.verbose)


if __name__ == "__main__":
    main()
