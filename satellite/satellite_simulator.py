import os
import json
import time
import random
import logging
from datetime import datetime

INCOMING_DIR = '../database'
os.makedirs(INCOMING_DIR, exist_ok=True)

class SatelliteImageGenerator:
    def __init__(self,
                 incoming_dir: str = INCOMING_DIR,
                 min_interval: float = 0.1,
                 max_interval: float = 2.0,
                 min_images: int = 5,
                 max_images: int = 15):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

        self.incoming_dir = incoming_dir
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.min_images = min_images
        self.max_images = max_images

        os.makedirs(self.incoming_dir, exist_ok=True)

    def generate_image_metadata(self, image_id):
        image_types = ['infrared', 'visible_light', 'thermal', 'radar', 'multispectral']
        return {
            'image_id': f'sat_img_{image_id}',
            'timestamp': datetime.now().isoformat(),
            'image_type': random.choice(image_types),
            'latitude': random.uniform(-90, 90),
            'longitude': random.uniform(-180, 180),
            'resolution_meters': random.choice([1, 5, 10, 30]),
            'cloud_cover_percentage': random.uniform(0, 100),
            'additional_metadata': {
                'orbit_number': random.randint(1000, 9999),
                'sensor_temperature': random.uniform(-50, 50)
            }
        }

    def run(self):
        self.logger.info("Satellite image generator started")
        try:
            while True:
                time.sleep(random.uniform(self.min_interval, self.max_interval))
                for i in range(random.randint(self.min_images, self.max_images)):
                    image_id = f'{int(time.time())}_{i}'
                    data = self.generate_image_metadata(image_id)
                    filename = f'{data["image_id"]}.txt'
                    filepath = os.path.join(self.incoming_dir, filename)
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2)
                    self.logger.info(f"Generated image: {filename}")
        except KeyboardInterrupt:
            self.logger.info("Satellite image generator stopped")

def main():
    SatelliteImageGenerator().run()

if __name__ == '__main__':
    main()
