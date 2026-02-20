


class ChatLoop:
    def __init__(self):
        print("init")

    def new_message(self, message):
        print(f"mess: {message}")
        return f"reçu : {message}"


def main():
    # Paramètres : à adapter selon votre configuration
    chat_loop = ChatLoop(
        # collection_name="mon_pod",
        # persist_directory="./chroma_storage"
    )
    print("Assistant RAG prêt. Tapez votre question (ou 'quit' pour quitter).")
    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() in ('quit', 'exit'):
            break
        if not query:
            continue
        answer = chat_loop.new_message(query)
        print(f"\n{answer}\n")

if __name__ == "__main__":
    main()