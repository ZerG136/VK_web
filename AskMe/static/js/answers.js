document.addEventListener('DOMContentLoaded', function () {
    const cards = document.getElementsByClassName('card');

    for (const card of cards) {
        const upvoteButton = card.querySelector('.upvote_ans');
        const downvoteButton = card.querySelector('.downvote_ans');
        const likeCounter = card.querySelector('.counter_ans');
        const answerId = card.querySelector('.upvote_ans').getAttribute('data-answer-id');

        updateButtonState(upvoteButton, 'like');
        updateButtonState(downvoteButton, 'dislike');

        upvoteButton.addEventListener('click', function () {
            handleVote(answerId, 'like', likeCounter, upvoteButton, downvoteButton);
        });

        downvoteButton.addEventListener('click', function () {
            handleVote(answerId, 'dislike', likeCounter, upvoteButton, downvoteButton);
        });

        const correctCheckbox = card.querySelector('.flexCheckChecked');
        if (correctCheckbox) {
            addCorrectAnswerCheckboxHandler(correctCheckbox, answerId);
        }
        function addCorrectAnswerCheckboxHandler(checkbox, answerId) {
            console.log(answerId)
            checkbox.addEventListener('change', function () {
                if (window.user_is_authenticated === "False") {
                    alert("You need to log in to modify the correct answer.");
                    return;
                }

                if (checkbox.disabled) {
                    return;
                }

                const action = checkbox.checked ? 'mark_correct' : 'unmark_correct';

                console.log(window.MARK_ANSWER_URL)
                console.log(window.RATE_ANSWER_URL)

                fetch(window.MARK_ANSWER_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.CSRF_TOKEN,
                    },
                    body: JSON.stringify({
                        answer_id: answerId,
                        question_id: window.questionID
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
                    if (!data.message) {
                        alert('Error: ' + data.error);  
                        checkbox.checked = !checkbox.checked;  
                    }
                })
                .catch(error => {
                    alert('Error: ' + error.message);
                });
            });
        }

        function handleVote(answerId, action, likeCounter, upvoteButton, downvoteButton) {
            console.log(action)
            let currentUpvoteAction = upvoteButton.getAttribute('data-action');
            let currentDownvoteAction = downvoteButton.getAttribute('data-action');
            
            if (action === 'like' && currentUpvoteAction === 'like') {
                action = 'none'; 
            } else if (action === 'dislike' && currentDownvoteAction === 'dislike') {
                action = 'none'; 
            }

            if (window.user_is_authenticated == "False") 
            {
                alert("You need to log in to vote.");
                return;
            }

            fetch(window.RATE_ANSWER_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.CSRF_TOKEN,
                },
                body: JSON.stringify({
                    answer_id: answerId,
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