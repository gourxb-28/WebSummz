print("START")

from app.services.chunking import clean_text, chunk_text

print("IMPORT DONE")

text = " ".join(
    f"Sentence number {i} talks about topic {i}."
    for i in range(200)
)

print("TEXT CREATED")

text = clean_text(text)
print("CLEAN DONE")

chunks = chunk_text(text)
print("CHUNK DONE")

print("Total characters:", len(text))
print("Number of chunks:", len(chunks))
print("Chunk lengths:", [len(c) for c in chunks])

print("\nEND of chunk 0:", chunks[0][-120:])
print("START of chunk 1:", chunks[1][:120], "...")