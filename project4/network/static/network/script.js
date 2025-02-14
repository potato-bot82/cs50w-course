function editPost(postId) {
    const postContentElement = document.getElementById(`post-content-${postId}`);
    const originalContent = postContentElement.innerText;

    // Create a textarea for editing
    const textArea = document.createElement("textarea");
    textArea.value = originalContent;
    textArea.id = `edit-textarea-${postId}`;
    textArea.style.width = "100%";
    textArea.style.height = "60px";

    // Create a save button
    const saveButton = document.createElement("button");
    saveButton.innerText = "Save";
    saveButton.onclick = function () {
        saveEdit(postId);
    };

    // Replace content with textarea and save button
    const postDiv = document.getElementById(`post-${postId}`);
    postDiv.innerHTML = "";
    postDiv.appendChild(textArea);
    postDiv.appendChild(saveButton);
}

function saveEdit(postId) {
    const newContent = document.getElementById(`edit-textarea-${postId}`).value.trim();

    if (newContent === "") {
        alert("Post content cannot be empty!");
        return;
    }

    fetch(`/edit_post/${postId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken(),
        },
        body: `content=${encodeURIComponent(newContent)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Update the post content with the new text
            document.getElementById(`post-${postId}`).innerHTML = `
                <p id="post-content-${postId}">${data.content}</p>
                <button onclick="editPost(${postId})">Edit</button>
            `;
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error("Error:", error));
}

function toggleLike(postId) {
    fetch(`/toggle_like/${postId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        const likeButton = document.querySelector(`#post-${postId} button`);
        const likeCount = document.getElementById(`like-count-${postId}`);

        if (data.action === "liked") {
            likeButton.innerText = "Unlike";
        } else {
            likeButton.innerText = "Like";
        }

        likeCount.innerText = data.total_likes;  // Update like count
    })
    .catch(error => console.error("Error:", error));
}

// Function to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            return value;
        }
    }
    return "";
}

