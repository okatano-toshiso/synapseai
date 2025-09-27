let mediaRecorder;
let audioChunks = [];
var isTranslating = false;

document.getElementById("startRecord").onclick = function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.onstop = () => {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                document.getElementById("audioPlayback").src = audioUrl;
                const formData = new FormData();
                formData.append('audioFile', audioBlob, 'user.wav');

                fetch('/callcenter/upload/', { // 正しいエンドポイントに修正
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                    },
                })
                .then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error("アップロード中にエラーが発生しました: ", error));
                // 録音データの配列をクリア
                audioChunks = [];
            };
            mediaRecorder.start();
            document.getElementById("stopRecord").disabled = false;
        })
        .catch(error => {
            console.error("マイクのアクセスに失敗しました: ", error);
        });
};

document.getElementById("stopRecord").onclick = function() {
    mediaRecorder.stop();
    document.getElementById("stopRecord").disabled = true;
};
