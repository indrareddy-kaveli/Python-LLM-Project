
def detect_intent(message: str) -> str:
    message = message.lower().strip()

    if any(word in message for word in [
        "summarize", "summary", "shorten"
    ]):
        return "summarization"

    if any(word in message for word in [
        "explain", "describe", "teach me"
    ]):
        return "explanation"

    question_words = [
        "what", "who", "when", "where", "why",
        "which", "how", "is", "are", "can",
        "do", "does"
    ]

    words = message.replace("?", "").split()

    if any(word in question_words for word in words):
        return "question"

    if message in ["hi", "hello", "hey", "hey there"]:
        return "greeting"

    return "general"


if __name__ == "__main__":
    message = input("Enter your message: ")
    intent = detect_intent(message)

    print("User message:", message)
    print("Detected intent:", intent)
