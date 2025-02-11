import cv2
from transformers import AutoProcessor, AutoModelForImageTextToText, pipeline
import torch
import logging
import time
from PIL import Image
import sys
from threading import Thread, Lock
from queue import Queue

def setup_logging():
    """Configure logging with basic formatting"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class CaptionGenerator:
    def __init__(self, processor, model, device):
        self.processor = processor
        self.model = model
        self.device = device
        self.current_caption = f"Initializing caption... ({device.upper()})"
        self.caption_queue = Queue(maxsize=1)
        self.lock = Lock()
        self.running = True
        self.thread = Thread(target=self._caption_worker)
        self.thread.daemon = True
        self.thread.start()

    def _caption_worker(self):
        while self.running:
            try:
                if not self.caption_queue.empty():
                    frame = self.caption_queue.get()
                    caption = self._generate_caption(frame)
                    with self.lock:
                        self.current_caption = caption
            except Exception as e:
                logging.error(f"Caption worker error: {str(e)}")
            time.sleep(0.1)  # Prevent busy waiting

    def _generate_caption(self, image):
        try:
            # Resize to 640x480 (or any other size)
            image_resized = cv2.resize(image, (640, 480))

            # Convert to RGB
            rgb_image = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)

            # Process the image for captioning
            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {name: tensor.to(self.device) for name, tensor in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=30,
                    num_beams=5,
                    num_return_sequences=1
                )

            caption = self.processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
            return f"BLIP: {caption} ({self.device.upper()})"
        except Exception as e:
            logging.error(f"Caption generation error: {str(e)}")
            return f"BLIP: Caption generation failed ({self.device.upper()})"

    def update_frame(self, frame):
        if self.caption_queue.empty():
            try:
                self.caption_queue.put_nowait(frame.copy())
            except:
                pass  # Queue is full, skip this frame

    def get_caption(self):
        with self.lock:
            return self.current_caption

    def stop(self):
        self.running = False
        self.thread.join()

def get_gpu_usage():
    """Get the GPU memory usage and approximate utilization"""
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
        memory_total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)  # MB

        memory_used_percent = (memory_allocated / memory_total) * 100
        gpu_info = f"GPU Memory Usage: {memory_used_percent:.2f}% | Allocated: {memory_allocated:.2f} MB / {memory_total:.2f} MB"
        
        return gpu_info
    else:
        return "GPU not available"

def load_models():
    """Load BLIP model"""
    try:
        blip_processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        blip_model = AutoModelForImageTextToText.from_pretrained("Salesforce/blip-image-captioning-large")

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if device == 'cuda':
            # Set GPU memory usage limit to 90%
            torch.cuda.set_per_process_memory_fraction(0.9)
            blip_model = blip_model.to('cuda')

        return blip_processor, blip_model, device
    except Exception as e:
        logging.error(f"Failed to load models: {str(e)}")
        return None, None, None


def describe_image(image_path, processor, model, device):
    """Generate a caption for a single image"""
    try:
        # Load the image
        image = Image.open(image_path).convert("RGB")

        # Process the image for captioning
        inputs = processor(images=image, return_tensors="pt")
        inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=100,
                num_beams=5,
                num_return_sequences=1
            )

        caption = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
        logger.info(f"Caption for {image_path}: {caption}")
        return caption
    except Exception as e:
        logger.error(f"Failed to generate caption for {image_path}: {str(e)}")
        return None

if __name__ == "__main__":
    logger = setup_logging()

    logger.info("Loading BLIP model...")
    blip_processor, blip_model, device = load_models()
    if None in (blip_processor, blip_model):
        logging.error("Failed to load the BLIP model. Exiting.")
        sys.exit(1)

    logger.info(f"Using {device.upper()} for inference.")


    image_path = input("Enter the path to the image: ")
    describe_image(image_path, blip_processor, blip_model, device)
    

# Загрузка предобученной модели для генерации ответов
qa_pipeline = pipeline("question-answering")

# Пример использования модели
context = "BLIP_CAM generated description goes here."
question = "What is the main idea of the description?"

result = qa_pipeline(question=question, context=context)
print(result)
