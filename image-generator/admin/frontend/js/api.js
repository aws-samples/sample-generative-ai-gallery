// API utility functions
class ImageGalleryAPI {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async fetchImages(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            // Add pagination params
            queryParams.append('page', params.page || 1);
            queryParams.append('per_page', params.per_page || APP_CONFIG.DEFAULT_PER_PAGE);
            
            // Add filter params
            if (params.gender) queryParams.append('gender', params.gender);
            if (params.skin_tone) queryParams.append('skin_tone', params.skin_tone);
            if (params.profession) queryParams.append('profession', params.profession);
            if (params.historical_period) queryParams.append('historical_period', params.historical_period);
            if (params.artistic_style) queryParams.append('artistic_style', params.artistic_style);
            
            const response = await fetch(`${this.baseURL}${API_CONFIG.ENDPOINTS.IMAGES}?${queryParams}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching images:', error);
            throw error;
        }
    }

    async fetchImageDetail(key) {
        try {
            const encodedKey = encodeURIComponent(key);
            const response = await fetch(`${this.baseURL}${API_CONFIG.ENDPOINTS.IMAGE_DETAIL}/${encodedKey}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching image detail:', error);
            throw error;
        }
    }

    async deleteImage(key) {
        try {
            const encodedKey = encodeURIComponent(key);
            const response = await fetch(`${this.baseURL}${API_CONFIG.ENDPOINTS.DELETE_IMAGE}/${encodedKey}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error deleting image:', error);
            throw error;
        }
    }

    async deleteMultipleImages(imageKeys) {
        try {
            const response = await fetch(`${this.baseURL}${API_CONFIG.ENDPOINTS.DELETE_MULTIPLE}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    selected_images: imageKeys
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error deleting multiple images:', error);
            throw error;
        }
    }
}

// Create global API instance
const api = new ImageGalleryAPI();
