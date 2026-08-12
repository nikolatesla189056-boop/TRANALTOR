from groq import Groq
import time
import os

# GitHub ke safe secrets se automatic API key uthana
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

input_file = "american.oxt"
output_file = "american_roman.oxt"
batch_size = 20

def translate_batch(batch_items):
    prompt = (
        "You are an expert game translator. Translate the following lines into natural, conversational, "
        "and very easy WhatsApp-style Roman Urdu (Latin script) that a common Pakistani/Indian gamer can easily read. "
        "Strictly follow these rules:\n"
        "1. Maintain the exact same line order and keep the hex keys (e.g., 0x1A2B3C4D) and tabs on the left completely UNTOUCHED.\n"
        "2. Keep the formatting tags (~z~ or ~w~) exactly where they are at the start of the text.\n"
        "3. Only output the translated lines, nothing else.\n\n"
        "Lines to translate:\n" + "\n".join(batch_items)
    )
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        if hasattr(completion.choices[0], 'message'):
            response_text = completion.choices[0].message.content.strip()
        else:
            response_text = completion.choices[0]['message']['content'].strip()
            
        translated_lines = response_text.split('\n')
        if len(translated_lines) == len(batch_items):
            return [line.strip('"').strip("'") for line in translated_lines]
    except Exception as e:
        print(f"Batch Error: {e}")
    return batch_items

if os.path.exists(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        
    final_lines = list(all_lines)
    batch_items = []
    batch_indices = []
    
    for idx, line in enumerate(all_lines):
        if "~z~" in line or "~w~" in line:
            if "\t" in line: parts = line.split("\t", 1)
            elif " " in line: parts = line.split(" ", 1)
            else: continue
            if len(parts) > 1 and parts[1].strip() and not parts[1].strip().startswith("//"):
                batch_items.append(line.strip())
                batch_indices.append(idx)

    total_batches = (len(batch_items) + batch_size - 1) // batch_size
    print(f"Processing {total_batches} batches on GitHub Cloud...")
    
    for i in range(0, len(batch_items), batch_size):
        current_batch = batch_items[i:i+batch_size]
        current_indices = batch_indices[i:i+batch_size]
        
        translated_batch = translate_batch(current_batch)
        
        for b_idx, trans_line in zip(current_indices, translated_batch):
            final_lines[b_idx] = trans_line + "\n"
            
        print(f"➔ Processed Batch {(i // batch_size) + 1} of {total_batches}")
        time.sleep(4.0) # Rate limit safety

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.writelines(final_lines)
