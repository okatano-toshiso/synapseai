document.getElementById('copyButton').addEventListener('click', function() {
    var copyText = document.querySelector('.copy-target').innerText;
    var textArea = document.createElement('textarea');
    textArea.value = copyText;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
});
