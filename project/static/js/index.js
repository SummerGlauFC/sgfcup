const getMessage = (file) => file.previewElement.getElementsByClassName("dz-error-message")[0]
const getProgress = (file) => file.previewElement.getElementsByClassName("dz-progress")[0]
const getRemoveAllButton = () => document.getElementById("remove-all-files")
const getPreviewTemplate = () => document.getElementById("dz-preview-template").innerHTML

function showUploadResult(file, response, message) {
  const errorMessage = getMessage(file)
  const progress = getProgress(file)
  errorMessage.innerHTML = message
  fadeIn(errorMessage, 300)
  fadeOut(progress, 300)
}

const previews = document.getElementById("previews")

Dropzone.options.myAwesomeDropzone = {
  url: "/api/upload/file",
  autoProcessQueue: false,
  uploadMultiple: false,
  previewsContainer: previews,
  parallelUploads: 2,
  maxFiles: 1000,
  maxFilesize: 1024,
  paramName: "files",
  clickable: "#files",
  addRemoveLinks: false,
  timeout: 1000 * 60 * 60 * 24,
  previewTemplate: getPreviewTemplate(),
  headers: {
    "X-CSRFToken": window.CSRF_TOKEN
  },
  init: function () {
    const dropzone = this

    dropzone.updated_login_form = false

    this.element
      .querySelector(`input[name="submit"]`)
      .addEventListener("click", function (e) {
        e.preventDefault()
        e.stopPropagation()
        dropzone.processQueue()
      })

    this.on("addedfile", function (file) {
      const removeAllButton = getRemoveAllButton()
      // add remove all files button if it does not already exist
      if (!removeAllButton) {
        const btn = document.createElement("button")
        btn.innerHTML = "Remove all"
        btn.id = "remove-all-files"
        btn.addEventListener("click", () => dropzone.removeAllFiles())
        previews.insertBefore(btn, previews.firstChild)
      }
    })
    this.on("reset", function () {
      // remove button when all files are gone
      const removeAllButton = getRemoveAllButton()
      if (removeAllButton) {
        previews.removeChild(removeAllButton)
      }
    })
    this.on("sending", function (file, xhr, formData) {
      // make sure progress bar is shown again
      fadeIn(getProgress(file), 0)
    })
    this.on("success", function (file, response) {
      // hide the error mark when re-uploading errored files
      file.previewElement.removeChild(file.previewElement.getElementsByClassName("dz-error-mark")[0])

      // update URL for gallery button upon upload
      const gallery = document.getElementById("button-gallery")
      if (gallery && response.key !== "anon") gallery.href = `/gallery/${response.key}`

      showUploadResult(file, response, `<a href="${response.full_url}">${response.full_url}</a>`)
      dropzone.processQueue()
    })
    this.on("error", function (file, response) {
      const isResp = response.hasOwnProperty("error")
      showUploadResult(file, response, `<span>${isResp ? response.error : response}</span>`)
      // only requeue if it's a server error and not a dropzone error
      if (isResp) {
        file.status = Dropzone.ADDED
        dropzone.enqueueFile(file)
      }
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
        setTimeout(() => fadeToggle(overlay, 250), 250)
        fadeToggle(rules, 250)
      } else {
        setTimeout(() => fadeToggle(rules, 250), 250)
        fadeToggle(overlay, 250)
      }
    })
  })
})