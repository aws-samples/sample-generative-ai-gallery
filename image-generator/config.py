from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AppConfig:
    """Configuration settings for the application."""
    # AWS Configuration
    BEDROCK_REGION: str = "us-east-1"  # Nova Canvas is only available in us-east-1
    DYNAMODB_REGION: str = "us-west-2"  # DynamoDB is in us-west-2
    S3_BUCKET: str = 'amazon-bedrock-gallery-global-<your-unique-id>'
    S3_PREFIX: str = 'images/base-image/'
    DYNAMODB_TABLE: str = 'ddb-amazon-bedrock-gallery-base-resource'
    
    # Model IDs
    CLAUDE_MODEL_ID: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    NOVA_CANVAS_MODEL_ID: str = 'amazon.nova-canvas-v1:0'
    
    # Image Generation Configuration
    IMAGE_WIDTH: int = 720
    IMAGE_HEIGHT: int = 1280
    CFG_SCALE: float = 8.0
    NUMBER_OF_IMAGES: int = 1
    IMAGE_GENERATION_DELAY: int = 3  # seconds

# Historical Periods (5 significant eras)
HISTORICAL_PERIODS: List[str] = [
    "ancient_rome",
    # "medieval_period",
    # "renaissance"
]

# Gender options
GENDERS: List[str] = ["male", "female"]

# Skin tone options
SKIN_TONES: List[str] = [
    "light_pale_white",
    "white_fair",
    "medium_white_to_olive",
    "olive_tone",
    "light_brown",
    "dark_brown"
]

# Professions by historical period
PROFESSIONS: Dict[str, List[str]] = {
    "ancient_rome": [
        "senator",
        "philosopher",
        "military_general",
        "merchant"
    ],
    "medieval_period": [
        "knight",
        "monk_nun",
        "minstrel",
        "astrologer"
    ]
}

# Artistic styles with representative artists
ARTISTIC_STYLES: List[str] = [
    "realism_style_of_gustave_courbet",
    "impressionism_style_of_claude_monet",
]

# Display names for Prompt
DISPLAY_NAMES: Dict[str, Dict] = {
    "historical_periods": {
        "ancient_rome": "Ancient Rome (27 BC - 476 AD)",
        "medieval_period": "Medieval Period (5th-15th century)",
        "renaissance": "Renaissance (14th-17th century)"
    },
    "genders": {
        "male": "Male",
        "female": "Female"
    },
    "skin_tones": {
        "light_pale_white": "Light, Pale, White",
        "white_fair": "White, Fair",
        "medium_white_to_olive": "Medium White to Olive",
        "olive_tone": "Olive Tone",
        "light_brown": "Light Brown",
        "dark_brown": "Dark Brown"
    },
    "professions": {
        "ancient_rome": {
            "senator": "Senator",
            "philosopher": "Philosopher",
            "military_general": "Military General",
            "merchant": "Merchant"
        },
        "medieval_period": {
            "knight": "Knight",
            "monk_nun": "Monk/Nun",
            "minstrel": "Minstrel",
            "astrologer": "Astrologer"
        },
        "renaissance": {
            "painter": "Painter",
            "scholar": "Scholar",
            "merchant": "Merchant",
            "nobleman_noblewoman": "Nobleman/Noblewoman"
        },
    },
    "artistic_styles": {
        "realism_style_of_gustave_courbet": "Realism (style of Gustave Courbet)",
        "impressionism_style_of_claude_monet": "Impressionism (style of Claude Monet)"
    }
}

# System prompt for Claude
SYSTEM_PROMPT: str = """
You are an expert at creating image generation prompts for portrait art. Your task is to generate detailed prompts for Amazon Nova Canvas based on specific historical and artistic parameters. For each set of variables, create a complete portrait concept that includes:

1. A main image prompt that reads like a caption, not a command
2. A negative prompt that lists elements to exclude
3. A brief fictional character backstory

Always format your response as a JSON object with fields for "prompt", "negative_prompt", and "story".

Remember these key principles for image generation:
- Image models don't understand negation (words like "no", "not", "without")
- Always describe what SHOULD be in the image, not what should be excluded
- The portrait must show a single person facing forward with clearly visible facial features
- The subject must be looking directly at the viewer with their eyes clearly visible
- Frame the portrait as a head and upper body (bust/upper torso) composition
- Include period-appropriate details for clothing, environment, and context
- Incorporate the specific artistic style's techniques and visual qualities
- The image must be rendered in oil painting style, with visible brush strokes and rich texture
- Emphasize the depth and richness of oil paint, with characteristic blending and layering
- Include the natural sheen and luminosity typical of oil paintings
- Ensure the painting has the traditional oil painting finish and appearance
""" 