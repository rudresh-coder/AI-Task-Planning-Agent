import json
from planner_service import generate_plan


def main() -> None:
    user_goal = input("\nEnter your goal for the AI Planning & Execution Agent:\n> ")

    print("\nCalling API... please wait.")

    try:
        data = generate_plan(user_goal)
    except ValueError as exc:
        print(str(exc))
        raise SystemExit(1)

    print("\n================ FINAL OUTPUT ================\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()