import os
import openai
import json
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

RawInputName = "abortion_transgender_data.json"
AutoAnnatationOutputname = "abortion_transgender_annotation_wo_human.json"

with open(RawInputName, "r") as f:
   convs = json.load(f)
   
messages = [{"role":"system", "content":"By looking through the below conversations where people are argueing on a controversial topic, you are albe to infer the moral concern of each speaker according to what they say in each turn."}]
for c_id, conv in enumerate(convs):
    messages = [{"role":"system", "content":"By looking through below conversations where people are argueing on a controversial topic, you are albe to infer the moral concern of each speaker according to what they say in each turn."}]  
    text = ""
    for utter in conv["Conversation"]:
        prefix = f'Speaker{utter["Speaker_id"]}-Utterance{utter["Utterance_id"]}'
        utterance = f'{prefix}:{utter["Content"]}\n'
        text += utterance 
    messages.append({"role":"user", "content": text})
    for u_id, utter in enumerate(conv["Conversation"]):
        prefix = f'Speaker{utter["Speaker_id"]}-Utterance{utter["Utterance_id"]}'  
        last_command = {"role":"system", "content": f"Tell me the moral principle or the intrisic value what {prefix} is promoting or supporting. Answer me with a phrase within 4 words."}
        
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", 
                                                messages=messages + [last_command], 
                                                temperature=0.7, 
                                                max_tokens=256,
                                                top_p = 0.7,
                                                n=5)
        print(messages + [last_command])
        choicel = []
        for choice in response["choices"]:
            print(choice["message"]["content"])
            choicel.append(choice["message"]["content"])
            
        convs[c_id]["Conversation"][u_id]["Enhancing"] = choicel
        
            
        last_command = {"role":"system", "content": f"Tell me the moral principle or the intrisic value what {prefix} is downplaying or opposing. Answer me with a phrase within 4 words."}
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", 
                                                messages=messages + [last_command], 
                                                temperature=0.7, 
                                                max_tokens=256,
                                                n=5)
        print(messages + [last_command])
        choicel = []
        for choice in response["choices"]:
            print(choice["message"]["content"])
            choicel.append(choice["message"]["content"])
        convs[c_id]["Conversation"][u_id]["Undercutting"] = choicel
        
with open(AutoAnnatationOutputname,"w") as f:
   json.dump(convs, f, indent=1)