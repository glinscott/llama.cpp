#!/usr/bin/python3
import os
import sys
import subprocess
import threading
import time
from googleapiclient.discovery import build

API_KEY = os.getenv("GOOGLE_SEARCH_KEY")
API_CX = os.getenv("GOOGLE_CX")

def search(search_term, api_key=API_KEY, cse_id=API_CX, **kwargs):
  service = build("customsearch", "v1", developerKey=api_key)
  res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
  return res

def forward_user_input(process):
  while True:
    # Wait for user input and forward it to the process
    user_input = input()
    process.stdin.write((user_input + "\n").encode())
    process.stdin.flush()

def main():
  p = subprocess.Popen(['stdbuf', '-o0', 'examples/vicuna.sh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
  #p = subprocess.Popen(['stdbuf', '-o0'] + ["examples/vicuna.sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)

  # Create and start a thread for reading the user input
  input_thread = threading.Thread(target=forward_user_input, args=[p])
  input_thread.start()

  query = ""
  buffer = ""
  started = False
  bytes_array = bytearray()
  for char in iter(lambda: p.stdout.read(1), b''):
    bytes_array += char
    try:
      char = bytes_array.decode()
      bytes_array.clear()
    except:
      continue
    sys.stdout.write(char)
    sys.stdout.flush()

    if char == '\n':
      buffer = ""
    else:
      buffer += char

    if buffer.startswith("[user]"):
      started = True

    if not started:
      continue

    if buffer.startswith("Search:"):
      # Reset query
      query = buffer[8:]
    elif buffer.startswith("Observation:"):
      time.sleep(1)
      items = search(query)['items']
      result = "###\\".join(["Title: %s\\Snippet: %s\\" % (item["title"], item["snippet"]) for item in items[:2]])
      #print('search results:', result)
      result += "\n\n"
      p.stdin.write(result.encode())
      p.stdin.flush()
      buffer = ""

  raise Exception('exited unexpectedly')

  output_thread = threading.Thread(target=read_output, args=(p))
  output_thread.start()

  while True:
    # Collect user input and put it into the queue
    user_input = input()
    print("foo: ", user_input)
    input_queue.put(user_input)

if __name__ == "__main__":
  main()