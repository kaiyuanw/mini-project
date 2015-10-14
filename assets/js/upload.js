// Get the template HTML and remove it from the doument
var previewNode = document.querySelector("#template");
previewNode.id = "";
var previewTemplate = previewNode.parentNode.innerHTML;
previewNode.parentNode.removeChild(previewNode);

var error_counter = 0;

var myDropzone = new Dropzone(document.body, { // Make the whole body a dropzone
    url: "/upload", // Set the url
    paramName: "photo",
    thumbnailWidth: 80,
    thumbnailHeight: 80,
    parallelUploads: 10,
    previewTemplate: previewTemplate,
    autoQueue: false, // Make sure the files aren't queued until manually added
    previewsContainer: "#previews", // Define the container to display the previews
    clickable: ".fileinput-button" // Define the element that should be used as click trigger to select files.
});

myDropzone.on("addedfile", function (file) {
    // Hookup the start button
    file.previewElement.querySelector(".start").onclick = function () {
        myDropzone.enqueueFile(file);
    };
});

// Update the total progress bar
myDropzone.on("totaluploadprogress", function (progress) {
    document.querySelector("#total-progress .progress-bar").style.width = progress + "%";
});

myDropzone.on("sending", function (file) {
    // Show the total progress bar when upload starts
    document.querySelector("#total-progress").style.opacity = "1";
    // And disable the start button
    file.previewElement.querySelector(".start").setAttribute("disabled", "disabled");
});

// Hide the total progress bar when nothing's uploading anymore
myDropzone.on("queuecomplete", function (progress) {
    document.querySelector("#total-progress").style.opacity = "0";
    window.location.reload()
});

myDropzone.on('error', function (file, errorMessage, xhr) {
    if (error_counter <= 5) {
        file.previewElement.classList.remove("dz-error");
        file.previewElement.querySelector("[data-dz-errormessage]").innerHTML = "";
        myDropzone.uploadFile(file);
        error_counter += 1;
    }
    else {
        file.previewElement.querySelector("[data-dz-errormessage]").innerHTML = "Upload operation fails";
        error_counter = 0;
    }
});

myDropzone.on('success', function (file, response) {
    error_counter = 0;
    //file.previewElement.classList.remove("dz-error");
    return file.previewElement.classList.add("dz-success");
});

// Setup the buttons for all transfers
// The "add files" button doesn't need to be setup because the config
// `clickable` has already been specified.
document.querySelector("#actions .start").onclick = function () {
    myDropzone.enqueueFiles(myDropzone.getFilesWithStatus(Dropzone.ADDED));
};

document.querySelector("#actions .cancel").onclick = function () {
    myDropzone.removeAllFiles(true);
};