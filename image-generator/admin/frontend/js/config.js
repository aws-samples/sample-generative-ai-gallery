// API Configuration
const API_CONFIG = {
    // For local development
    BASE_URL: 'http://localhost:5001',
    
    // For production (API Gateway URL)
    // BASE_URL: 'https://5yi9e07ex6.execute-api.us-east-1.amazonaws.com/prod',
    
    ENDPOINTS: {
        IMAGES: '/api/images',
        IMAGE_DETAIL: '/api/images',
        DELETE_IMAGE: '/api/images',
        DELETE_MULTIPLE: '/api/images/delete-multiple'
    }
};

// App Configuration
const APP_CONFIG = {
    DEFAULT_PER_PAGE: 12,
    MAX_PER_PAGE: 50
};
