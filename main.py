import os
import json
import time
import random
import logging
import queue
import multiprocessing
from datetime import datetime
from multiprocessing import Pool, Queue, Event, Process

# Constants for directories
INCOMING_DIR = 'database'
PROCESSED_DIR = 'database_2'

# Ensure directories exist
os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def receptor_loop(shared_queue, stop_event):
    while not stop_event.is_set():
        try:
            image_files = [f for f in os.listdir(INCOMING_DIR) if f.endswith('.txt')]
            for filename in image_files:
                filepath = os.path.join(INCOMING_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    data['receptor_timestamp'] = time.time()
                    try:
                        shared_queue.put(data, timeout=1)
                        os.remove(filepath)
                        logger.info(f"[RECEPTOR] Queued image: {filename}")
                    except queue.Full:
                        logger.warning("[RECEPTOR] Queue is full, retrying later...")
                except Exception as e:
                    logger.error(f"[RECEPTOR] Error with {filename}: {e}")
                    os.remove(filepath)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"[RECEPTOR] Unexpected error: {e}")
            time.sleep(1)

def process_image(image_data):
    time.sleep(random.uniform(1.0, 5.0))  # Simulate processing
    image_data['processed_timestamp'] = time.time()
    image_data['processing_notes'] = 'Processed successfully'
    logger.info(f"[PROCESSOR] Processed image: {image_data['image_id']}")
    return image_data

def writer_loop(processed_queue, stop_event):
    while not stop_event.is_set():
        try:
            image_data = processed_queue.get(timeout=1)
            filename = f"{image_data['image_id']}.txt"
            filepath = os.path.join(PROCESSED_DIR, filename)
            with open(filepath, 'w') as f:
                json.dump(image_data, f, indent=2)
            logger.info(f"[WRITER] Wrote processed image: {filename}")
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"[WRITER] Error: {e}")

def processor_worker(input_queue, output_queue, stop_event):
    def async_callback(results):
        for result in results:
            try:
                output_queue.put(result, timeout=1)
            except queue.Full:
                logger.warning("[PROCESSOR] Output queue full")

    with Pool(processes=4) as pool:
        while not stop_event.is_set():
            images = []
            try:
                for _ in range(min(5, input_queue.qsize())):
                    try:
                        images.append(input_queue.get(timeout=0.5))
                    except queue.Empty:
                        break

                if images:
                    async_result = pool.map_async(process_image, images, callback=async_callback)
                    async_result.wait(timeout=10)  # Espera razonable
            except KeyboardInterrupt:
                logger.warning("[PROCESSOR] KeyboardInterrupt inside worker loop")
                stop_event.set()
                break
            except Exception as e:
                logger.error(f"[PROCESSOR] Exception in worker: {e}")
                time.sleep(0.5)

        logger.info("[PROCESSOR] Closing pool...")
        pool.close()
        pool.join()
        logger.info("[PROCESSOR] Pool closed.")

def main():
    shared_queue = Queue(maxsize=100)
    processed_queue = Queue(maxsize=100)
    stop_event = Event()

    receptor_proc = Process(target=receptor_loop, args=(shared_queue, stop_event))
    processor_proc = Process(target=processor_worker, args=(shared_queue, processed_queue, stop_event))
    writer_proc = Process(target=writer_loop, args=(processed_queue, stop_event))

    processes = [receptor_proc, processor_proc, writer_proc]

    for p in processes:
        p.start()

    try:
        while any(p.is_alive() for p in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("[MAIN] KeyboardInterrupt received. Stopping processes...")
        stop_event.set()
    finally:
        logger.info("[MAIN] Waiting for processes to finish...")
        for p in processes:
            p.join()
        logger.info("[MAIN] All processes have been stopped.")

if __name__ == '__main__':
    main()