# Demo for StackFix end-to-end test
# Expected: add(2, 3) == 5

from calc import add


def main():
    result = add(2, 3)
    if result != 5:
        raise SystemExit(f"FAIL: add(2,3) returned {result}, expected 5")
    print("PASS")


if __name__ == "__main__":
    main()
