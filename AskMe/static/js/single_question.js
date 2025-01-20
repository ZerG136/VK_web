    document.addEventListener('DOMContentLoaded', function () {
        const cards = document.getElementsByClassName('w-100');

        for (const card of cards) {
            const upvoteButton = card.querySelector('.upvote');
            const downvoteButton = card.querySelector('.downvote');
            const likeCounter = card.querySelector('.counter');

            // Чтобы не было Cannot read properties of null (reading 'getAttribute'), на работу не влияет
            if (!upvoteButton) {
                return;
            }
    
            const questionId = card.querySelector('.upvote').getAttribute('data-question-id');

            updateButtonState(upvoteButton, 'like');
            updateButtonState(downvoteButton, 'dislike');

            upvoteButton.addEventListener('click', function () {
                handleVote(questionId, 'like', likeCounter, upvoteButton, downvoteButton);
            });

            downvoteButton.addEventListener('click', function () {
                handleVote(questionId, 'dislike', likeCounter, upvoteButton, downvoteButton);
            });

            function handleVote(questionId, action, likeCounter, upvoteButton, downvoteButton) {
                let currentUpvoteAction = upvoteButton.getAttribute('data-action');
                let currentDownvoteAction = downvoteButton.getAttribute('data-action');

                if (action === 'like' && currentUpvoteAction === 'like') {
                    action = 'none';
                } else if (action === 'dislike' && currentDownvoteAction === 'dislike') {
                    action = 'none';
                }

                if (window.user_is_authenticated === "False") {
                    alert("You need to log in to vote.");
                    return;
                }

                fetch(window.RATE_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": window.CSRF_TOKEN,
                    },
                    body: JSON.stringify({
                        question_id: questionId,
                        action: action,
                    }),
                })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            alert("You need to log in to vote.");
                        } else {
                            alert("Error: " + response.statusText);
                        }
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    likeCounter.textContent = data.new_rate;

                    if (action === 'like') {
                        upvoteButton.setAttribute('data-action', 'like');
                        downvoteButton.setAttribute('data-action', 'none');
                    } else if (action === 'dislike') {
                        downvoteButton.setAttribute('data-action', 'dislike');
                        upvoteButton.setAttribute('data-action', 'none');
                    } else {
                        upvoteButton.setAttribute('data-action', 'none');
                        downvoteButton.setAttribute('data-action', 'none');
                    }

                    updateButtonState(upvoteButton, 'like');
                    updateButtonState(downvoteButton, 'dislike');
                })
                .catch(error => {
                    alert("Ошибка: " + error.message);
                });
            }

            function updateButtonState(button, type) {
                const action = button.getAttribute('data-action');

                if (type === 'like') {
                    if (action === 'like') {
                        button.src = window.LIKED_IMG;  
                    } else {
                        button.src = window.LIKE_IMG; 
                    }
                } else if (type === 'dislike') {
                    if (action === 'dislike') {
                        button.src = window.DISLIKED_IMG; 
                    } else {
                        button.src = window.DISLIKE_IMG; 
                    }
                }
            }
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }