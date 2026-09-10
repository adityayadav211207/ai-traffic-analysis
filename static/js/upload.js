const dropArea = document.querySelector(".drop-area");
const fileInput = document.getElementById("dataset");
const fileName = document.getElementById("file-name");

// Click Upload
dropArea.addEventListener("click", () => {

    fileInput.click();

});

// File Selected
fileInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        const file = this.files[0];

        fileName.innerHTML = `
            <i class="fa-solid fa-file-csv"></i>
            ${file.name}
        `;

    }

});

// Drag Over
dropArea.addEventListener("dragover", (e) => {

    e.preventDefault();

    dropArea.classList.add("drag-active");

});

// Drag Leave
dropArea.addEventListener("dragleave", () => {

    dropArea.classList.remove("drag-active");

});

// Drop File
dropArea.addEventListener("drop", (e) => {

    e.preventDefault();

    dropArea.classList.remove("drag-active");

    if (e.dataTransfer.files.length > 0) {

        fileInput.files = e.dataTransfer.files;

        const file = e.dataTransfer.files[0];

        fileName.innerHTML = `
            <i class="fa-solid fa-file-csv"></i>
            ${file.name}
        `;

    }

});