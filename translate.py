from groq import Groq
import time
import os

# AAPKI SAARE 6 ACCOUNTS KI ACTIVE GROQ KEYS DIRECT CODE MEIN
GROQ_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]

current_key_index = 0
client = Groq(api_key=GROQ_KEYS[current_key_index])

input_file = "american.oxt"
output_file = "american_roman.oxt"

# BREAKPOINT: Batch 48 se freshly translation resume hogi
START_FROM_BATCH = 48  
batch_size = 20

def translate_batch(batch_items):
    global current_key_index, client
    prompt = (
        "You are an expert game translator. Translate the following lines into natural, conversational, "
        "and very easy WhatsApp-style Roman Urdu (Latin script) that a common Pakistani/Indian gamer can easily read (e.g., 'Main yahan fasa hua hoon'). "
        "Strictly follow these rules:\n"
        "1. Maintain the exact same line order and keep the hex keys (e.g., 0x1A2B3C4D) and tabs on the left completely UNTOUCHED.\n"
        "2. Keep the formatting tags (~z~ or ~w~) exactly where they are at the start of the text.\n"
        "3. Only output the translated lines, nothing else. Do not add any introductory or extra text.\n\n"
        "Lines to translate:\n" + "\n".join(batch_items)
    )
    
    while current_key_index < len(GROQ_KEYS):
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4000,
            )
            
            if hasattr(completion.choices, 'message'):
                response_text = completion.choices.message.content.strip()
            else:
                response_text = completion.choices['message']['content'].strip()
                
            translated_lines = response_text.split('\n')
            if len(translated_lines) == len(batch_items):
                return [line.strip('"').strip("'") for line in translated_lines]
            return batch_items
        except Exception as e:
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                current_key_index += 1
                if current_key_index < len(GROQ_KEYS):
                    print(f"\n🔄 Rate Limit Reached! Shifting to API Key #{current_key_index + 1}...")
                    client = Groq(api_key=GROQ_KEYS[current_key_index])
                    time.sleep(2)
                    continue
                else:
                    print("\n❌ Error: Saari 6 API Keys ka quota khatam ho gaya hai!")
                    return None
            else:
                print(f"\n⚠️ API Warning: {e}. Keeping original text.")
                return batch_items
    return None

if os.path.exists(input_file):
    print(f"🚀 GitHub Cloud Multi-Key Engine Active... Resuming from Batch {START_FROM_BATCH}")
    
    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        
    final_lines = list(all_lines)
    
    if os.path.exists(output_file) and START_FROM_BATCH > 1:
        with open(output_file, "r", encoding="utf-8") as f_out:
            final_lines = f_out.readlines()

    batch_items = []
    batch_indices = []
    
    for idx, line in enumerate(all_lines):
        if "~z~" in line or "~w~" in line:
            if "\t" in line: parts = line.split("\t", 1)
            elif " " in line: parts = line.split(" ", 1)
            else: continue
            
            # 🟢 FIXED: List filtering logic handle kiya bina 'strip' crash ke
            if len(parts) > 1:
                content_text = parts[1].strip()
                if content_text and not content_text.startswith("//"):
                    batch_items.append(line.strip())
                    batch_indices.append(idx)

    total_batches = (len(batch_items) + batch_size - 1) // batch_size
    print(f"📋 Total Dialogues Verified: {len(batch_items)} lines ({total_batches} batches).")
    
    for i in range(0, len(batch_items), batch_size):
        current_batch_num = (i // batch_size) + 1
        
        if current_batch_num < START_FROM_BATCH:
            continue
            
        current_batch = batch_items[i:i+batch_size]
        current_indices = batch_indices[i:i+batch_size]
        
        translated_batch = translate_batch(current_batch)
        
        if translated_batch is None:
            break  
            
        for b_idx, trans_line in zip(current_indices, translated_batch):
            final_lines[b_idx] = trans_line + "\n"
            
        print(f"➔ Processed Batch {current_batch_num} of {total_batches} successfully.")
        
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.writelines(final_lines)
            
        time.sleep(4.0)

    print("\n🎉 SUCCESS: Task completed.")
else:
    print("File nahi mili!")
