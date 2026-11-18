# Project Reflection: PawPal+ AI System

Building PawPal+ was an exercise in understanding the difference between "making an AI work" and "building a reliable AI system." 

## What I Learned
- **The Fallback is Everything:** During development, the free OpenRouter API failed multiple times (Error 429, 503). Without the Regex fallback, the app would have crashed. I learned that defensive programming is not just a "nice to have" in AI; it is a requirement.
- **Observability:** Initially, my evaluation script counted fallbacks as successes. This masked the AI's failures. By refactoring the system to return the `source` (llm or fallback), I gained true observability. You cannot improve what you cannot measure.
- **AI Collaboration:** I used the AI to help design the prompt and schema, but I had to reject its suggestion to create a 5th class (`Recurrence`) because it overcomplicated a simple function.

## Future Improvements
If I had more time, I would implement a vector database (like ChromaDB) for the RAG component instead of a local JSON file, and add a user authentication layer to move away from session-only storage.