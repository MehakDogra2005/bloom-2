// This is a script to detect and fix CORS issues with Google Cloud Storage images
// Add the following line to the HTML file to include this script:
// <script src="/static/js/cors-fixer.js"></script>

(function() {
    // Function to check if an image exists and is accessible
    function checkImageExists(url, callback, timeout = 5000) {
        const img = new Image();
        
        // Add timeout for stalled image loads
        const timer = setTimeout(() => {
            console.warn(`Image check timeout: ${url}`);
            callback(false);
        }, timeout);
        
        img.onload = function() { 
            clearTimeout(timer);
            callback(true); 
        };
        
        img.onerror = function() { 
            clearTimeout(timer);
            console.warn(`Image failed to load: ${url}`);
            callback(false); 
        };
        
        // Set crossOrigin to anonymous to allow CORS requests
        img.crossOrigin = "anonymous";
        img.src = url;
    }

    // Function to preload an image and return a promise
    function preloadImage(url, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            
            // Add a timeout to handle stalled image loads
            const timer = setTimeout(() => {
                console.warn(`Image load timeout: ${url}`);
                reject(new Error(`Image load timeout: ${url}`));
            }, timeout);
            
            img.onload = () => {
                clearTimeout(timer);
                resolve(url);
            };
            
            img.onerror = () => {
                clearTimeout(timer);
                console.warn(`Failed to load image: ${url}`);
                reject(new Error(`Failed to load image: ${url}`));
            };
            
            // Set crossOrigin to anonymous to allow CORS requests
            img.crossOrigin = "anonymous";
            img.src = url;
        });
    }

    // Expose these functions globally
    window.imageUtils = {
        checkImageExists: checkImageExists,
        preloadImage: preloadImage
    };
})();
