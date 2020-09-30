Dropzone.options.myAwesomeDropzone = {
  url: "/api/upload/file",
  autoProcessQueue: false,
  uploadMultiple: false,
  previewsContainer: "#previews",
  parallelUploads: 2,
  maxFiles: 1000,
  maxFilesize: 1024,
  paramName: "files",
  clickable: "#files",
  addRemoveLinks: true,
  init: function () {
    const myDropzone = this
    this.element
      .querySelector("input[name=\"submit\"]")
      .addEventListener("click", function (e) {
        e.preventDefault()
        e.stopPropagation()
        myDropzone.processQueue()
      })
    this.on("sending", function (file, xhr, formData) {
    })
    this.on("success", function (file, response) {
      const errorMessage = file.previewElement.getElementsByClassName("dz-error-message")[0]
      errorMessage.getElementsByTagName("span")[0]
        .innerHTML = `<a href="${response.full_url}">${response.full_url}</a>`
      errorMessage.style.opacity = "1"
      file.previewElement.removeChild(file.previewElement.getElementsByClassName("dz-error-mark")[0])
      myDropzone.processQueue()
    })
    this.on("error", function (file, response) {
      file.previewElement.getElementsByClassName("dz-error-message")[0].style.opacity = "1"
      myDropzone.processQueue()
      file.status = Dropzone.ADDED
      myDropzone.enqueueFile(file)
    })
  }
}


ready(() => {
  const ruleBtns = document.getElementsByClassName("toggle-rules")
  Array.prototype.forEach.call(ruleBtns, el => {
    el.addEventListener("click", () => {
      const overlay = document.getElementById("overlay")
      const rules = document.getElementById("rules-hidden")
      if (isVisible(overlay)) {
        setTimeout(() => fadeToggle(overlay, 500), 500)
        fadeToggle(rules, 500)
      } else {
        setTimeout(() => fadeToggle(rules, 500), 600)
        fadeToggle(overlay, 500)
      }
    })
  })
})