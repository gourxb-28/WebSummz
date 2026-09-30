from app.services.retriever import retrieve_context

paragraphs = [f"Paragraph {i}. " + "This is filler text about topic. " * 30 for i in range(20)]
paragraphs[7] = "Key finding: the study concludes that regular exercise improves memory. " * 10
text = "\n\n".join(paragraphs)

selected = retrieve_context(text)
print("Chunks returned:", len(selected))
for i, c in enumerate(selected):
    print(f"\n--- chunk {i} ({len(c)} chars) ---\n{c[:100]}...")