import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import cv2
import pygame

from datetime import datetime, timedelta
from queue import Queue
from time import sleep

# Set TERM environment variable
os.environ['TERM'] = 'xterm-256color'  # or another appropriate value

# Set CUDA environment variable if using GPU acceleration
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=1,
                        help="How real-time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    parser.add_argument("--max_words", default=10,
                        help="Maximum number of words to display at once.", type=int)
    parser.add_argument("--language", default="en",
                        help="Language for the transcription model.", type=str)
    parser.add_argument("--output_file", default="transcription.txt",
                        help="Output file to save the transcription.", type=str)

    args = parser.parse_args()

    phrase_time = None
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)

    audio_model = whisper.load_model("large")

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout
    max_words = args.max_words
    language = args.language
    output_file = args.output_file

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Model loaded.\n")

    def update_buffer(text, buffer, max_words):
        words = buffer.split()
        words += text.split()
        while len(words) > max_words:
            words.pop(0)
        return ' '.join(words)

    buffer = ""

    # Initialize Pygame
    pygame.init()
    font = pygame.font.SysFont('Arial', 24)
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Live Feed with Captions")

    # OpenCV video capture
    cap = cv2.VideoCapture(1)

    while True:
        try:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break

            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                phrase_time = now

                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                result = audio_model.transcribe(audio_np, language=language, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                buffer = update_buffer(text, buffer, max_words)

                # Write the transcription to the output file
                with open(output_file, 'a') as f:
                    f.write(text + ' ')

            # Clear the screen
            screen.fill((0, 0, 0))

            # Convert the frame to a format suitable for Pygame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)

            # Blit the frame onto the screen
            screen.blit(frame, (0, 0))

            # Render the text
            text_surface = font.render(buffer, True, (255, 255, 255))
            screen.blit(text_surface, (10, 450))

            # Update the display
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    return

            sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)

    # Save the final transcription to the output file
    with open(output_file, 'a') as f:
        f.write('\n'.join(transcription))

if __name__ == "__main__":
    main()
