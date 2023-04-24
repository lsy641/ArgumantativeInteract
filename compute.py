import os
import openai
import json
import time

def compute_accuracy(gt_file, data_file):
    with open(gt_file) as f:
        gt_data = json.load(f)
    with open(data_file) as f:
        result_data = json.load(f)

    total_conflicts = 0
    correct_conflicts = 0
    for conv1, conv2 in zip(gt_data, result_data):
        total_conflicts += conv1["count"]
        if conv1["count"] == 0 or conv2["count"] == 0:
            continue
        
        for conflict1 in conv1["conflicts"]:
            for conflict2 in conv2["conflicts"]:
                if conflict1["utter1"] == conflict2["utter1"] and conflict1["utter2"] == conflict2["utter2"]:
                    correct_conflicts +=1
    return total_conflicts, correct_conflicts
        

if __name__ == "__main__":
    gt_file = "ground_truth_data.json"
    eval_file = "llm_ns_data_semantic_only.json"
    total_conflicts, correct_conflicts = compute_accuracy(gt_file, eval_file)
    print("total count = ", total_conflicts)
    print("correct count = ", correct_conflicts)
    print("accuracy = ", float(correct_conflicts) / float(total_conflicts))