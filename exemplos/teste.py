import subprocess
import glob
import json
import datetime

EXAM_PATH = './inputs/'
OUTPUT_PATH = './outputs/'
MODEL_PATH='./model/'

exam_data = '{}exam_data.json'.format(EXAM_PATH)


print(f"""Start Model -{datetime.datetime.now()}""")
prediction_output = subprocess.run(['python', MODEL_PATH+'predict.py', '--exam_path', EXAM_PATH, '--exam_data', exam_data, '--model_output', OUTPUT_PATH], 
stdout=subprocess.PIPE, universal_newlines=True)
print(f"""End Model -{datetime.datetime.now()}""")

print("####### Finish Model with sucess #######")
print(prediction_output)

file_list = glob.glob(OUTPUT_PATH+"**/*.json", recursive=True)
outputs = []
for file in file_list:

    # Read output file
    output_data = open(file).read()
    output_data = json.loads(output_data)
    print(output_data)

print(f"""End Process -{datetime.datetime.now()}""")

#para teste 
#docker build -t teste:latest -f Dockerfile.dev . && docker run teste