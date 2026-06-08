from agents import run

def get_script():
    print("Enter Your Script: (Press Ctrl + Z + Enter To Finish)")
    print("-" * 60)
    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass

    script = "\n".join(lines).strip()

    if not script:
        raise ValueError("No Script Provided.")
    
    return script

def main():
    script = get_script()

    print("Running Capton AI... \n")
    data = run(script=script)

    if data is None:
        print("Failed To Generate Captions")
        return None
    
    hooks = data.get("hooks", [])
    caption = data.get("caption", [])
    hashtags = data.get("hashtags", [])

    print("\n=== Hooks (for Shorts / Reels / FB) ===")
    for i, h in enumerate(hooks, start=1):
        print(f"{i}) {h}")
    print("=======================================\n")

    print("=== Caption (multi-platform) ===")
    print(caption)
    print("================================\n")

    print("=== Hashtags (multi-platform) ===")
    print(" ".join(hashtags))
    print("=================================\n")

    print("=== Ready-to-paste Description (any platform) ===")
    print(caption)
    print()
    print(" ".join(hashtags))
    print("=================================================")


if __name__ == "__main__":
    main()

    