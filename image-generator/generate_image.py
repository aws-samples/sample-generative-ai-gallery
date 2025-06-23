import boto3
import json
import random
import base64
import io
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from PIL import Image
from botocore.exceptions import ClientError
from botocore.config import Config

from config import (
    AppConfig,
    HISTORICAL_PERIODS,
    GENDERS,
    SKIN_TONES,
    PROFESSIONS,
    ARTISTIC_STYLES,
    SYSTEM_PROMPT
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageGeneratorError(Exception):
    """Custom exception for image generation errors."""
    pass

class ImageGenerator:
    """Handles image generation using Amazon Bedrock models."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        
        # Create Bedrock client in us-east-1
        self.bedrock_client = boto3.client(
            "bedrock-runtime", 
            region_name=config.BEDROCK_REGION,
            config=Config(read_timeout=300)
        )
        
        # Create S3 client in us-east-1 (same as Bedrock)
        self.s3_client = boto3.client('s3', region_name=config.BEDROCK_REGION)
        
        # Create DynamoDB client in us-west-2
        self.dynamodb = boto3.resource('dynamodb', region_name=config.DYNAMODB_REGION)
        self.table = self.dynamodb.Table(config.DYNAMODB_TABLE)
    
    def _generate_claude_prompt(self, historical_period: str, gender: str, 
                              skin_tone: str, profession: str, artistic_style: str) -> str:
        """Generate a prompt using Claude model."""
        user_prompt = f"""
        Generate a portrait-mode self-portrait concept based on these variables:

        Historical Period: {historical_period}
        Gender: {gender}
        Skin Tone: {skin_tone}
        Profession: {profession}
        Artistic Style: {artistic_style}
        """
        
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_prompt}],
                }
            ],
        }
        
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.config.CLAUDE_MODEL_ID, 
                body=json.dumps(native_request)
            )
            model_response = json.loads(response["body"].read())
            
            return model_response["content"][0]["text"]
        except Exception as e:
            raise ImageGeneratorError(f"Failed to generate Claude prompt: {e}")
    
    def _generate_image_with_nova_canvas(self, prompt: str, negative_prompt: str) -> bytes:
        """Generate an image using Nova Canvas model."""
        body = json.dumps({
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": negative_prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": self.config.NUMBER_OF_IMAGES,
                "height": self.config.IMAGE_HEIGHT,
                "width": self.config.IMAGE_WIDTH,
                "cfgScale": self.config.CFG_SCALE,
                "seed": random.randint(0, 1000000)
            }
        })
        
        try:
            response = self.bedrock_client.invoke_model(
                body=body, 
                modelId=self.config.NOVA_CANVAS_MODEL_ID, 
                accept="application/json", 
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            
            if "error" in response_body:
                raise ImageGeneratorError(f"Nova Canvas error: {response_body['error']}")
                
            base64_image = response_body.get("images")[0]
            base64_bytes = base64_image.encode('ascii')
            return base64.b64decode(base64_bytes)
        except Exception as e:
            raise ImageGeneratorError(f"Failed to generate image: {e}")
    
    def _save_image_to_s3(self, image_bytes: bytes, object_key: str) -> None:
        """Save image to S3 bucket."""
        try:
            self.s3_client.put_object(
                Bucket=self.config.S3_BUCKET,
                Key=object_key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            logger.info(f"Image saved to s3://{self.config.S3_BUCKET}/{object_key}")
        except Exception as e:
            raise ImageGeneratorError(f"Failed to save image to S3: {e}")
    
    def _create_object_key(self, historical_period: str, gender: str, skin_tone: str,
                         profession: str, artistic_style: str) -> str:
        """Create S3 object key from parameters."""
        object_key = f"{self.config.S3_PREFIX}{historical_period}-{gender}-{skin_tone}-{profession}-{artistic_style}.jpeg"
        return object_key.replace(" ", "-").replace("(", "").replace(")", "")
    
    def _save_to_dynamodb(self, historical_period: str, gender: str, skin_tone: str,
                         object_key: str, story: str) -> None:
        """Save image metadata to DynamoDB."""
        try:
            pk = f"#THEME#{historical_period}#GENDER#{gender}#SKIN#{skin_tone}"
            sk = f"#UUID#{uuid.uuid4()}"
            
            item = {
                'PK': pk,
                'SK': sk,
                'base_image_object_key': object_key,
                'story': story,
                'created_at': datetime.now().isoformat(),
                'historical_period': historical_period,
                'gender': gender,
                'skin_tone': skin_tone
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Saved metadata to DynamoDB: {pk} - {sk}")
            
        except Exception as e:
            raise ImageGeneratorError(f"Failed to save to DynamoDB: {e}")
    
    def _log_error(self, period: str, gender: str, skin_tone: str,
                  profession: str, artistic_style: str) -> None:
        """Log error to errors.txt file."""
        try:
            with open('errors.txt', 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {period}, {gender}, {skin_tone}, {profession}, {artistic_style}\n")
        except Exception as e:
            logger.error(f"Failed to write to errors.txt: {e}")
    
    def generate_and_save_image(self, period: str, gender: str, skin_tone: str,
                              profession: str, artistic_style: str) -> None:
        """Generate and save an image for a specific combination."""
        try:
            # Generate prompt using Claude
            claude_response = self._generate_claude_prompt(
                period, gender, skin_tone, profession, artistic_style
            )
            response_json = json.loads(claude_response)
            
            # Generate image using Nova Canvas
            image_bytes = self._generate_image_with_nova_canvas(
                response_json["prompt"],
                response_json["negative_prompt"]
            )
            
            # Save image to S3
            object_key = self._create_object_key(
                period, gender, skin_tone, profession, artistic_style
            )
            self._save_image_to_s3(image_bytes, object_key)
            
            # Save metadata to DynamoDB
            self._save_to_dynamodb(
                period,
                gender,
                skin_tone,
                object_key,
                response_json["story"]
            )
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            self._log_error(period, gender, skin_tone, profession, artistic_style)
            raise

def _calculate_total_combinations(
    start_from: Optional[Dict[str, str]] = None
) -> Tuple[int, Dict[str, str]]:
    """Calculate total combinations and get starting parameters.
    
    Args:
        start_from: Dictionary containing starting parameters
        
    Returns:
        Tuple of (total_combinations, start_params)
    """
    total_combinations = 0
    period_started = False
    gender_started = False
    skin_tone_started = False
    profession_started = False
    artistic_style_started = False
    
    start_params = {
        'historical_period': start_from.get('historical_period') if start_from else HISTORICAL_PERIODS[0],
        'gender': start_from.get('gender') if start_from else GENDERS[0],
        'skin_tone': start_from.get('skin_tone') if start_from else SKIN_TONES[0],
        'profession': start_from.get('profession') if start_from else None,
        'artistic_style': start_from.get('artistic_style') if start_from else None
    }
    
    for period in HISTORICAL_PERIODS:
        if not period_started and period != start_params['historical_period']:
            continue
        period_started = True
        
        for gender in GENDERS:
            if not gender_started and gender != start_params['gender']:
                continue
            gender_started = True
            
            for skin_tone in SKIN_TONES:
                if not skin_tone_started and skin_tone != start_params['skin_tone']:
                    continue
                skin_tone_started = True
                
                for profession in PROFESSIONS[period]:
                    if not profession_started and start_params['profession'] and profession != start_params['profession']:
                        continue
                    profession_started = True
                    
                    for artistic_style in ARTISTIC_STYLES:
                        if not artistic_style_started and start_params['artistic_style'] and artistic_style != start_params['artistic_style']:
                            continue
                        artistic_style_started = True
                        
                        total_combinations += 1
    
    return total_combinations, start_params

def _should_skip_combination(
    period: str,
    gender: str,
    skin_tone: str,
    profession: str,
    artistic_style: str,
    start_params: Dict[str, str],
    flags: Dict[str, bool]
) -> Tuple[bool, Dict[str, bool]]:
    """Check if current combination should be skipped based on starting parameters.
    
    Args:
        period: Current historical period
        gender: Current gender
        skin_tone: Current skin tone
        profession: Current profession
        artistic_style: Current artistic style
        start_params: Starting parameters
        flags: Current state flags
        
    Returns:
        Tuple of (should_skip, updated_flags)
    """
    if not flags['period_started'] and period != start_params['historical_period']:
        return True, flags
    flags['period_started'] = True
    
    if not flags['gender_started'] and gender != start_params['gender']:
        return True, flags
    flags['gender_started'] = True
    
    if not flags['skin_tone_started'] and skin_tone != start_params['skin_tone']:
        return True, flags
    flags['skin_tone_started'] = True
    
    if not flags['profession_started'] and start_params['profession'] and profession != start_params['profession']:
        return True, flags
    flags['profession_started'] = True
    
    if not flags['artistic_style_started'] and start_params['artistic_style'] and artistic_style != start_params['artistic_style']:
        return True, flags
    flags['artistic_style_started'] = True
    
    return False, flags

def _process_combination(
    generator: ImageGenerator,
    period: str,
    gender: str,
    skin_tone: str,
    profession: str,
    artistic_style: str,
    min_images_per_combination: int,
    config: AppConfig
) -> int:
    """Process a single combination of parameters.
    
    Args:
        generator: ImageGenerator instance
        period: Historical period
        gender: Gender
        skin_tone: Skin tone
        profession: Profession
        artistic_style: Artistic style
        min_images_per_combination: Number of images to generate
        config: Application configuration
        
    Returns:
        Number of successfully generated images
    """
    generated_count = 0
    logger.info(f"Generating images for combination: {period}, {gender}, {skin_tone}, {profession}, {artistic_style}")
    
    for _ in range(min_images_per_combination):
        time.sleep(config.IMAGE_GENERATION_DELAY)
        try:
            generator.generate_and_save_image(
                period, gender, skin_tone, profession, artistic_style
            )
            generated_count += 1
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            continue
    
    return generated_count

def generate_all_combinations(
    config: AppConfig, 
    min_images_per_combination: int = 1,
    start_from: Optional[Dict[str, str]] = None
) -> None:
    """Generate images for all possible combinations of parameters."""
    generator = ImageGenerator(config)
    
    # Calculate total combinations and get starting parameters
    total_combinations, start_params = _calculate_total_combinations(start_from)
    total_images = total_combinations * min_images_per_combination
    
    logger.info(f"Generating {total_images} images ({min_images_per_combination} per combination)")
    logger.info(f"Total combinations: {total_combinations}")
    
    # Initialize flags for combination processing
    flags = {
        'period_started': False,
        'gender_started': False,
        'skin_tone_started': False,
        'profession_started': False,
        'artistic_style_started': False
    }
    
    total_generated = 0
    for period in HISTORICAL_PERIODS:
        for gender in GENDERS:
            for skin_tone in SKIN_TONES:
                for profession in PROFESSIONS[period]:
                    for artistic_style in ARTISTIC_STYLES:
                        # Check if we should skip this combination
                        should_skip, flags = _should_skip_combination(
                            period, gender, skin_tone, profession, artistic_style,
                            start_params, flags
                        )
                        if should_skip:
                            continue
                        
                        # Process the combination
                        generated = _process_combination(
                            generator, period, gender, skin_tone, profession,
                            artistic_style, min_images_per_combination, config
                        )
                        total_generated += generated
                        logger.info(f"Generated {total_generated}/{total_images} images")

def main():
    """Main entry point for the application."""
    try:
        config = AppConfig()
        
        # Number of images to generate per combination
        min_images_per_combination = 1
        
        # Optional: Start from specific combination
        start_from = {
            'historical_period': 'future_space_age',
            'gender': 'male',
            'skin_tone': 'light_brown',
            'profession': 'robot_engineer',
            'artistic_style': 'futuristic_style'
        }
        
        # Generate all combinations
        generate_all_combinations(config, min_images_per_combination)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()

