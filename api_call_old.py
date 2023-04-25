import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

RawInputName = "abortion_transgender_data.json"
AutoAnnatationOutputname = "abortion_transgender_annotation_wo_human.json"

with open(RawInputName, "r") as f:
   convs = json.load(f)
   
messages = [{"role":"system", "content":"By looking through the below conversations where people are argueing on a controversial topic, you are albe to infer the moral concern of each speaker according to what they say in each turn."}]
for c_id, conv in enumerate(convs[:]):
    messages = [{"role":"system", "content":"By looking through below conversations where people are argueing on a controversial topic, you are albe to infer the moral concern of each speaker according to what they say in each turn."}]  
    text = ""
    for utter in conv["Conversation"]:
        prefix = f'Speaker{utter["Speaker_id"]}-Utterance{utter["Utterance_id"]}'
        utterance = f'{prefix}:{utter["Content"]}\n'
        text += utterance 
    messages.append({"role":"user", "content": text})
    for u_id, utter in enumerate(conv["Conversation"]):
        prefix = f'Speaker{utter["Speaker_id"]}-Utterance{utter["Utterance_id"]}'  
        last_command = {"role":"system", "content": f"Tell me the moral principle or the intrisic value what {prefix} is promoting or supporting. If there isn't an answer, reply me NA. Answer me with a phrase within 4 words."}
        
        print(messages + [last_command])
        print("~~~")
        while True:
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", 
                                                        messages=messages + [last_command], 
                                                        temperature=0.7, 
                                                        max_tokens=256,
                                                        top_p = 0.7,
                                                        n=5)
            except Exception as e:
                print(e)
            else:
                break
        choicel = []
        assert len(response["choices"]) == 5
        for choice in response["choices"]:
            print(choice["message"]["content"])
            choicel.append(choice["message"]["content"].replace(".", ""))
        # messages.append(last_command)   
        # last_command = {"role": "assistant", "content": f'{",".join(choicel)}'}
        # messages.append(last_command)    
        convs[c_id]["Conversation"][u_id]["Enhancing"] = choicel
        time.sleep(0.1)  
        last_command = {"role":"system", "content": f"Tell me the moral principle or the intrisic value what {prefix} is downplaying or opposing. If there isn't an answer, reply me NA. Answer me with a phrase within 4 words."}
        print(messages + [last_command])
        print("~~~")
        while True:
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", 
                                                        messages=messages + [last_command], 
                                                        temperature=0.7, 
                                                        max_tokens=256,
                                                        top_p = 0.7,
                                                        n=5)
            except Exception as e:
                print(e)
            else:
                break
        assert len(response["choices"]) == 5
        choicel = []
        for choice in response["choices"]:
            print(choice["message"]["content"])
            choicel.append(choice["message"]["content"])
        convs[c_id]["Conversation"][u_id]["Undercutting"] = choicel
        
        
with open(AutoAnnatationOutputname,"w") as f:
   json.dump(convs, f, indent=1)