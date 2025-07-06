import os

try:
    import openai
except Exception:  # pragma: no cover - openai may not be installed
    openai = None


def generate_course_topics(title: str, n: int = 5):
    """Generate a list of lesson titles using OpenAI if possible."""
    if openai is None or not os.getenv("OPENAI_API_KEY"):
        return [f"{title} Topic {i+1}" for i in range(n)]

    openai.api_key = os.environ["OPENAI_API_KEY"]
    prompt = f"Generate {n} short lesson titles for a course about '{title}'."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content
        topics = [t.strip(" -\n") for t in text.splitlines() if t.strip()]
        return topics[:n] if topics else [f"{title} Topic {i+1}" for i in range(n)]
    except Exception:
        return [f"{title} Topic {i+1}" for i in range(n)]