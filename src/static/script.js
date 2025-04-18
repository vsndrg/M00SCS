let editor;

window.onload = () => {
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/solarized_light");
    editor.session.setMode("ace/mode/c_cpp");
    editor.session.setTabSize(2);
    editor.session.setUseSoftTabs(true);

    editor.setOptions({
        fontFamily: "Consolas, 'Courier New', monospace",
        fontSize: "14px",
        highlightActiveLine: true,

        showInvisibles: true,
    });

    const toggleCheckButton = () => {
        const button = document.getElementById("checkButton");
        const hotkeyHint = document.getElementById("hotkeyHint");
        if (editor.getValue().trim() !== "") {
            button.style.display = "block";
            hotkeyHint.style.display = "block";
        }
        else {
            button.style.display = "none";
            hotkeyHint.style.display = "none";
        }
    };
    editor.session.on('change', toggleCheckButton);

    editor.commands.addCommand({
        name: "customCheck",
        bindKey: { win: "Ctrl-S", mac: "Cmd-S" },
        exec: uploadCode
    });

    editor.focus();
}

document.getElementById("fileInput").addEventListener("change", (event) => {
    const fileLabel = document.querySelector(".custom-file-upload");
    const fileNameDisplay = document.getElementById("fileName");
    const verificationCodeInput = document.getElementById("verificationCode");
    const copyButton = document.querySelector(".copy-btn");

    if (event.target.files.length > 0) {
        const file = event.target.files[0];

        if (!file) {
            return;
        }
        const fileName = file.name;
        if (!fileName.match(/\.c$/i)) {
            alert("Error: Only files with .c extensions can be uploaded");
            event.target.value = "";
            return;
        }

        fileNameDisplay.textContent = file.name;
        fileLabel.textContent = "Change File";

        setEditorCode(file);
        uploadFile(file);
    } else {
        fileNameDisplay.textContent = "No file chosen";
        fileLabel.textContent = "Choose File";
        verificationCodeInput.textContent = "";

        // Сменить текст кнопки на "Copy"
        copyButton.textContent = "Copy";
        copyButton.disabled = false;
    }
    event.target.value = '';
});

const setEditorCode = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
        const fileContent = e.target.result;
        editor.setValue(fileContent, -1);
    }
    reader.readAsText(file);
}

const uploadCode = () => {
    const code = editor.getValue();
    const programName = document.getElementById("programSelect").value;

    if (programName == "") {
        alert("Choose program!");
        return;
    }

    const blob = new Blob([code], { type: "plain/text" });
    const file = new File([blob], programName + ".c", { type: "plain/text" });

    uploadFile(file);
};

const uploadFile = (file) => {
    const errorBlock = document.getElementById("errorBlock");
    const errorList = document.getElementById("errorList");
    const verificationCode = document.getElementById("verificationCode");
    const programName = document.getElementById("programSelect").value;
    const loader = document.getElementById("loader");
    const resultBlock = document.getElementById("resultBlock");
    const copyButton = document.querySelector(".copy-btn");

    if (programName == "") {
        alert("Choose program!");
        return;
    }

    resultBlock.style.display = "none";

    errorList.value = "";
    errorBlock.style.display = "none";

    loader.style.display = "block";
    
    const formData = new FormData();
    formData.append("file", file);

    fetch("http://192.168.0.10:8080", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server Response:", data);

        if (data.error) {
            loader.style.display = "none";
            errorList.value = data.error;
            errorBlock.style.display = "block";
            verificationCode.textContent = "";
            resultBlock.style.display = "none";
        }
        else {
            loader.style.display = "none";
            errorBlock.style.display = "none";
            errorList.value = "";
            resultBlock.style.display = "flex";
            verificationCode.textContent = data.verificationCode;
        }
    })
    .catch(error => {
        console.error("Error during file upload: ", error);
    });

    // Сменить текст кнопки на "Copy"
    copyButton.textContent = "Copy";
    copyButton.disabled = false;
};

const setVerificationCode = (file) => {
    // Get the file name in lower case for case-insensitivity
    const fileName = file.name.toLowerCase();
    const encoder = new TextEncoder();
    const data = encoder.encode(fileName);
    // Calculate SHA-256 hash using the Web Crypto API
    crypto.subtle.digest("SHA-256", data)
        .then((hashBuffer) => {
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            // Convert the hash to a hexadecimal string
            const hashHex = hashArray
                .map(b => b.toString(16).padStart(2, "0"))
                .join("");
            // Write the resulting hash into the verificationCode element
            document.getElementById("verificationCode").value = hashHex;
        })
        .catch((error) => {
            console.error("Error calculating hash:", error);
        });
};

const copyResult = () => {
    const codeInput = document.getElementById("verificationCode");
    const copyButton = document.querySelector(".copy-btn");

    if (codeInput.value !== "") {
        navigator.clipboard.writeText(codeInput.value).then(() => {
            // Сменить текст кнопки на "Copied"
            copyButton.textContent = "Copied";
            copyButton.disabled = true;
    
            // // Восстановить текст кнопки на "Copy" через 2 секунды
            // setTimeout(() => {
            //     copyButton.textContent = "Copy";
            // }, 2000);
        });
    }
};
