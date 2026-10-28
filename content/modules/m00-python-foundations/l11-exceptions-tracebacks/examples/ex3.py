def parse_quality(text):
    """Fix quality '0'..'8' -> int. Raises ValueError with a clear message."""
    if text == "":
        raise ValueError("fix quality field is empty")
    quality = int(text)              # may raise Python's own ValueError
    if quality < 0 or quality > 8:
        raise ValueError(f"fix quality must be 0 to 8, got {quality}")
    return quality


for text in ["1", "4", "", "9"]:
    try:
        q = parse_quality(text)
    except ValueError as err:
        print(f"rejected {text!r}: {err}")     # str(err) is YOUR message
    else:
        print(f"quality {q}")                  # runs only if nothing was raised

print(parse_quality("2"))
