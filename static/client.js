let mediaRecorder;
let audioChunks = [];

document.getElementById("start").onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const output = document.getElementById("output");

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = async e => {
        audioChunks.push(e.data);
        if (mediaRecorder.state === "inactive") {
            const blob = new Blob(audioChunks, { type: "audio/webm" });
            audioChunks = [];

            const formData = new FormData();
            formData.append("audio", blob, "live_audio.webm");

            const response = await fetch("/live", { method: "POST", body: formData });
            const audioBlob = await response.blob();
            const url = URL.createObjectURL(audioBlob);
            output.src = url;
        }
    };
};

document.getElementById("stop").onclick = () => {
    if (mediaRecorder) mediaRecorder.stop();
};
