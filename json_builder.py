import json 

names = ["abortion", "transgender"]
samples = []
for fname in names:
    f = open(fname, "r")
    raw_list = f.read().split("Con&")[1:]   
    
    for raw in raw_list:
        sample = {}
        sample["Topic"] = fname.capitalize()
        
        items = raw.split("\n")
        conv = []
        speaker = []
        for idx, item in enumerate(items):
            if not item:
                continue
            temp = {}
            iteml = item.split(":") 
            print(iteml)        
            assert len(iteml) == 2
            assert "Person" in iteml[0]
            temp["Content"] = iteml[1].strip()
            if iteml[0].strip()[6] not in speaker:
                speaker.append(iteml[0].strip()[6])
            temp["Speaker_id"] = speaker.index(iteml[0].strip()[6])
            temp["Utterance_id"] = idx
            conv.append(temp)
            
        sample["Speaker_count"] = len(speaker)
        sample["Conversation"] = conv 
        samples.append(sample) 
    
with open(f"abortion_transgender_data.json", "w") as ff:
    json.dump(samples, ff, indent=1)       
            