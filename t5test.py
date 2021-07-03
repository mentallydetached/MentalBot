from simpletransformers.t5 import T5Model
import sys

model = T5Model(
    "t5",
    "t5-base",
    use_cuda=False
)

inp = sys.argv[1]
print(inp)

match_rate = model.predict([f"stsb sentence1: How quickly does the fox jump over the quick brown dog? sentence2: {inp}"])
match_rate = match_rate[0]
print(match_rate)
match_percent = ((float(match_rate) * 100) / 5)
print(match_percent)
