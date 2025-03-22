// like-button.js - Add to your website to create a floating like button with archive link
(function() {
    // Create a self-contained function that initializes the like button
    function initLikeButton(config) {
        // Default config values
        const settings = {
            pageId: null,
            position: 'bottom-right',
            archiveUrl: '/archive'
        };
        
        // Merge provided config with defaults
        Object.assign(settings, config);
        
        // Validate required parameters
        if (!settings.pageId) {
            console.error('LikeButton Error: pageId is required');
            return;
        }
        
        // Create a container for all our elements
        const containerElement = document.createElement('div');
        containerElement.className = 'like-button-container';
        
        // Set position based on config
        if (settings.position === 'bottom-right') {
            containerElement.style.bottom = '30px';
            containerElement.style.right = '30px';
        } else if (settings.position === 'bottom-left') {
            containerElement.style.bottom = '30px';
            containerElement.style.left = '30px';
        } else if (settings.position === 'top-right') {
            containerElement.style.top = '30px';
            containerElement.style.right = '30px';
        } else if (settings.position === 'top-left') {
            containerElement.style.top = '30px';
            containerElement.style.left = '30px';
        }
        
        document.body.appendChild(containerElement);
        
        // Create a horizontal container for count and archive link
        const horizontalContainer = document.createElement('div');
        horizontalContainer.className = 'horizontal-container';
        containerElement.appendChild(horizontalContainer);
        
        // Add archive link
        const archiveLink = document.createElement('a');
        archiveLink.className = 'archive-link';
        archiveLink.href = settings.archiveUrl;
        archiveLink.innerHTML = 'View Archive';
        horizontalContainer.appendChild(archiveLink);

        // Create and append the like count element
        const likeCountElement = document.createElement('div');
        likeCountElement.className = 'like-count';
        
        const countSpan = document.createElement('span');
        countSpan.className = 'count-value';
        countSpan.textContent = '0';
        
        likeCountElement.appendChild(countSpan);
        likeCountElement.appendChild(document.createTextNode(' Likes'));
        horizontalContainer.appendChild(likeCountElement);
        
        // Add like button
        const likeButton = document.createElement('button');
        likeButton.className = 'like-button';
        likeButton.innerHTML = '<span class="heart-icon">♥</span>';
        containerElement.appendChild(likeButton);
        
        // Handle button functionality
        // Check if user has already liked this specific page in this session
        const storageKey = 'hasLiked-' + settings.pageId;
        const hasLiked = sessionStorage.getItem(storageKey) === 'true';
        if (hasLiked) {
            likeButton.disabled = true;
        }
        
        // Get initial like count for this page
        fetchLikeCount();
        
        likeButton.addEventListener('click', function() {
            if (!hasLiked) {
                incrementLike();
                likeButton.disabled = true;
                likeButton.classList.add('liked');
                sessionStorage.setItem(storageKey, 'true');
            }
        });
        
        function fetchLikeCount() {
            fetch('/api/likes?pageId=' + encodeURIComponent(settings.pageId))
                .then(response => response.json())
                .then(data => {
                    updateLikeCount(data.count);
                })
                .catch(error => {
                    console.error('Error fetching like count:', error);
                });
        }
        
        function incrementLike() {
            fetch('/api/likes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pageId: settings.pageId })
            })
            .then(response => response.json())
            .then(data => {
                updateLikeCount(data.count);
            })
            .catch(error => {
                console.error('Error incrementing like count:', error);
                // Revert button state if error occurs
                likeButton.disabled = false;
                sessionStorage.removeItem(storageKey);
            });
        }
        
        function updateLikeCount(count) {
            countSpan.textContent = count;
        }
    }
    
    // Add styles once for all instances
    const styles = document.createElement('style');
    styles.textContent = `
        .like-button-container {
            position: fixed;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            z-index: 1000;
        }
        
        .horizontal-container {
            display: flex;
            flex-direction: row;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .like-button {
            background-color: #1da1f2;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .like-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        
        .like-button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .like-count {
            background-color: white;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            font-weight: bold;
            white-space: nowrap;
            color: #333333;
        }
        
        .archive-link {
            background-color: white;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            font-weight: bold;
            text-decoration: none;
            color: #1da1f2;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .archive-link:hover {
            background-color: #f5f8fa;
            transform: translateY(-2px);
        }
        
        .heart-icon {
            color: #e0245e;
        }
        
        .liked {
            animation: liked 0.4s ease;
        }
        
        @keyframes liked {
            0% { transform: scale(1); }
            50% { transform: scale(1.3); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(styles);
    
    // Make the init function available globally
    window.LikeButton = {
        init: initLikeButton
    };
    
    // Auto-initialize if data-attributes are present
    document.addEventListener('DOMContentLoaded', function() {
        const scripts = document.querySelectorAll('script[data-like-button-id]');
        scripts.forEach(script => {
            const pageId = script.getAttribute('data-like-button-id');
            const position = script.getAttribute('data-like-button-position') || 'bottom-right';
            const archiveUrl = script.getAttribute('data-like-button-archive') || '/archive';
            
            if (pageId) {
                initLikeButton({
                    pageId: pageId,
                    position: position,
                    archiveUrl: archiveUrl
                });
            }
        });
    });
})();
