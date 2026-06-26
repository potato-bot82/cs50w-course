document.addEventListener('DOMContentLoaded', function() {
    const textBox = document.getElementById("text-box"); // Ambil elemen input (textarea)
    const chatBox = document.querySelector(".chat-box"); // Ambil elemen chat-box

    textBox.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) { 
            event.preventDefault(); // Mencegah baris baru di textarea
            
            let userMessage = textBox.value.trim(); // Ambil teks yang diketik
            if (userMessage === "") return; // Jangan kirim jika kosong
            
            // Tambahkan pesan pengguna ke chat
            chatBox.innerHTML += `<div class='message user'>${userMessage}</div>`;
            textBox.value = ""; // Kosongkan textarea setelah dikirim
            
            // Kirim pertanyaan ke backend
            fetch(`/chatbot/chat/?question=${encodeURIComponent(userMessage)}`)
                .then(response => response.json())
                .then(data => {
                    // Tambahkan jawaban bot ke dalam chat
                    chatBox.innerHTML += `<div class='message bot'>${data.answer}</div>`;
                    
                    // Scroll otomatis ke bawah agar pesan terbaru terlihat
                    chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch(error => {
                    console.error("Error:", error);
                    chatBox.innerHTML += `<div class='message bot error'>Maaf, terjadi kesalahan.</div>`;
                });
        }
    });
});
