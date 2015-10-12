/**
 * Created by Kaiyuan_Wang on 10/11/15.
 */

Dropzone.autoDiscover = true;

var myDropzone = new Dropzone('#myDropzone', {
    paramName: "photo",
    maxFilesize: 5.0,
    maxFile: 10,
    parallelUploads: 10000,
    uploadMultiple: true,
    autoProcessQueue: false
});

$(document).ready(function () {
    console.log("ready");
    $('#btn-upload').on('click', function () {
        myDropzone.processQueue();
        console.log("button pressed");
    });
});

//Dropzone.options.myDropzone = {
//    paramName: "photo",
//    maxFilesize: 5.0,
//    maxFile: 10,
//    parallelUploads: 10000,
//    uploadMultiple: true,
//    autoProcessQueue: true
//};