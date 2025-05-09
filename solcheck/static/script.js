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

    const toggleDynamicElements = () => {
        const button = document.getElementById("checkButton");
        const hotkeyHint = document.getElementById("hotkeyHint");
        const task = document.getElementById("programSelector");

        if (editor.getValue().trim() !== "") {
            button.style.display = "block";
            hotkeyHint.style.display = "block";
            task.style.display = "block";
        }
        else {
            button.style.display = "none";
            hotkeyHint.style.display = "none";
        }
    };
    editor.session.on('change', toggleDynamicElements);

    editor.commands.addCommand({
        name: "customCheck",
        bindKey: { win: "Ctrl-S", mac: "Cmd-S" },
        exec: uploadCode
    });

    editor.focus();
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        editor.focus();
    }
    if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'f') {
        event.preventDefault();
        document.getElementById("fileInput").click();
    }
});

document.getElementById("fileInput").addEventListener("change", (event) => {
    const fileLabel = document.querySelector(".custom-file-upload");
    const fileNameDisplay = document.getElementById("fileName");
    const verificationCodeInput = document.getElementById("verificationCode");
    const copyButton = document.querySelector(".copy-btn");
    const programName = document.getElementById("programSelect").value;
    const section = window.location.pathname.split('/')[1];
    let ext;

    if (event.target.files.length > 0) {
        const file = event.target.files[0];

        if (!file) {
            return;
        }
        const fileName = file.name;

        switch (section) {
            case 'c':
                ext = 'C';
                break;
            case 'cpp':
                ext = 'cpp';
                break;
            case 'coq':
                ext = 'v';
                break;
        }

        if (!fileName.match(new RegExp(`\.${ext}$`, 'i'))) {
            alert(`Error: Only files with .${ext} extensions can be uploaded`);
            event.target.value = "";
            return;
        }

        fileNameDisplay.textContent = file.name;
        fileLabel.textContent = "Change File";

        setEditorCode(file);
        setProgramNameAuto(fileName);
        uploadFile(file, section);
    } else {
        fileNameDisplay.textContent = "No file chosen";
        fileLabel.textContent = "Choose File";
        verificationCodeInput.textContent = "";

        copyButton.textContent = "Copy";
        copyButton.disabled = false;
    }
    event.target.value = '';
});

const setProgramNameAuto = (filename) => {
    document.getElementById("programSelect").value = filename.toUpperCase().split('.')[0];
}

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
    const section = window.location.pathname.split('/')[1];
    let ext;

    if (programName == "not_selected") {
        alert("Choose program!");
        return;
    }

    switch (section) {
        case 'c':
            ext = 'C';
            break;
        case 'cpp':
            ext = 'cpp';
            break;
        case 'coq':
            ext = 'v';
            break;
    }

    const blob = new Blob([code], { type: "plain/text" });
    const file = new File([blob], programName + `.${ext}`, { type: "plain/text" });

    uploadFile(file, section);
};

const uploadFile = (file, section) => {
    const errorBlock = document.getElementById("errorBlock");
    const errorList = document.getElementById("errorList");
    const verificationCode = document.getElementById("verificationCode");
    const programName = document.getElementById("programSelect").value;
    const loader = document.getElementById("loader");
    const resultBlock = document.getElementById("resultBlock");
    const copyButton = document.querySelector(".copy-btn");

    if (programName == "not_selected") {
        alert("Choose program!");
        return;
    }

    resultBlock.style.display = "none";

    errorList.value = "";
    errorBlock.style.display = "none";

    loader.style.display = "block";

    const formData = new FormData();
    formData.append("file", file);
    if (programName !== "not_selected")
        formData.append("task", programName);

    formData.append("prefix", section);

    fetch(`https://solcheck.ru/${section}`, {
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

    if (codeInput.textContent !== "") {
        navigator.clipboard.writeText(codeInput.textContent).then(() => {
            copyButton.textContent = "Copied";
            copyButton.disabled = true;

            setTimeout(() => {
                copyButton.textContent = "Copy";
                copyButton.disabled = false;
            }, 2000);
        });
    }
};
